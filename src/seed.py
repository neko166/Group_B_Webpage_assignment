"""
seed.py — ダミーデータ投入スクリプト
実行方法: src/ ディレクトリで `python seed.py`
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# .env を database インポート前にロード（app.db を使うため）
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from datetime import date, datetime
from database import SessionLocal, engine
from models import Base, User, Skill, UserSkill, CareerHistory, Training, Project, Roadmap, ChatSession, ChatMessage

# テーブルが存在しない場合は作成
Base.metadata.create_all(bind=engine)

# Users.password カラムが存在しない場合は追加（マイグレーション）
import sqlite3 as _sqlite3
_db_path = engine.url.database
_con = _sqlite3.connect(_db_path)
_cols = [row[1] for row in _con.execute("PRAGMA table_info(Users)").fetchall()]
if "password" not in _cols:
    _con.execute("ALTER TABLE Users ADD COLUMN password VARCHAR(255)")
    _con.commit()
_con.close()

db = SessionLocal()

def run():
    # 既存データをクリア（再実行時の重複防止）
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.query(Roadmap).delete()
    db.query(UserSkill).delete()
    db.query(CareerHistory).delete()
    db.query(User).delete()
    db.query(Skill).delete()
    db.query(Training).delete()
    db.query(Project).delete()
    db.commit()

    # ──────────────────────────────────────────────
    # Users
    # ──────────────────────────────────────────────
    users = [
        User(
            name="田中 太郎",
            email="taro.tanaka@example.com",
            password="password123",
            current_role="インフラエンジニア",
            target_role="機械学習エンジニア",
        ),
        User(
            name="佐藤 花子",
            email="hanako.sato@example.com",
            password="password123",
            current_role="バックエンドエンジニア",
            target_role="データサイエンティスト",
        ),
        User(
            name="鈴木 一郎",
            email="ichiro.suzuki@example.com",
            password="password123",
            current_role="フロントエンドエンジニア",
            target_role="フルスタックエンジニア",
        ),
    ]
    db.add_all(users)
    db.commit()

    # ──────────────────────────────────────────────
    # Skills（マスタ）
    # ──────────────────────────────────────────────
    skills_data = [
        ("Python",          "バックエンド"),
        ("JavaScript",      "フロントエンド"),
        ("TypeScript",      "フロントエンド"),
        ("React",           "フロントエンド"),
        ("Vue.js",          "フロントエンド"),
        ("FastAPI",         "バックエンド"),
        ("Django",          "バックエンド"),
        ("TensorFlow",      "AI/ML"),
        ("PyTorch",         "AI/ML"),
        ("scikit-learn",    "AI/ML"),
        ("Pandas",          "データ分析"),
        ("NumPy",           "データ分析"),
        ("SQL",             "データベース"),
        ("PostgreSQL",      "データベース"),
        ("Docker",          "インフラ"),
        ("Kubernetes",      "インフラ"),
        ("AWS",             "クラウド"),
        ("GCP",             "クラウド"),
        ("Linux",           "インフラ"),
        ("Git",             "開発ツール"),
        ("Keras",           "AI/ML"),
        ("Terraform",       "インフラ"),
    ]
    skills = [Skill(skill_name=name, category=cat) for name, cat in skills_data]
    db.add_all(skills)
    db.commit()

    # skill_name → Skill オブジェクトのマップ
    skill_map = {s.skill_name: s for s in db.query(Skill).all()}

    # ──────────────────────────────────────────────
    # User_Skills
    # ──────────────────────────────────────────────
    user_skills = [
        # 田中（インフラ → ML）
        UserSkill(user_id=users[0].user_id, skill_id=skill_map["Linux"].skill_id,      skill_level=4),
        UserSkill(user_id=users[0].user_id, skill_id=skill_map["AWS"].skill_id,        skill_level=3),
        UserSkill(user_id=users[0].user_id, skill_id=skill_map["Docker"].skill_id,     skill_level=3),
        UserSkill(user_id=users[0].user_id, skill_id=skill_map["Python"].skill_id,     skill_level=2),
        UserSkill(user_id=users[0].user_id, skill_id=skill_map["SQL"].skill_id,        skill_level=2),
        # 佐藤（バックエンド → DS）
        UserSkill(user_id=users[1].user_id, skill_id=skill_map["Python"].skill_id,     skill_level=4),
        UserSkill(user_id=users[1].user_id, skill_id=skill_map["FastAPI"].skill_id,    skill_level=3),
        UserSkill(user_id=users[1].user_id, skill_id=skill_map["SQL"].skill_id,        skill_level=4),
        UserSkill(user_id=users[1].user_id, skill_id=skill_map["Pandas"].skill_id,     skill_level=2),
        UserSkill(user_id=users[1].user_id, skill_id=skill_map["Docker"].skill_id,     skill_level=2),
        # 鈴木（フロント → フルスタック）
        UserSkill(user_id=users[2].user_id, skill_id=skill_map["JavaScript"].skill_id, skill_level=4),
        UserSkill(user_id=users[2].user_id, skill_id=skill_map["TypeScript"].skill_id, skill_level=3),
        UserSkill(user_id=users[2].user_id, skill_id=skill_map["React"].skill_id,      skill_level=4),
        UserSkill(user_id=users[2].user_id, skill_id=skill_map["Vue.js"].skill_id,     skill_level=2),
        UserSkill(user_id=users[2].user_id, skill_id=skill_map["Git"].skill_id,        skill_level=3),
    ]
    db.add_all(user_skills)
    db.commit()

    # ──────────────────────────────────────────────
    # Career_History
    # ──────────────────────────────────────────────
    careers = [
        # 田中
        CareerHistory(
            user_id=users[0].user_id,
            project_name="社内インフラ基盤刷新プロジェクト",
            role="インフラエンジニア",
            tech_stack="Linux, AWS, Terraform, Docker",
            period_start=date(2020, 4, 1),
            period_end=date(2022, 3, 31),
            description="オンプレミスサーバーをAWSへ移行。EC2・RDS・S3を活用したシステム構築を担当。",
        ),
        CareerHistory(
            user_id=users[0].user_id,
            project_name="MLOpsパイプライン構築",
            role="インフラ兼MLOpsエンジニア",
            tech_stack="Python, Docker, Kubernetes, GCP",
            period_start=date(2022, 4, 1),
            period_end=None,
            description="機械学習モデルのデプロイ基盤をKubernetesで構築。CI/CDパイプライン整備も担当。",
        ),
        # 佐藤
        CareerHistory(
            user_id=users[1].user_id,
            project_name="ECサイトバックエンド開発",
            role="バックエンドエンジニア",
            tech_stack="Python, Django, PostgreSQL, Docker",
            period_start=date(2019, 7, 1),
            period_end=date(2021, 6, 30),
            description="DjangoによるREST API開発。PostgreSQL設計・クエリ最適化を担当。",
        ),
        CareerHistory(
            user_id=users[1].user_id,
            project_name="顧客行動分析基盤構築",
            role="バックエンド／データエンジニア",
            tech_stack="Python, FastAPI, Pandas, SQL, GCP",
            period_start=date(2021, 7, 1),
            period_end=None,
            description="ユーザーログを分析する集計バッチ処理とAPIを開発。BigQueryを活用したデータ基盤を設計。",
        ),
        # 鈴木
        CareerHistory(
            user_id=users[2].user_id,
            project_name="コーポレートサイトリニューアル",
            role="フロントエンドエンジニア",
            tech_stack="JavaScript, Vue.js, HTML/CSS",
            period_start=date(2021, 1, 1),
            period_end=date(2022, 12, 31),
            description="Vue.jsを用いたSPA開発。デザイナーとの協業でUI/UXを実装。",
        ),
        CareerHistory(
            user_id=users[2].user_id,
            project_name="社内管理システムフルリプレイス",
            role="フロントエンド兼バックエンド",
            tech_stack="TypeScript, React, FastAPI, PostgreSQL",
            period_start=date(2023, 1, 1),
            period_end=None,
            description="ReactとFastAPIによるフルスタック開発。認証基盤やダッシュボードUIを設計・実装。",
        ),
    ]
    db.add_all(careers)
    db.commit()

    # ──────────────────────────────────────────────
    # Trainings
    # ──────────────────────────────────────────────
    trainings = [
        Training(
            title="Python機械学習入門",
            description="scikit-learnとPandasを使ったデータ分析・機械学習の基礎を学ぶ研修です。",
            tags="Python,機械学習,scikit-learn,Pandas",
            held_at="2026年4月10日 10:00〜17:00",
            location="東京オフィス 5F 研修室A",
            target="バックエンドエンジニア・インフラエンジニア向け",
        ),
        Training(
            title="AWSクラウド実践研修",
            description="EC2・S3・RDS・Lambdaを用いたクラウドインフラ構築の実践研修。",
            tags="AWS,クラウド,インフラ,Lambda",
            held_at="2026年5月15日 9:00〜18:00",
            location="オンライン（Zoom）",
            target="インフラエンジニア・バックエンドエンジニア向け",
        ),
        Training(
            title="React/TypeScriptフロントエンド開発",
            description="TypeScriptとReactによるコンポーネント設計・状態管理の実践研修。",
            tags="React,TypeScript,フロントエンド",
            held_at="2026年6月20日 10:00〜17:00",
            location="東京オフィス 3F 会議室B",
            target="フロントエンドエンジニア・フルスタック志望者向け",
        ),
        Training(
            title="深層学習とニューラルネットワーク",
            description="TensorFlow/Kerasを使ったディープラーニングモデルの設計・訓練・評価。",
            tags="TensorFlow,Keras,深層学習,AI",
            held_at="2026年7月8日 10:00〜17:00",
            location="オンライン（Teams）",
            target="機械学習エンジニア・データサイエンティスト志望者向け",
        ),
        Training(
            title="Dockerコンテナ実践入門",
            description="Dockerfileの書き方からdocker-composeによるマルチコンテナ構成まで習得する研修。",
            tags="Docker,コンテナ,インフラ,DevOps",
            held_at="2026年8月5日 10:00〜16:00",
            location="東京オフィス 5F 研修室A",
            target="全エンジニア向け",
        ),
    ]
    db.add_all(trainings)
    db.commit()

    # ──────────────────────────────────────────────
    # Projects（案件マスタ）
    # ──────────────────────────────────────────────
    projects = [
        Project(
            project_name="金融系データ基盤構築",
            company="株式会社フィンテックソリューションズ",
            project_overview="BigQueryを活用した大規模データパイプラインの設計・構築",
            required_skills="Python,SQL,GCP,Pandas",
            match_rate=92,
            employ_type="フルリモート",
            project_duration=date(2026, 6, 1),
        ),
        Project(
            project_name="ECサイト機械学習レコメンド機能開発",
            company="株式会社オンラインコマース",
            project_overview="購買データを用いた商品レコメンドエンジンの開発・運用",
            required_skills="Python,TensorFlow,scikit-learn,SQL",
            match_rate=88,
            employ_type="週3リモート",
            project_duration=date(2026, 7, 1),
        ),
        Project(
            project_name="社内向け管理ダッシュボード開発",
            company="株式会社テックビジョン",
            project_overview="ReactとFastAPIによる社内業務管理システムのフルスタック開発",
            required_skills="React,TypeScript,FastAPI,PostgreSQL",
            match_rate=85,
            employ_type="フルリモート",
            project_duration=date(2026, 5, 1),
        ),
        Project(
            project_name="クラウドインフラ移行支援",
            company="株式会社クラウドテック",
            project_overview="オンプレミスシステムのAWSへの移行設計・実装・運用サポート",
            required_skills="AWS,Terraform,Docker,Linux",
            match_rate=90,
            employ_type="一部リモート",
            project_duration=date(2026, 6, 15),
        ),
        Project(
            project_name="自然言語処理モデル開発",
            company="株式会社AIラボ",
            project_overview="社内文書検索システム向けNLPモデルのファインチューニングと評価",
            required_skills="Python,PyTorch,Keras,NumPy",
            match_rate=78,
            employ_type="フルリモート",
            project_duration=date(2026, 8, 1),
        ),
        Project(
            project_name="Kubernetesクラスタ運用・保守",
            company="株式会社インフラサービス",
            project_overview="本番環境KubernetesクラスタのCI/CD整備および監視基盤の強化",
            required_skills="Kubernetes,Docker,GCP,Linux",
            match_rate=82,
            employ_type="週2出社",
            project_duration=date(2026, 5, 15),
        ),
        Project(
            project_name="Vue.jsを使ったポータルサイト開発",
            company="株式会社デジタルメディア",
            project_overview="コンテンツ配信ポータルのフロントエンドリニューアルおよびパフォーマンス改善",
            required_skills="Vue.js,JavaScript,TypeScript,HTML/CSS",
            match_rate=80,
            employ_type="フルリモート",
            project_duration=date(2026, 7, 15),
        ),
        Project(
            project_name="データ可視化ダッシュボード構築",
            company="株式会社アナリティクスプロ",
            project_overview="PandasとBIツールを組み合わせた営業データの可視化・分析基盤整備",
            required_skills="Python,Pandas,SQL,NumPy",
            match_rate=75,
            employ_type="フルリモート",
            project_duration=date(2026, 9, 1),
        ),
    ]
    db.add_all(projects)
    db.commit()

    print("seed complete.")
    print(f"   Users:          {db.query(User).count()}")
    print(f"   Skills:         {db.query(Skill).count()}")
    print(f"   User_Skills:    {db.query(UserSkill).count()}")
    print(f"   Career_History: {db.query(CareerHistory).count()}")
    print(f"   Trainings:      {db.query(Training).count()}")
    print(f"   Projects:       {db.query(Project).count()}")

    db.close()

if __name__ == "__main__":
    run()
