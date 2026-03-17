import json
import os
import re
import traceback
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database import get_db
import models, schemas

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


async def _get_ollama_model(client: httpx.AsyncClient, base_url: str) -> str:
    configured = os.getenv("OLLAMA_MODEL", "qwen2.5")
    try:
        tags = await client.get(f"{base_url}/api/tags")
        tags.raise_for_status()
        model_list = [m["name"] for m in tags.json().get("models", [])]
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollamaに接続できません。Ollamaが起動しているか確認してください。")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollamaモデル一覧の取得に失敗しました: {type(e).__name__}: {e}")
    if not model_list:
        raise HTTPException(status_code=503, detail=f"Ollamaにモデルがありません。`ollama pull {configured}` を実行してください。")
    for m in model_list:
        if m.startswith(configured.split(":")[0]):
            return m
    return model_list[0]


async def _call_ollama(prompt: str) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    async with httpx.AsyncClient(timeout=180) as client:
        model = await _get_ollama_model(client, base_url)
        resp = await client.post(
            f"{base_url}/api/chat",
            json={
                "model":    model,
                "messages": [{"role": "user", "content": prompt}],
                "stream":   False,
                "options":  {"num_predict": 2000},
            },
        )
        if resp.status_code == 404:
            resp = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model":   model,
                    "prompt":  prompt,
                    "stream":  False,
                    "options": {"num_predict": 2000},
                },
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        if not resp.is_success:
            raise HTTPException(
                status_code=503,
                detail=f"Ollama エラー (HTTP {resp.status_code}): {resp.text[:500]}"
            )
        return resp.json()["message"]["content"].strip()


# ══════════════════════════════════════════════
# ロードマップ生成
# ══════════════════════════════════════════════
@router.post("/generate", response_model=schemas.RoadmapResponse)
async def generate_roadmap(
    payload: schemas.RoadmapGenerateRequest,
    db: Session = Depends(get_db),
):
    user_id = payload.user_id

    # ユーザー取得
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    target_role = payload.target_role or user.target_role or "未設定"

    # 目標ロールを更新
    if payload.target_role and payload.target_role != user.target_role:
        user.target_role = payload.target_role
        db.commit()

    # ユーザーのスキル取得
    user_skills = (
        db.query(models.UserSkill)
        .options(joinedload(models.UserSkill.skill))
        .filter(models.UserSkill.user_id == user_id)
        .all()
    )
    skills_text = "\n".join([
        f"- {us.skill.skill_name}（{us.skill.category}）: レベル {us.skill_level}/5"
        for us in user_skills
    ]) or "スキル未登録"

    # 職務経歴取得
    careers = (
        db.query(models.CareerHistory)
        .filter(models.CareerHistory.user_id == user_id)
        .order_by(models.CareerHistory.period_start.desc())
        .all()
    )
    career_text = "\n".join([
        f"- {c.project_name}（{c.role}）: {c.tech_stack} / {c.description}"
        for c in careers
    ]) or "職務経歴未登録"

    # 研修情報取得
    trainings = db.query(models.Training).all()
    training_text = "\n".join([
        f"- {t.title}（対象: {t.target}）: {t.description}"
        for t in trainings
    ]) or "研修情報なし"

    # ── LLM プロンプト構築 ──
    current_role = user.current_role or "エンジニア"
    prompt = f"""JSONのみ出力。説明文・コードブロック不要。

対象者: {current_role} → {target_role} へのキャリア転換を目指すエンジニア
保有スキル: {skills_text}
職務経歴: {career_text}

上記の「{current_role}」が「{target_role}」になるための4段階ロードマップを作成し、以下の仕様でJSONを出力してください。

仕様:
- steps配列に4要素
- step 1: title="{current_role}", status="completed", progress=100, duration="現在", description={current_role}の業務説明(40〜80字)
- step 2: title={current_role}からのステップアップ職種(シニア/リード/スペシャリスト等の実在職種名), status="current", progress=40
- step 3: title={target_role}へ近づく隣接職種(実在職種名), status="upcoming", progress=0
- step 4: title="{target_role}", status="upcoming", progress=0, duration=X〜Xヶ月
- 全stepにskills_to_acquire(3〜5個の具体的スキル名)とdescription(40〜80字)を付与
- overall_progressは20〜30, estimated_total_durationは合計期間
- 禁止: titleに「中間」「ステップ」「ロール名」などの抽象語を使わないこと

JSON:"""

    # ── プレースホルダー検出ヘルパー ──
    _PLACEHOLDER_PATTERNS = [
        "中間ロール名", "ステップ名", "ロール名", "スキル例",
        "このステップで習得する内容", "現在担当している業務内容の説明",
        "目標とするロールの説明", "X〜X", "合計期間",
    ]

    def _is_valid_roadmap(data: dict) -> bool:
        steps = data.get("steps", [])
        if len(steps) < 2:
            return False
        for step in steps:
            text = " ".join([
                str(step.get("title", "")),
                str(step.get("description", "")),
                str(step.get("duration", "")),
            ])
            if any(pat in text for pat in _PLACEHOLDER_PATTERNS):
                print(f"[roadmap] プレースホルダー検出: {text[:120]}")
                return False
        # 最終ステップのtitleが目標ロールと一致するか確認
        last_title = steps[-1].get("title", "")
        if target_role and last_title and target_role not in last_title and last_title not in target_role:
            print(f"[roadmap] target_role不一致: last_step.title='{last_title}' vs target='{target_role}'")
            return False
        return True

    def _extract_json(raw: str) -> dict:
        m = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw)
        if not m:
            m = re.search(r'\{[\s\S]*\}', raw)
        if not m:
            raise ValueError(f"JSONが見つかりません: {raw[:200]}")
        extracted = m.group(1) if m.lastindex else m.group()
        parsed = json.loads(extracted)
        if "steps" not in parsed:
            raise ValueError("'steps'フィールドがありません")
        return parsed

    # ── Ollama API 呼び出し（最大2回: 通常→厳格プロンプト） ──
    strict_prompt = (
        f"JSONのみ出力。\n"
        f"現在ロール={current_role}, 目標ロール={target_role}\n"
        f"保有スキル: {skills_text}\n\n"
        f"4段階キャリアロードマップJSON:\n"
        f"step1={{\"step_number\":1,\"title\":\"{current_role}\",\"status\":\"completed\",\"progress\":100,\"duration\":\"現在\",\"description\":\"...\",\"skills_to_acquire\":[\"...\",\"...\",\"...\"]}}\n"
        f"step2={{\"step_number\":2,\"title\":\"【{current_role}の上位または隣接する実在職種名をここに記入】\",\"status\":\"current\",\"progress\":40,\"duration\":\"X〜Xヶ月\",\"description\":\"...\",\"skills_to_acquire\":[\"...\",\"...\",\"...\"]}}\n"
        f"step3={{\"step_number\":3,\"title\":\"【{target_role}に近い実在職種名をここに記入】\",\"status\":\"upcoming\",\"progress\":0,\"duration\":\"X〜Xヶ月\",\"description\":\"...\",\"skills_to_acquire\":[\"...\",\"...\",\"...\"]}}\n"
        f"step4={{\"step_number\":4,\"title\":\"{target_role}\",\"status\":\"upcoming\",\"progress\":0,\"duration\":\"X〜Xヶ月\",\"description\":\"...\",\"skills_to_acquire\":[\"...\",\"...\",\"...\"]}}\n"
        f"overall_progress=25, estimated_total_duration=\"合計X〜Xヶ月\"\n"
        f"titleの「【...】」部分を実在する具体的な職種名で置き換えてJSONを出力:"
    )
    parsed = None
    last_error = None
    for attempt, use_prompt in enumerate([prompt, strict_prompt], start=1):
        try:
            raw = await _call_ollama(use_prompt)
            candidate = _extract_json(raw)
            if _is_valid_roadmap(candidate):
                parsed = candidate
                break
            else:
                print(f"[roadmap] attempt {attempt}: プレースホルダー検出、リトライします")
                last_error = ValueError("プレースホルダーを含む不正な出力")
        except HTTPException:
            raise
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[roadmap] attempt {attempt} error:\n{tb}")
            last_error = e

    if parsed is None:
        tb = traceback.format_exc()
        print(f"[roadmap] 全試行失敗:\n{tb}")
        raise HTTPException(status_code=500, detail=f"LLM生成エラー: {type(last_error).__name__}: {last_error}")

    content_json = json.dumps(parsed, ensure_ascii=False)

    # ── DB保存 ──
    roadmap = models.Roadmap(
        user_id=user_id,
        target_role=target_role,
        content_json=content_json,
        created_at=datetime.now(timezone.utc),
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    content = schemas.RoadmapContent(**json.loads(content_json))
    return schemas.RoadmapResponse(
        roadmap_id=roadmap.roadmap_id,
        user_id=roadmap.user_id,
        target_role=roadmap.target_role,
        content=content,
        created_at=roadmap.created_at,
    )


# ══════════════════════════════════════════════
# 最新ロードマップ取得
# ══════════════════════════════════════════════
@router.get("/latest/{user_id}", response_model=Optional[schemas.RoadmapResponse])
def get_latest_roadmap(user_id: int, db: Session = Depends(get_db)):
    roadmap = (
        db.query(models.Roadmap)
        .filter(models.Roadmap.user_id == user_id)
        .order_by(models.Roadmap.created_at.desc())
        .first()
    )
    if not roadmap:
        return None

    content = schemas.RoadmapContent(**json.loads(roadmap.content_json))
    return schemas.RoadmapResponse(
        roadmap_id=roadmap.roadmap_id,
        user_id=roadmap.user_id,
        target_role=roadmap.target_role,
        content=content,
        created_at=roadmap.created_at,
    )


# ══════════════════════════════════════════════
# ステップに対するマッチング案件取得
# ══════════════════════════════════════════════
@router.get("/step-projects", response_model=schemas.StepProjectsResponse)
def get_step_projects(
    step_number: int,
    skills: str,  # カンマ区切りスキル文字列
    db: Session = Depends(get_db),
):
    """
    ステップの習得スキルに基づいてマッチング度の高い案件を2件返す
    """
    skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
    all_projects = db.query(models.Project).all()

    def _matches(step_skill: str, proj_skill: str) -> bool:
        """双方向部分一致でスキルを照合（日本語LLM生成スキル対応）"""
        return proj_skill in step_skill or step_skill in proj_skill

    # スキルマッチング計算
    scored = []
    for p in all_projects:
        req = [s.strip().lower() for s in (p.required_skills or "").split(",") if s.strip()]
        if not req:
            match = 0
        else:
            matched = sum(
                1 for proj_s in req
                if any(_matches(step_s, proj_s) for step_s in skill_list)
            )
            match = int(matched / len(req) * 100)
        scored.append((p, match))

    # マッチ度でソートして上位2件
    scored.sort(key=lambda x: x[1], reverse=True)

    return schemas.StepProjectsResponse(
        step_number=step_number,
        projects=[
            schemas.ProjectResponse(
                project_id=p.project_id,
                project_name=p.project_name,
                company=p.company,
                project_overview=p.project_overview,
                required_skills=p.required_skills,
                match_rate=s,
                employ_type=p.employ_type,
                project_duration=str(p.project_duration) if p.project_duration else None,
            )
            for p, s in scored[:2]
        ],
    )


# ══════════════════════════════════════════════
# 案件一覧取得
# ══════════════════════════════════════════════
@router.get("/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()


# ══════════════════════════════════════════════
# 案件詳細取得
# ══════════════════════════════════════════════
@router.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


