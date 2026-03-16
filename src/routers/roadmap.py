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
        resp.raise_for_status()
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
    prompt = f"""あなたはエンジニアのキャリアアドバイザーです。
以下のユーザー情報を元に、「現在のロール」から「目標ロール」に到達するための具体的なキャリアロードマップをJSON形式で生成してください。

【ユーザー情報】
- 現在のロール: {user.current_role or "未設定"}
- 目標ロール: {target_role}
- 氏名: {user.name}

【保有スキル】
{skills_text}

【職務経歴】
{career_text}

【社内研修情報】
{training_text}

【最重要ルール】
- 必ず「現在のロール（{user.current_role or "現在地"}）」から始まり、「目標ロール（{target_role}）」で終わるロードマップを作成すること
- 各ステップは現在ロールから目標ロールへの道筋となる具体的な職種・役割を表すこと
- ステップ1は現在のロールを表し status を "completed" または "current" にすること
- 最後のステップは必ず目標ロール（{target_role}）にすること
- 最後のステップ（目標ロール）の status は必ず "upcoming" にすること（目標はまだ未達成であるため）
- ユーザーの現在スキル・経歴を活かして現実的な段階を設定すること
- すべてのフィールド（title・description・skills_to_acquire）は必ず日本語で記述すること。英語は絶対に使用しないこと

【出力形式】
以下のJSON形式のみで回答してください。説明文や```は不要です。

{{
  "steps": [
    {{
      "step_number": 1,
      "title": "ステップのタイトル（職種名や役割名）",
      "description": "このステップで何をするか、どんな仕事をするか詳しく説明",
      "duration": "3ヶ月",
      "skills_to_acquire": ["スキル1", "スキル2", "スキル3"],
      "status": "completed",
      "progress": 100
    }}
  ],
  "overall_progress": 15,
  "estimated_total_duration": "12ヶ月"
}}

【ルール】
- steps は3〜5件で、現在ロールから目標ロールまでの段階的な道筋を表すこと
- status は "completed"（達成済）/ "current"（現在取り組み中）/ "upcoming"（未着手）のいずれか
- ステップ1（現在ロール）のみ "completed" または "current" にすること
- 最後のステップ（目標ロール）は必ず "upcoming" にすること
- 中間ステップは状況に応じて "completed" / "current" / "upcoming" を設定すること
- progress はそのステップの完了率（0〜100）。"upcoming" のステップは progress を 0 にすること
- overall_progress は全体の進捗率（0〜100）
- skills_to_acquire には社内研修で学べるものを優先的に含めること
- title・description・skills_to_acquire はすべて日本語で記述すること。英語を使わないこと"""

    # ── Ollama API 呼び出し ──
    try:
        raw = await _call_ollama(prompt)
        # JSONブロックを抽出（```json ... ``` も考慮）
        match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw)
        if not match:
            match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            raise ValueError(f"LLMがJSON形式で返しませんでした。応答の先頭: {raw[:300]}")
        extracted = match.group(1) if match.lastindex else match.group()
        parsed = json.loads(extracted)
        # steps が無い場合はフォールバック
        if "steps" not in parsed:
            raise ValueError("LLMレスポンスに'steps'フィールドがありません")
        content_json = json.dumps(parsed, ensure_ascii=False)
    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[roadmap] LLM error:\n{tb}")
        raise HTTPException(status_code=500, detail=f"LLM生成エラー: {type(e).__name__}: {e}")

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

    # スキルマッチング計算
    scored = []
    for p in all_projects:
        req = [s.strip().lower() for s in (p.required_skills or "").split(",") if s.strip()]
        if not req:
            match = 0
        else:
            match = len(set(skill_list) & set(req)) / len(req) * 100
        scored.append((p, int(match)))

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
                project_duration=p.project_duration,
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
