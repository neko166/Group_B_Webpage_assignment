from database import SessionLocal, engine, Base
import models
import json
from datetime import date

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # User
    user = models.User(
        name="山田 太郎",
        email="yamada@example.com",
        current_role="インフラエンジニア",
        target_role="機械学習エンジニア",
    )
    db.add(user)
    db.flush()
    print(f"✅ User追加: user_id={user.user_id}")

    # Skill マスタ
    skill_data = [
        {"skill_name": "Python",     "category": "バックエンド"},
        {"skill_name": "JavaScript", "category": "フロントエンド"},
        {"skill_name": "SQL",        "category": "データベース"},
        {"skill_name": "Docker",     "category": "DevOps"},
        {"skill_name": "AWS",        "category": "インフラ"},
        {"skill_name": "TensorFlow", "category": "AI/ML"},
    ]
    skills = []
    for s in skill_data:
        skill = models.Skill(**s)
        db.add(skill)
        skills.append(skill)
    db.flush()
    print(f"✅ Skill追加: {len(skills)}件")

    # UserSkill
    levels = [4, 3, 3, 2, 3, 2]
    for skill, level in zip(skills, levels):
        db.add(models.UserSkill(
            user_id=user.user_id,
            skill_id=skill.skill_id,
            skill_level=level,
        ))
    db.flush()
    print("✅ UserSkill追加完了")

    # CareerHistory
    db.add(models.CareerHistory(
        user_id=user.user_id,
        project_name="ECサイト開発",
        role="バックエンドエンジニア",
        tech_stack="Python,FastAPI,PostgreSQL",
        period_start=date(2023, 4, 1),
        period_end=date(2024, 3, 31),
        description="ECサイトのAPI設計・開発を担当。",
    ))
    db.add(models.CareerHistory(
        user_id=user.user_id,
        project_name="インフラ移行プロジェクト",
        role="インフラエンジニア",
        tech_stack="AWS,Terraform,Docker",
        period_start=date(2022, 6, 1),
        period_end=date(2023, 3, 31),
        description="オンプレミス環境からAWSへの移行。IaC化を推進。",
    ))
    db.flush()
    print("✅ CareerHistory追加完了")

    # Training
    db.add(models.Training(
        title="AWSアーキテクト研修",
        description="AWSの主要サービスを活用したシステム設計・構築スキルを習得します。",
        tags="AWS,クラウド,インフラ",
        held_at="2026年4月15日〜4月17日",
        location="オンライン",
        target="AWS基礎知識保有者",
    ))
    db.add(models.Training(
        title="機械学習基礎講座",
        description="Python・scikit-learn・TensorFlowを使用した機械学習の基礎から応用を学びます。",
        tags="Python,ML,AI",
        held_at="2026年5月10日〜5月12日",
        location="オンライン",
        target="Python経験者",
    ))
    db.add(models.Training(
        title="設計書作成トレーニング",
        description="要件定義から詳細設計まで、実践的な設計書の書き方を習得します。",
        tags="設計,ドキュメント",
        held_at="2026年4月24日",
        location="東京本社（会場）",
        target="全エンジニア",
    ))
    db.flush()
    print("✅ Training追加完了")

    # Project（案件）
    db.add(models.Project(
        required_skills="Python,FastAPI,PostgreSQL,Docker",
        project_name="AIチャットボット開発",
        company="ABCテクノロジー株式会社",
        project_overview="社内問い合わせ対応を自動化するAIチャットボットの開発。",
        match_rate=85,
        employ_type="リモート併用",
        project_duration=date(2026, 4, 1),
    ))
    db.add(models.Project(
        required_skills="VB.NET,SQLServer,WindowsForms",
        project_name="基幹業務システム改修",
        company="ビジネスソリューション株式会社",
        project_overview="既存の基幹業務システム（VB.NET）の機能追加および保守。",
        match_rate=70,
        employ_type="常駐",
        project_duration=date(2026, 5, 1),
    ))
    db.add(models.Project(
        required_skills="Java,SpringBoot,MySQL",
        project_name="在庫管理システム開発",
        company="ロジスティクスシステム株式会社",
        project_overview="物流企業向け在庫管理システムのバックエンド開発。",
        match_rate=75,
        employ_type="ハイブリッド",
        project_duration=date(2026, 6, 1),
    ))
    db.add(models.Project(
        required_skills="JavaScript,React,TypeScript,HTML,CSS",
        project_name="ECサイトフロントエンド刷新",
        company="ECソリューションズ株式会社",
        project_overview="ECサイトのUI/UX改善およびフロントエンド再構築。",
        match_rate=80,
        employ_type="フルリモート",
        project_duration=date(2026, 7, 1),
    ))
    db.add(models.Project(
        required_skills="AWS,Terraform,Docker,Kubernetes",
        project_name="クラウドインフラ構築",
        company="クラウドシステム株式会社",
        project_overview="AWSを利用したWebシステム基盤の設計・構築。",
        match_rate=78,
        employ_type="リモート併用",
        project_duration=date(2026, 4, 15),
    ))
    db.flush()
    print("✅ Project追加完了")

    # Roadmap
    roadmap_content = {
        "levels": [
            {
                "level": 1,
                "title": "基礎習得フェーズ",
                "duration": "3ヶ月",
                "skills": ["Python", "SQL", "Linux基礎"],
                "description": "プログラミングとデータ操作の基礎を固める",
                "projects": [
                    {"project_name": "社内業務自動化ツール開発", "company": "株式会社A", "match_rate": 65},
                    {"project_name": "データ集計バッチ開発",     "company": "株式会社B", "match_rate": 60},
                ]
            },
            {
                "level": 2,
                "title": "データ分析フェーズ",
                "duration": "3ヶ月",
                "skills": ["pandas", "numpy", "matplotlib", "scikit-learn"],
                "description": "データ分析・可視化・機械学習の基礎を習得する",
                "projects": [
                    {"project_name": "売上予測モデル構築",           "company": "株式会社C", "match_rate": 75},
                    {"project_name": "顧客分析ダッシュボード開発",   "company": "株式会社D", "match_rate": 70},
                ]
            },
            {
                "level": 3,
                "title": "機械学習実践フェーズ",
                "duration": "4ヶ月",
                "skills": ["TensorFlow", "PyTorch", "MLflow", "Docker"],
                "description": "深層学習モデルの構築・学習・評価を実践する",
                "projects": [
                    {"project_name": "画像認識システム開発",       "company": "株式会社E", "match_rate": 85},
                    {"project_name": "自然言語処理APIの構築",       "company": "株式会社F", "match_rate": 80},
                ]
            },
            {
                "level": 4,
                "title": "MLエンジニア実務フェーズ",
                "duration": "2ヶ月",
                "skills": ["Kubernetes", "CI/CD", "AWS/GCP", "LLM活用"],
                "description": "モデルの本番運用・MLOpsを習得し機械学習エンジニアとして独立できる状態を目指す",
                "projects": [
                    {"project_name": "MLパイプライン構築・運用",         "company": "株式会社G", "match_rate": 92},
                    {"project_name": "LLMを用いたチャットボット開発",     "company": "株式会社H", "match_rate": 90},
                ]
            }
        ]
    }
    db.add(models.Roadmap(
        user_id=user.user_id,
        target_role="機械学習エンジニア",
        content_json=json.dumps(roadmap_content, ensure_ascii=False),
    ))
    db.flush()
    print("✅ Roadmap追加完了")

    db.commit()
    print("\n🎉 シード完了！")

except Exception as e:
    db.rollback()
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()