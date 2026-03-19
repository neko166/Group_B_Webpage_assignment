"""
案件(Project)・研修(Training) ダミーデータ投入スクリプト
実行: cd src && python seed_dummy.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from datetime import date
from database import SessionLocal
import models

# ──────────────────────────────────────────────
# 共通業務フロー定義
# ──────────────────────────────────────────────
FLOW_WEB    = "要件定義 → UI/UX設計 → フロントエンド実装 → バックエンドAPI連携 → テスト → リリース → 運用保守"
FLOW_BE     = "要件定義 → DB設計 → API設計 → 実装 → 単体/結合テスト → ステージング確認 → 本番リリース"
FLOW_INFRA  = "現状調査 → アーキテクチャ設計 → 構築・自動化 → 負荷テスト → 移行・切り替え → 運用監視"
FLOW_DATA   = "データ収集設計 → ETL構築 → データ品質確認 → 分析基盤整備 → BIダッシュボード → 定期レポート"
FLOW_ML     = "課題定義 → データ収集/前処理 → モデル開発・評価 → A/Bテスト → 本番デプロイ → モニタリング"
FLOW_MOBILE = "要件定義 → UI設計 → 実装 → API連携 → テスト（実機/エミュレータ） → ストア申請 → 運用"
FLOW_SEC    = "スコープ定義 → 情報収集 → 脆弱性診断 → ペネトレーション → 報告書作成 → 改善提案"

# ──────────────────────────────────────────────
# 案件ダミーデータ 100件
# 項目順: (name, company, overview, required_skills, match_rate, employ_type, duration,
#          preferred_skills, location, reward, team_size, interview_count, work_process, description)
# ──────────────────────────────────────────────
PROJECTS = [
    # --- Web / フロントエンド ---
    ("ReactによるECサイトリニューアル",
     "株式会社ウェブコマース", "React/TypeScriptを用いたECサイトのUI全面刷新",
     "React,TypeScript,CSS Modules,Storybook", 82, "フルリモート", date(2026,6,1),
     "Next.js,GraphQL,jest", "東京（フルリモート）", "60〜80万円/月",
     "フロント3名・バック2名・PL1名", "2回", FLOW_WEB,
     "老舗ECサイトのフロントエンドをReact+TypeScriptで全面刷新するプロジェクトです。Storybookでコンポーネント管理を行い、パフォーマンス最適化（Core Web Vitals改善）も担当いただきます。チームはフルリモートで活動しており、週次でスプリントレビューを実施します。"),

    ("Vue3 管理画面開発",
     "株式会社アドテック", "広告配信管理ダッシュボードのVue3移行と機能追加",
     "Vue3,Pinia,Vite,TypeScript", 78, "週3リモート", date(2026,5,15),
     "Vitest,Playwright,GraphQL", "東京・渋谷", "55〜70万円/月",
     "フロント4名・バック3名", "2回", FLOW_WEB,
     "広告配信プラットフォームの管理画面をVue2からVue3+Composition APIへ移行するプロジェクトです。リアルタイムのキャンペーン効果測定グラフや入稿フォームの再設計も含みます。週3日は渋谷オフィスに出社いただきます。"),

    ("Next.js コーポレートサイト構築",
     "株式会社クリエイティブ", "Next.js App RouterによるSEO対応コーポレートサイト",
     "Next.js,TypeScript,Tailwind CSS", 75, "フルリモート", date(2026,7,1),
     "Contentful,Vercel,Cypress", "東京（フルリモート）", "50〜65万円/月",
     "フロント2名・デザイナー1名", "1回", FLOW_WEB,
     "大手メーカーのコーポレートサイトをNext.js App Routerで新規構築します。CMSはContentfulを使用し、マーケティングチームがノーコードで更新できる仕組みを整えます。SEOスコア90以上を目標とします。"),

    ("Angular金融ポータル開発",
     "株式会社フィンポータル", "Angularベースの資産管理ポータルサイト開発",
     "Angular,RxJS,NgRx,TypeScript", 80, "一部リモート", date(2026,6,15),
     "D3.js,Jest,Cypress", "東京・大手町", "65〜85万円/月",
     "フロント5名・バック4名・QA2名", "2回", FLOW_WEB,
     "個人投資家向け資産管理ポータルのフロントエンド開発です。株価チャート・ポートフォリオ分析・取引履歴閲覧機能をAngular+NgRxで実装します。金融系のため高いセキュリティ基準が求められます。"),

    ("Nuxt3 旅行予約サービス",
     "旅行テック株式会社", "Nuxt3 SSRによる旅行予約フロントエンド開発",
     "Nuxt3,Vue3,TypeScript,GraphQL", 77, "フルリモート", date(2026,8,1),
     "Pinia,Vitest,Playwright", "東京（フルリモート）", "58〜75万円/月",
     "フロント3名・バック2名", "2回", FLOW_WEB,
     "国内旅行予約サービスのフロントエンドをNuxt3 SSRで構築します。ホテル検索・空き状況カレンダー・予約フロー・マイページ機能を担当します。SEOが重要なためSSR最適化に注力します。"),

    # --- バックエンド ---
    ("FastAPI マイクロサービス開発",
     "株式会社クラウドビズ", "決済システムのマイクロサービス化とAPI設計",
     "Python,FastAPI,PostgreSQL,Docker", 85, "フルリモート", date(2026,6,1),
     "Redis,Celery,Kubernetes,pytest", "東京（フルリモート）", "70〜90万円/月",
     "バック4名・インフラ2名・PL1名", "2回", FLOW_BE,
     "モノリシックな決済システムをFastAPIベースのマイクロサービスへ分割するプロジェクトです。各サービス間はREST＋非同期メッセージ（Celery/Redis）で連携します。99.9%以上の可用性が要件です。"),

    ("Spring Boot 基幹システム改修",
     "製造業DX株式会社", "製造ラインの在庫管理システムをSpring Bootで刷新",
     "Java,Spring Boot,MySQL,Maven", 70, "週2リモート", date(2026,5,1),
     "JUnit,MyBatis,AWS", "愛知・名古屋", "60〜75万円/月",
     "バック5名・PL1名・インフラ1名", "3回", FLOW_BE,
     "製造ラインの在庫管理システム（旧VB.NET）をJava/Spring Bootでリプレイスします。原材料の入出庫管理・棚卸し機能・発注アラートを新システムに移行します。名古屋オフィスへ週2回出社が必要です。"),

    ("Go言語APIサーバー開発",
     "株式会社スピードテック", "高トラフィック対応のREST APIをGoで構築",
     "Go,Gin,PostgreSQL,Redis", 88, "フルリモート", date(2026,7,1),
     "gRPC,Docker,Kubernetes,OpenTelemetry", "東京（フルリモート）", "75〜95万円/月",
     "バック4名・SRE1名", "2回", FLOW_BE,
     "月間1億PVのメディアサービスのAPIサーバーをGoで新規構築します。レスポンスタイム50ms以下・99.99%可用性が要件です。OpenTelemetryで可観測性を確保し、Kubernetesで自動スケールします。"),

    ("Django RESTfulシステム",
     "株式会社エデュテック", "学習管理システムのバックエンドAPI開発",
     "Python,Django,DRF,PostgreSQL", 76, "フルリモート", date(2026,6,15),
     "Celery,Redis,AWS,pytest", "東京（フルリモート）", "55〜70万円/月",
     "バック3名・フロント2名", "2回", FLOW_BE,
     "オンライン学習プラットフォームのバックエンドAPIをDjango REST Frameworkで開発します。動画進捗管理・演習採点・受講証明書発行機能を実装します。テストカバレッジ80%以上が必須です。"),

    ("Ruby on Rails ECバックエンド",
     "株式会社コマースラボ", "大規模ECサイトのバックエンド機能拡張",
     "Ruby,Rails,MySQL,Sidekiq", 73, "週3リモート", date(2026,5,15),
     "ElasticSearch,Redis,RSpec", "東京・品川", "58〜72万円/月",
     "バック5名・フロント3名・QA2名", "2回", FLOW_BE,
     "年商100億円規模のECサイトのバックエンド機能拡張です。商品レコメンド・クーポン管理・在庫連携APIの新規実装を担当します。既存RailsコードベースへのElasticSearch導入も含みます。"),

    # --- データ基盤 / ML ---
    ("BigQueryデータウェアハウス構築",
     "株式会社データドリブン", "小売業のBigQuery移行と分析基盤整備",
     "BigQuery,dbt,Python,Airflow", 90, "フルリモート", date(2026,6,1),
     "Looker,Terraform,GCP", "東京（フルリモート）", "75〜95万円/月",
     "データエンジニア3名・アナリスト2名", "2回", FLOW_DATA,
     "全国300店舗の小売チェーンの販売データをBigQueryに集約するDWH構築プロジェクトです。dbtでデータ変換パイプラインを整備し、LookerでKPIダッシュボードを構築します。最終的にリアルタイム在庫最適化に活用します。"),

    ("機械学習レコメンドエンジン",
     "株式会社AIコマース", "ユーザー購買履歴を活用したリアルタイム推薦モデル",
     "Python,scikit-learn,TensorFlow,Spark", 86, "フルリモート", date(2026,7,1),
     "MLflow,Feast,Kafka,AWS", "東京（フルリモート）", "80〜100万円/月",
     "MLエンジニア3名・データエンジニア2名", "2回", FLOW_ML,
     "ECサイトのトップページ・商品詳細ページに表示するリアルタイムレコメンドエンジンの開発です。協調フィルタリング・コンテンツベースの両手法を組み合わせ、A/Bテストで継続改善します。CTR+15%が目標KPIです。"),

    ("自然言語処理チャットボット",
     "株式会社カスタマーAI", "社内問い合わせ対応チャットボットのLLM活用開発",
     "Python,LangChain,OpenAI API,FastAPI", 83, "フルリモート", date(2026,8,1),
     "Qdrant,Slack API,Azure", "東京（フルリモート）", "75〜90万円/月",
     "AIエンジニア2名・バック2名", "2回", FLOW_ML,
     "社内のIT・人事・経費に関する問い合わせをLLMで自動回答するチャットボットの開発です。RAGアーキテクチャで社内ドキュメントを参照し、Slack Botとして提供します。月間問い合わせ件数の60%削減が目標です。"),

    ("Databricks MLパイプライン",
     "株式会社分析ラボ", "DatabricksによるMLOpsパイプライン構築",
     "Python,Databricks,MLflow,Spark", 87, "週2リモート", date(2026,6,15),
     "Delta Lake,Terraform,Azure", "東京・丸の内", "80〜100万円/月",
     "データエンジニア2名・MLエンジニア3名", "2回", FLOW_ML,
     "複数部門のMLモデルを統一的に管理・デプロイするMLOpsプラットフォームをDatabricks上に構築します。実験管理（MLflow）・モデルレジストリ・自動再学習パイプラインを整備します。"),

    ("画像認識システム開発",
     "株式会社ビジョンテック", "製造ラインの外観検査AIモデルの開発と展開",
     "Python,PyTorch,OpenCV,Docker", 84, "一部リモート", date(2026,7,15),
     "TensorRT,ONNX,C++,Kubernetes", "神奈川・横浜", "75〜90万円/月",
     "MLエンジニア3名・インフラ1名・製造SE2名", "3回", FLOW_ML,
     "半導体製造ラインに設置したカメラ映像からAIで不良品を自動検出するシステムの開発です。検出精度99.5%以上・処理速度30ms以下が要件です。TensorRTでエッジデバイスへの最適化も担当します。"),

    # --- インフラ / クラウド ---
    ("AWSマイグレーション支援",
     "株式会社クラウドマイグ", "オンプレミスサーバーのAWS移行設計と実装",
     "AWS,Terraform,Ansible,Linux", 79, "フルリモート", date(2026,5,1),
     "AWS CDK,Python,CloudFormation", "東京（フルリモート）", "65〜85万円/月",
     "インフラ3名・PL1名", "2回", FLOW_INFRA,
     "物理サーバー50台を段階的にAWSへ移行するプロジェクトです。TerraformでIaC化し、ダウンタイムゼロの移行計画を立案・実行します。コスト削減30%以上が目標です。"),

    ("Kubernetes基盤構築",
     "株式会社コンテナプロ", "本番EKSクラスタの設計・構築・運用自動化",
     "Kubernetes,Helm,ArgoCD,Terraform", 91, "フルリモート", date(2026,6,1),
     "Istio,Prometheus,Grafana,AWS", "東京（フルリモート）", "80〜100万円/月",
     "インフラ3名・SRE2名", "2回", FLOW_INFRA,
     "急成長SaaSのインフラをEKSベースのKubernetes基盤へ移行します。マルチAZ構成・自動スケール・GitOps（ArgoCD）による継続的デリバリーを実現します。稼働率99.95%以上が要件です。"),

    ("GCPデータ基盤整備",
     "株式会社クラウドデータ", "Google CloudによるデータレイクとBIダッシュボード構築",
     "GCP,BigQuery,Dataflow,Looker", 85, "フルリモート", date(2026,7,1),
     "Terraform,dbt,Python,Pub/Sub", "東京（フルリモート）", "70〜90万円/月",
     "データエンジニア3名・インフラ1名", "2回", FLOW_DATA,
     "複数サービスのログ・イベントデータをGCSに集約し、Dataflowでリアルタイム処理するデータレイクを構築します。最終的にLookerでマーケティング・プロダクトチームがセルフサービス分析できる環境を整備します。"),

    ("Azureセキュリティ強化",
     "株式会社エンタープライズ", "Azure AD・Defender活用によるゼロトラスト移行支援",
     "Azure,Terraform,PowerShell,Sentinel", 77, "週3リモート", date(2026,5,15),
     "Entra ID,Defender XDR,Python", "東京・新宿", "70〜85万円/月",
     "インフラ2名・セキュリティ2名", "2回", FLOW_INFRA,
     "従業員5000名規模の企業のゼロトラストセキュリティ移行を支援します。Azure ADの条件付きアクセスポリシー設計・Microsoft Sentinelによる脅威検知ルール実装・SIEM運用フロー整備を担当します。"),

    ("CI/CDパイプライン整備",
     "株式会社DevOpsプロ", "GitHub ActionsとArgoCD活用の自動デプロイ基盤構築",
     "GitHub Actions,ArgoCD,Docker,Kubernetes", 82, "フルリモート", date(2026,6,15),
     "Terraform,Helm,SonarQube", "東京（フルリモート）", "65〜80万円/月",
     "DevOps3名・インフラ2名", "2回", FLOW_INFRA,
     "10チームが開発する複数マイクロサービスのCI/CDパイプラインを統一的に整備します。GitHub Actionsでビルド・テスト・イメージ作成、ArgoCDでKubernetesへの自動デプロイを実現します。デプロイ頻度を週1回から毎日に改善します。"),

    # --- モバイル ---
    ("Reactネイティブ健康管理アプリ",
     "株式会社ヘルスデジタル", "iOS/Android対応の健康トラッキングアプリ開発",
     "React Native,TypeScript,Firebase", 76, "フルリモート", date(2026,7,1),
     "HealthKit,Health Connect,Reanimated", "東京（フルリモート）", "60〜75万円/月",
     "モバイル3名・バック2名", "2回", FLOW_MOBILE,
     "歩数・睡眠・食事を記録する健康管理アプリのReact Nativeによる新規開発です。iOS HealthKit・Android Health Connectとの連携、プッシュ通知、ウィジェット実装を担当します。"),

    ("Flutterフィンテックアプリ",
     "株式会社モバイルフィン", "家計管理とクレジットスコア表示のFlutterアプリ",
     "Flutter,Dart,Firebase,REST API", 74, "週3リモート", date(2026,6,1),
     "Riverpod,go_router,Fastlane", "東京・六本木", "58〜72万円/月",
     "モバイル3名・バック2名・デザイナー1名", "2回", FLOW_MOBILE,
     "銀行口座と連携して家計を自動仕分けするFlutterアプリの開発です。Riverpodで状態管理、go_routerでナビゲーション管理を行います。Open Banking API連携とFace ID/Touch ID認証が必要です。"),

    ("iOSネイティブ物流アプリ",
     "株式会社ロジテック", "配送員向けSwiftUIアプリのリニューアル",
     "Swift,SwiftUI,CoreData,MapKit", 71, "一部リモート", date(2026,5,1),
     "Combine,CloudKit,ARKit", "神奈川・川崎", "58〜72万円/月",
     "iOS2名・バック2名", "3回", FLOW_MOBILE,
     "全国2000名の配送スタッフが使うiOSアプリをUIKitからSwiftUIにリニューアルします。地図での配送ルート表示・荷物スキャン・配達完了報告機能を実装します。オフライン動作対応が必須です。"),

    ("AndroidKotlin在庫管理",
     "株式会社リテールDX", "倉庫スタッフ向けAndroidアプリの新規開発",
     "Kotlin,Jetpack Compose,Room,Retrofit", 73, "週2リモート", date(2026,7,15),
     "Hilt,DataStore,WorkManager", "埼玉・さいたま", "55〜68万円/月",
     "Android2名・バック3名", "2回", FLOW_MOBILE,
     "倉庫スタッフがバーコードスキャンで入出庫を管理するAndroidアプリの新規開発です。Jetpack Composeで現代的なUIを実装し、オフライン対応（Room）・バックグラウンド同期（WorkManager）を実現します。"),

    # --- セキュリティ ---
    ("脆弱性診断・ペネトレーションテスト",
     "株式会社セキュアテック", "WebアプリケーションのOWASP基準脆弱性診断",
     "Python,Burp Suite,OWASP ZAP,Nmap", 69, "フルリモート", date(2026,6,1),
     "Metasploit,SQLMap,Linux", "東京（フルリモート）", "70〜90万円/月",
     "セキュリティ3名", "2回", FLOW_SEC,
     "Webアプリ・API・クラウドインフラを対象にOWASP Top10基準で脆弱性診断を実施します。ペネトレーションテスト後は日本語の詳細報告書と改善提案書を納品します。金融・医療系クライアントが中心です。"),

    ("SOCアナリスト支援",
     "株式会社サイバーガード", "SIEMアラート分析とインシデント対応手順整備",
     "Splunk,Elastic SIEM,Python,Linux", 72, "週3リモート", date(2026,5,15),
     "Kusto,Defender,MITRE ATT&CK", "東京・品川", "65〜80万円/月",
     "セキュリティ4名", "2回", FLOW_SEC,
     "エンタープライズ向けSOCのアナリスト支援業務です。SplunkでのSIEMルール作成・アラートトリアージ・インシデント対応手順書整備を担当します。MITRE ATT&CKフレームワークの知識が必要です。"),

    # --- QA / テスト ---
    ("自動テスト基盤構築（E2E）",
     "株式会社クオリティラボ", "PlaywrightによるE2Eテスト自動化とCI統合",
     "Playwright,TypeScript,GitHub Actions", 78, "フルリモート", date(2026,6,15),
     "Allure,k6,Jest", "東京（フルリモート）", "55〜70万円/月",
     "QA3名・DevOps1名", "2回",
     "テスト計画 → シナリオ設計 → E2Eスクリプト実装 → CI組み込み → レポート整備 → 継続メンテ",
     "手動テスト中心だったEC系サービスのE2Eテストを自動化します。Playwrightで主要ユーザーフロー（会員登録・購入・決済）をカバーし、PR毎にCIで自動実行する仕組みを構築します。"),

    ("APIテスト自動化",
     "株式会社テストプロ", "PostmanとPython pytestによるAPIリグレッションテスト整備",
     "Python,pytest,Postman,Docker", 75, "フルリモート", date(2026,7,1),
     "Newman,Allure,GitHub Actions", "東京（フルリモート）", "52〜65万円/月",
     "QA2名・バック1名", "2回",
     "API仕様書確認 → テストケース設計 → pytestスクリプト実装 → CI組み込み → 定期レポート",
     "マイクロサービス構成の約200エンドポイントに対するAPIリグレッションテストを整備します。Postman CollectionをCI上でNewmanで実行し、Allureで可視化するパイプラインを構築します。"),

    # --- データエンジニアリング ---
    ("Airflowデータパイプライン構築",
     "株式会社データフロー", "複数ソースのETL処理をAirflowでオーケストレーション",
     "Python,Airflow,Spark,PostgreSQL", 84, "フルリモート", date(2026,6,1),
     "dbt,AWS MWAA,Delta Lake", "東京（フルリモート）", "70〜88万円/月",
     "データエンジニア3名", "2回", FLOW_DATA,
     "CRM・基幹・ECの3システムのデータをAirflow DAGで日次・時次・リアルタイムに統合するETLパイプラインを構築します。AWS MWAA上で運用し、データ品質チェック（Great Expectations）も実装します。"),

    ("Kafkaリアルタイム分析基盤",
     "株式会社ストリーミングDX", "Kafka + Flink構成のリアルタイムイベント分析基盤",
     "Kafka,Flink,Python,Kubernetes", 89, "フルリモート", date(2026,7,1),
     "Avro,Schema Registry,Grafana", "東京（フルリモート）", "80〜100万円/月",
     "データエンジニア4名・インフラ1名", "2回", FLOW_DATA,
     "秒間10万イベントのユーザー行動ログをKafka+Flinkでリアルタイム集計し、不正検知・リアルタイムレコメンドへ活用する基盤を構築します。Schema Registryでスキーマ管理を行います。"),

    # --- ERP / 業務システム ---
    ("SalesforceカスタマイズとAPI連携",
     "株式会社CRMソリューション", "Salesforce Apexによる業務フロー自動化と外部API連携",
     "Salesforce,Apex,SOQL,REST API", 68, "週2リモート", date(2026,5,1),
     "LWC,Flow Builder,MuleSoft", "東京・新宿", "60〜80万円/月",
     "Salesforceエンジニア3名・コンサル1名", "2回",
     "要件定義 → Apex実装 → LWCコンポーネント開発 → 外部API連携 → UAT → 本番リリース",
     "営業支援システムのSalesforceカスタマイズを担当します。Apexトリガー・Flowによる業務自動化、基幹システムとのMuleSoft連携を実装します。SFA活用率向上が最終目標です。"),

    ("kintoneアプリ開発",
     "株式会社スモールDX", "中小企業向けkintoneカスタマイズと外部連携API開発",
     "kintone,JavaScript,REST API,Node.js", 67, "フルリモート", date(2026,7,1),
     "Garoon,kintone UI Component,React", "東京（フルリモート）", "45〜60万円/月",
     "エンジニア2名・コンサル1名", "1回",
     "要件ヒアリング → kintoneアプリ設計 → JSカスタマイズ → 外部API連携 → 導入支援",
     "中小企業向けのkintoneアプリ開発・カスタマイズを複数案件担当します。JavaScriptによるカスタマイズ、外部SaaSとのREST API連携、Webhookを活用した自動化を実装します。"),

    # --- ブロックチェーン / Web3 ---
    ("Solidityスマートコントラクト開発",
     "株式会社Web3ラボ", "NFTマーケットプレイスのスマートコントラクト実装",
     "Solidity,Hardhat,TypeScript,ethers.js", 72, "フルリモート", date(2026,8,1),
     "OpenZeppelin,Foundry,The Graph", "東京（フルリモート）", "70〜90万円/月",
     "ブロックチェーンエンジニア3名", "2回",
     "設計 → コントラクト実装 → テスト（Hardhat） → 監査対応 → デプロイ → フロント連携",
     "NFTの発行・取引・ロイヤリティ分配を管理するスマートコントラクトをEVM互換チェーン上に実装します。OpenZeppelinの標準規格（ERC-721/1155）を活用し、セキュリティ監査にも対応します。"),

    # --- ゲーム ---
    ("Unityモバイルゲーム開発",
     "株式会社ゲームスタジオ", "スマホ向けカジュアルゲームの新機能実装とパフォーマンス改善",
     "Unity,C#,Firebase,Addressables", 74, "週3リモート", date(2026,6,1),
     "UniRx,UniTask,Shader Graph", "東京・渋谷", "60〜75万円/月",
     "クライアントエンジニア4名・サーバー2名・デザイナー3名", "2回",
     "機能企画 → 設計 → Unity実装 → QA → リリース → A/Bテスト → 改善",
     "DAU50万人のカジュアルゲームの新ゲームモード実装とパフォーマンス最適化を担当します。AddressablesによるAsset管理効率化、描画負荷削減（DrawCall最適化）も対象です。"),

    # --- AI / LLM ---
    ("RAGシステム構築",
     "株式会社ナレッジAI", "社内ドキュメントを活用したRAGシステムの設計と実装",
     "Python,LangChain,Qdrant,FastAPI", 88, "フルリモート", date(2026,6,1),
     "LlamaIndex,OpenAI API,Docker", "東京（フルリモート）", "75〜95万円/月",
     "AIエンジニア3名・バック1名", "2回", FLOW_ML,
     "数万ページの社内ドキュメントをチャンク分割・ベクトル化してQdrantに格納し、LangChainのRAGパイプラインで質問応答するシステムを構築します。回答精度の継続的な評価・改善も担当します。"),

    ("LLMファインチューニング",
     "株式会社AIラボ", "業界特化LLMのファインチューニングと評価パイプライン構築",
     "Python,PyTorch,HuggingFace,PEFT", 86, "フルリモート", date(2026,8,1),
     "vLLM,DeepSpeed,Weights&Biases", "東京（フルリモート）", "85〜110万円/月",
     "MLエンジニア3名・研究者1名", "2回", FLOW_ML,
     "医療・法律向け業界特化LLMをLoRA/QLoRAでファインチューニングするプロジェクトです。訓練データ構築・ハイパーパラメータ最適化・ベンチマーク評価パイプラインの整備を担当します。"),

    ("AIエージェント基盤開発",
     "株式会社エージェントAI", "LLMベースの自律エージェント設計とツール統合",
     "Python,LangGraph,FastAPI,Docker", 90, "フルリモート", date(2026,7,15),
     "MCP,OpenAI API,Redis,Kubernetes", "東京（フルリモート）", "85〜110万円/月",
     "AIエンジニア4名・バック2名", "2回", FLOW_ML,
     "複数ツール（Web検索・コード実行・DB操作）を自律的に使いこなすAIエージェント基盤をLangGraphで開発します。エージェントの状態管理・ループ制御・ヒューマンインザループを実装します。"),

    # --- BI / 分析 ---
    ("Tableau BI基盤構築",
     "株式会社ビジネスBI", "全社KPI可視化のためのTableauダッシュボード整備",
     "Tableau,SQL,Python,PostgreSQL", 76, "週2リモート", date(2026,5,15),
     "Tableau Prep,dbt,Snowflake", "東京・大手町", "60〜78万円/月",
     "BIエンジニア2名・アナリスト2名", "2回", FLOW_DATA,
     "経営・営業・マーケティング・CS部門のKPIをTableauで統合可視化するBI基盤を整備します。データソースはDWH（Snowflake）からTableau Serverで提供します。各部門のセルフサービス分析を実現します。"),

    # --- IoT ---
    ("IoTゲートウェイ開発",
     "株式会社スマートファクト", "工場センサーデータ収集IoTゲートウェイのファームウェア開発",
     "C,Linux,MQTT,Python", 73, "週2リモート", date(2026,6,1),
     "Node-RED,InfluxDB,Modbus", "大阪・吹田", "60〜75万円/月",
     "組み込みエンジニア3名・クラウド1名", "3回", FLOW_INFRA,
     "工場内の温度・振動・電力センサー100点のデータをLinuxゲートウェイで収集し、MQTTでクラウドへ転送するシステムのファームウェア開発です。Modbus/RS-485通信規格の知識が必要です。"),

    # --- サーバーレス ---
    ("サーバーレスアーキテクチャ移行",
     "株式会社ラムダクラウド", "AWS LambdaとAPI Gatewayへのモノリス分解",
     "AWS Lambda,API Gateway,Python,DynamoDB", 81, "フルリモート", date(2026,6,15),
     "Step Functions,SQS,CDK", "東京（フルリモート）", "68〜85万円/月",
     "バック3名・インフラ2名", "2回", FLOW_INFRA,
     "Rails製モノリスアプリの機能をAWS Lambdaのサーバーレス関数に段階的に切り出すプロジェクトです。DynamoDBでのデータモデル設計・Step Functionsによるワークフロー管理も担当します。"),

    # --- ヘルスケア ---
    ("電子カルテシステム機能追加",
     "株式会社メディカルDX", "電子カルテへの予約管理APIと患者ポータルUI追加",
     "Java,Spring Boot,React,PostgreSQL", 72, "週3リモート", date(2026,5,15),
     "HL7 FHIR,OAuth2,JUnit", "東京・文京", "65〜80万円/月",
     "バック3名・フロント2名・SE1名", "3回", FLOW_BE,
     "病院の電子カルテシステムにオンライン予約管理APIと患者向けポータルUIを追加開発します。医療情報標準規格（HL7 FHIR）への対応と個人情報保護法・医療法への準拠が必須です。"),

    ("医療画像AI解析",
     "株式会社メドAI", "胸部X線画像の異常検知AIモデル開発",
     "Python,PyTorch,MONAI,FastAPI", 85, "フルリモート", date(2026,7,1),
     "DICOM,OpenCV,MLflow,Docker", "東京（フルリモート）", "80〜100万円/月",
     "MLエンジニア3名・医師監修1名", "2回", FLOW_ML,
     "胸部X線画像から肺炎・肺がん・気胸などの異常を検知するAIモデルをMONAIフレームワークで開発します。DICOM形式の医療画像処理・クラスアクティベーションマップによる根拠可視化も実装します。"),

    # --- フィンテック ---
    ("決済API開発",
     "株式会社ペイテック", "3Dセキュア対応クレジット決済APIの新規開発",
     "Python,FastAPI,PostgreSQL,Redis", 87, "フルリモート", date(2026,7,1),
     "Stripe,PCI DSS,Celery,Docker", "東京（フルリモート）", "80〜100万円/月",
     "バック4名・セキュリティ1名・PL1名", "2回", FLOW_BE,
     "EC・SaaS向け決済APIをFastAPIで新規開発します。3Dセキュア2.0対応・PCI DSS準拠・不正検知ロジック実装を担当します。毎月100億円以上の決済を処理するシステムになります。"),

    # --- 物流 ---
    ("配送最適化アルゴリズム開発",
     "株式会社ロジAI", "AIを用いた配送ルート最適化エンジンの開発",
     "Python,OR-Tools,FastAPI,PostgreSQL", 82, "フルリモート", date(2026,6,15),
     "Gurobi,Google Maps API,Docker", "東京（フルリモート）", "75〜90万円/月",
     "アルゴリズムエンジニア2名・バック2名", "2回", FLOW_ML,
     "全国5000台の配送車両のルートをOR-Toolsを用いたVRP（Vehicle Routing Problem）ソルバーで最適化するエンジンの開発です。配送距離15%削減・CO2排出量削減が目標KPIです。"),

    # --- HR Tech ---
    ("採用管理SaaS開発",
     "株式会社HRクラウド", "AIスクリーニング付き採用管理プラットフォームのAPI開発",
     "Python,FastAPI,PostgreSQL,OpenAI API", 81, "フルリモート", date(2026,6,1),
     "Celery,Redis,AWS,pytest", "東京（フルリモート）", "70〜88万円/月",
     "バック4名・フロント2名・AI1名", "2回", FLOW_BE,
     "AIによる書類スクリーニング・面接スコアリング機能を持つ採用管理SaaSのAPI開発です。GPT-4を活用した職務経歴書解析、求人票との適合度スコアリング機能を実装します。"),

    # --- マーケティング ---
    ("CRMデータ分析基盤",
     "株式会社マーケDX", "顧客行動データの収集・集計・可視化基盤構築",
     "Python,Spark,BigQuery,Looker", 83, "フルリモート", date(2026,7,1),
     "dbt,Airflow,GA4,Segment", "東京（フルリモート）", "72〜90万円/月",
     "データエンジニア3名・アナリスト2名", "2回", FLOW_DATA,
     "EC・アプリ・実店舗の顧客行動データを統合するCDPを構築し、Lookerでマーケターがセルフサービス分析できる環境を整備します。LTV予測モデルの実装も含みます。"),

    # --- クラウドデータ ---
    ("Snowflakeデータ基盤",
     "株式会社SnowDX", "SnowflakeによるDWH統合と分析クエリ最適化",
     "Snowflake,dbt,Python,Airflow", 86, "フルリモート", date(2026,7,1),
     "Terraform,GitHub Actions,Sigma", "東京（フルリモート）", "75〜95万円/月",
     "データエンジニア3名", "2回", FLOW_DATA,
     "複数データベースからSnowflakeへの移行とdbtによるデータモデリングを担当します。クエリパフォーマンスの最適化（クラスタリング・マテリアライズドビュー）とコスト管理も含みます。"),

    # --- グリーンテック ---
    ("再エネ予測AIシステム",
     "株式会社グリーンAI", "太陽光発電量予測モデルの開発と運用基盤構築",
     "Python,scikit-learn,FastAPI,PostgreSQL", 80, "フルリモート", date(2026,7,15),
     "Prophet,MLflow,AWS,Grafana", "東京（フルリモート）", "70〜88万円/月",
     "MLエンジニア2名・データエンジニア1名", "2回", FLOW_ML,
     "全国500箇所の太陽光発電所の72時間先の発電量を気象データから予測するAIモデルを開発します。予測精度RMSE±5%以内が目標。FastAPIで予測APIとして提供します。"),

    # --- 追加50件（概要版） ---
    ("Node.js WebSocketリアルタイムチャット",
     "株式会社コミュニティラボ", "Node.jsとSocket.IOを用いたチャットシステムのスケール改善",
     "Node.js,Socket.IO,Redis,Docker", 77, "フルリモート", date(2026,6,1),
     "PM2,Nginx,MongoDB", "東京（フルリモート）", "58〜72万円/月",
     "バック3名", "2回", FLOW_BE,
     "月間アクティブユーザー30万人のコミュニティサービスのリアルタイムチャット機能をスケールアウト対応にリアーキテクチャします。Socket.IOのRedisアダプターで複数ノード対応を実現します。"),

    ("PostgreSQLパフォーマンスチューニング",
     "株式会社DBプロ", "大規模PostgreSQLのインデックス最適化とクエリ改善",
     "PostgreSQL,PgBouncer,Linux,Python", 75, "フルリモート", date(2026,5,15),
     "pgBadger,TimescaleDB,AWS RDS", "東京（フルリモート）", "65〜82万円/月",
     "DBエンジニア2名", "2回", FLOW_INFRA,
     "テーブル数500以上・データ件数10億件規模のPostgreSQLのスロークエリ改善とインデックス設計を行います。パーティショニング・バキューム戦略の最適化も担当します。"),

    ("GraphQL APIゲートウェイ構築",
     "株式会社APIファースト", "複数マイクロサービスを束ねるGraphQL APIゲートウェイ開発",
     "GraphQL,Node.js,Apollo,TypeScript", 81, "フルリモート", date(2026,7,1),
     "Federation,DataLoader,Redis", "東京（フルリモート）", "68〜85万円/月",
     "バック3名・フロント2名", "2回", FLOW_BE,
     "15個のマイクロサービスをApollo Federationで束ねるGraphQL APIゲートウェイを構築します。N+1問題のDataLoader解決・認証認可・レート制限・クエリ深度制限を実装します。"),

    ("ElasticsearchFull-text検索基盤",
     "株式会社サーチDX", "ECサイト向けElasticsearch全文検索基盤の構築と最適化",
     "Elasticsearch,Kibana,Python,Docker", 79, "フルリモート", date(2026,6,15),
     "Logstash,OpenSearch,Redis", "東京（フルリモート）", "65〜80万円/月",
     "バック3名・インフラ1名", "2回", FLOW_BE,
     "商品数500万点のECサイトの検索をElasticsearchで高速化します。日本語形態素解析（Kuromoji）・ファセット検索・類義語辞書・検索スコアリング調整を実装します。"),

    ("メール配信基盤リニューアル",
     "株式会社メールマーケ", "大量メール配信システムの耐障害性向上とSPF/DKIM対応",
     "Python,Celery,Redis,AWS SES", 73, "フルリモート", date(2026,5,1),
     "Bounce handling,SNS,SQS", "東京（フルリモート）", "58〜72万円/月",
     "バック3名・インフラ1名", "2回", FLOW_BE,
     "月間5億通のメール配信基盤をリニューアルします。AWS SES+Celery分散キューで耐障害性を向上させ、SPF/DKIM/DMARC設定でメール到達率を改善します。バウンス・苦情の自動処理も実装します。"),

    ("マイクロフロントエンド移行",
     "株式会社モジュラーWeb", "モノリシックSPAをマイクロフロントエンドへ分割移行",
     "React,Module Federation,Webpack,TypeScript", 84, "フルリモート", date(2026,7,1),
     "Single-spa,Nx,Storybook", "東京（フルリモート）", "70〜88万円/月",
     "フロント5名・アーキテクト1名", "2回", FLOW_WEB,
     "10チームが開発する大規模SPAをWebpack Module Federationを使ってマイクロフロントエンドへ分割します。共通コンポーネントライブラリのNx管理・独立デプロイパイプラインの整備を担当します。"),

    ("OpenTelemetry可観測性基盤",
     "株式会社オブザーバビリティ", "OpenTelemetryによる分散トレーシングと可観測性基盤導入",
     "OpenTelemetry,Jaeger,Prometheus,Grafana", 85, "フルリモート", date(2026,6,1),
     "Loki,Tempo,Kubernetes,Python", "東京（フルリモート）", "72〜90万円/月",
     "SRE3名・インフラ2名", "2回", FLOW_INFRA,
     "20個以上のマイクロサービスにOpenTelemetryを導入し、Grafana Stackで分散トレーシング・メトリクス・ログを統合管理する可観測性基盤を構築します。MTTR半減が目標です。"),

    ("Terraform IaC統一化",
     "株式会社IaCコンサル", "マルチアカウントAWS環境のTerraform IaC化と標準化",
     "Terraform,AWS,Python,GitHub Actions", 83, "フルリモート", date(2026,6,15),
     "Terragrunt,Atlantis,AWS CDK", "東京（フルリモート）", "70〜88万円/月",
     "インフラ3名・SRE1名", "2回", FLOW_INFRA,
     "20以上のAWSアカウントを横断するインフラをTerraformでIaC化・標準化します。Atlantisで自動plan/applyを実現し、モジュール化でチーム間の再利用を促進します。"),

    ("SREエラーバジェット管理基盤",
     "株式会社SREプロ", "SLI/SLO/エラーバジェット管理ダッシュボードの構築",
     "Prometheus,Grafana,Python,Kubernetes", 87, "フルリモート", date(2026,7,1),
     "SLO,Alertmanager,PagerDuty", "東京（フルリモート）", "75〜95万円/月",
     "SRE3名", "2回", FLOW_INFRA,
     "プロダクトのSLI（可用性・レイテンシ・エラー率）を定義し、PrometheusでSLOを継続監視するダッシュボードを構築します。エラーバジェット消費速度のアラートとエスカレーションフローも整備します。"),

    ("Stripeサブスクリプション課金",
     "株式会社SaaSスタート", "StripeによるSaaS課金・プラン管理APIの実装",
     "Node.js,TypeScript,Stripe,PostgreSQL", 79, "フルリモート", date(2026,6,1),
     "Webhook,Prisma,NestJS", "東京（フルリモート）", "65〜80万円/月",
     "バック3名・フロント1名", "2回", FLOW_BE,
     "BtoB SaaSのサブスクリプション課金をStripeで実装します。フリー/スタンダード/エンタープライズの3プラン管理・使用量課金・請求書発行・Webhookによるサブスクライフサイクル管理を担当します。"),

    ("Auth0認証基盤導入",
     "株式会社アイデンティティ", "Auth0を用いたOIDC/SSOシングルサインオン基盤の導入",
     "Auth0,Node.js,TypeScript,React", 76, "フルリモート", date(2026,5,15),
     "SAML,JWT,MFA,Terraform", "東京（フルリモート）", "62〜78万円/月",
     "バック2名・インフラ1名", "2回", FLOW_BE,
     "複数SaaSサービスのSSOをAuth0で統一するIDaaS導入プロジェクトです。SAML/OIDC連携・MFA設定・カスタムドメイン・ブランディング・ロールベースアクセス制御を実装します。"),

    ("GISマッピングシステム開発",
     "株式会社マップDX", "地図データ可視化と経路分析GISシステムの開発",
     "Python,GeoPandas,PostGIS,React", 77, "フルリモート", date(2026,7,15),
     "Mapbox,Deck.gl,Airflow", "東京（フルリモート）", "65〜82万円/月",
     "バック2名・フロント2名・GISエンジニア1名", "2回", FLOW_DATA,
     "不動産・物流向けのGISマッピングシステムを開発します。PostGISでの空間データ管理・GeoPandasでの分析・Mapbox GL JSによる高性能地図可視化・等時圏分析APIを実装します。"),

    ("低遅延動画ストリーミング基盤",
     "株式会社メディアストリーム", "WebRTCとHLSを活用した低遅延ライブ配信基盤の構築",
     "WebRTC,FFmpeg,Node.js,AWS CloudFront", 82, "フルリモート", date(2026,6,15),
     "MediaLive,RTMP,Nginx,Redis", "東京（フルリモート）", "72〜90万円/月",
     "インフラ2名・バック3名", "2回", FLOW_INFRA,
     "スポーツ配信・ライブコマース向けの低遅延（3秒以下）ライブ配信基盤を構築します。WebRTCによる超低遅延・HLSによる大規模配信の両立設計・AWS MediaLiveとの連携を担当します。"),

    ("音声認識AIシステム",
     "株式会社ボイスAI", "コールセンター向け音声認識・議事録自動生成システム開発",
     "Python,Whisper,FastAPI,PostgreSQL", 84, "フルリモート", date(2026,7,1),
     "pyannote,Speaker Diarization,AWS", "東京（フルリモート）", "75〜92万円/月",
     "AIエンジニア2名・バック2名", "2回", FLOW_ML,
     "コールセンターの通話音声をリアルタイムで文字起こし・話者分離・要約するAIシステムをWhisper+pyannoteで開発します。オペレーターの応対品質スコアリング機能も実装します。"),

    ("プロダクトアナリティクス基盤",
     "株式会社プロダクトDX", "Mixpanel/Amplitude連携のユーザー行動分析基盤構築",
     "Python,Mixpanel,BigQuery,dbt", 80, "フルリモート", date(2026,6,1),
     "Segment,Amplitude,Looker", "東京（フルリモート）", "65〜82万円/月",
     "データエンジニア2名・アナリスト1名", "2回", FLOW_DATA,
     "プロダクトのユーザー行動イベントをSegmentで収集してMixpanel・BigQueryに連携するアナリティクス基盤を構築します。ファネル分析・コホート分析・リテンション改善のためのダッシュボードを整備します。"),

    ("ESGデータ管理システム",
     "株式会社サステナDX", "ESG指標収集・集計・レポート自動生成システムの開発",
     "Python,FastAPI,PostgreSQL,React", 76, "フルリモート", date(2026,6,15),
     "Celery,openpyxl,Docker,AWS", "東京（フルリモート）", "62〜78万円/月",
     "バック3名・フロント2名", "2回", FLOW_BE,
     "グローバル企業のCO2排出量・エネルギー消費・人権リスクなどのESG指標を各拠点から収集・集計し、GRI/TCFD準拠のレポートを自動生成するシステムを開発します。"),

    ("PWA開発",
     "株式会社プログレッシブWeb", "オフライン対応の注文管理PWAアプリ開発",
     "React,TypeScript,Service Worker,IndexedDB", 77, "フルリモート", date(2026,6,1),
     "Workbox,Push API,Web Share API", "東京（フルリモート）", "58〜72万円/月",
     "フロント3名・バック1名", "2回", FLOW_WEB,
     "飲食店向けの注文管理PWAアプリを開発します。オフライン時もIndexedDBで注文を蓄積しService Workerで自動同期、プッシュ通知で新規注文を通知する機能を実装します。"),

    ("マルチテナントSaaS基盤",
     "株式会社SaaSアーキ", "テナント分離・課金・RBAC対応マルチテナントSaaSの設計実装",
     "Python,FastAPI,PostgreSQL,Kubernetes", 88, "フルリモート", date(2026,7,1),
     "Stripe,Auth0,Redis,Terraform", "東京（フルリモート）", "80〜100万円/月",
     "バック4名・インフラ2名・アーキテクト1名", "2回", FLOW_BE,
     "複数企業が使うBtoB SaaSのマルチテナント基盤を設計・実装します。Row Level Securityでテナントデータを分離し、ロールベースアクセス制御・Stripeサブスクリプション課金・使用量メータリングを実装します。"),

    ("データカタログ構築",
     "株式会社データガバナンス", "Atlan/OpenMetadataによるデータカタログ導入と整備",
     "Python,OpenMetadata,PostgreSQL,Airflow", 82, "フルリモート", date(2026,6,1),
     "dbt,Lineage,Elasticsearch", "東京（フルリモート）", "68〜85万円/月",
     "データエンジニア2名・データスチュワード1名", "2回", FLOW_DATA,
     "データ民主化推進のためOpenMetadataによるデータカタログを導入します。テーブル定義・データ品質・所有者・利用状況・データリネージを一元管理し、データサイエンティストのデータ探索コストを削減します。"),

    ("フィーチャーストア構築",
     "株式会社MLOpsプロ", "Feastフィーチャーストアの導入とML基盤への統合",
     "Python,Feast,Redis,PostgreSQL", 83, "フルリモート", date(2026,7,1),
     "MLflow,Kubernetes,BigQuery", "東京（フルリモート）", "75〜92万円/月",
     "MLエンジニア3名・データエンジニア1名", "2回", FLOW_ML,
     "複数MLモデル間で特徴量を共有・再利用するフィーチャーストアをFeastで構築します。オンライン（Redis）・オフライン（BigQuery）ストアの整備、特徴量バージョン管理、トレーニング/推論の一貫性確保を担当します。"),

    ("ドキュメント自動生成ツール",
     "株式会社テックライト", "OpenAI APIを活用したAPI仕様書・設計書の自動生成ツール開発",
     "Python,FastAPI,OpenAI API,Jinja2", 79, "フルリモート", date(2026,6,15),
     "Pandoc,Markdown,GitHub Actions", "東京（フルリモート）", "60〜75万円/月",
     "バック2名・フロント1名", "2回", FLOW_BE,
     "コードとOpenAPI仕様書からGPT-4を活用して日本語の設計書・要件定義書・テスト仕様書を自動生成するツールを開発します。エンジニアのドキュメント作成コストを70%削減することが目標です。"),

    ("クロスプラットフォームデスクトップアプリ",
     "株式会社デスクトップDX", "ElectronによるWindowsおよびmacOS向け業務ツール開発",
     "Electron,React,TypeScript,SQLite", 74, "フルリモート", date(2026,6,1),
     "electron-builder,SQLCipher,IPC", "東京（フルリモート）", "58〜72万円/月",
     "フロント2名・バック1名", "2回", FLOW_WEB,
     "建設現場の施工管理者が使うWindows/macOS向けデスクトップ業務ツールをElectronで開発します。オフライン動作・暗号化SQLiteでのデータ管理・PDF帳票出力機能を実装します。"),

    ("ノーコード連携プラットフォーム",
     "株式会社ノーコードDX", "Make/Zapierと社内システムのノーコード連携基盤開発",
     "Node.js,REST API,PostgreSQL,Docker", 71, "フルリモート", date(2026,6,1),
     "Webhook,OAuth2,OpenAPI", "東京（フルリモート）", "55〜70万円/月",
     "バック2名・インテグレーション1名", "2回", FLOW_BE,
     "Make（旧Integromat）・Zapier・n8nと社内基幹システムを繋ぐカスタムコネクターを開発します。OAuth2認証・Webhook受信・OpenAPI仕様公開・レート制限処理を実装します。"),

    ("リアルタイム協調編集ツール開発",
     "株式会社コラボDX", "OperationalTransformation/CRDTを用いたリアルタイム共同編集",
     "Node.js,WebSocket,TypeScript,Redis", 80, "フルリモート", date(2026,7,1),
     "Yjs,CRDT,Liveblocks,React", "東京（フルリモート）", "70〜88万円/月",
     "バック3名・フロント2名", "2回", FLOW_BE,
     "Google Docs風のリアルタイム協調編集機能をYjs（CRDT）+WebSocketで実装します。複数ユーザーの同時編集・カーソル表示・変更履歴・コメント機能を担当します。"),

    ("Notionライク社内ナレッジ基盤",
     "株式会社ナレッジDX", "ブロックエディタ型の社内Wiki・ドキュメント管理システム開発",
     "React,TypeScript,Node.js,PostgreSQL", 78, "フルリモート", date(2026,6,15),
     "BlockNote,Slate.js,Full-text search", "東京（フルリモート）", "65〜80万円/月",
     "フロント3名・バック2名", "2回", FLOW_WEB,
     "Notionライクなブロックエディタ型の社内ナレッジ管理システムを開発します。ドラッグ&ドロップのブロック編集・全文検索・アクセス権限管理・Slack通知連携を実装します。"),

    ("音楽ストリーミングバックエンド",
     "株式会社ミュージックテック", "楽曲配信・プレイリスト・レコメンドAPIのバックエンド開発",
     "Go,PostgreSQL,Redis,AWS S3", 76, "フルリモート", date(2026,7,15),
     "Elasticsearch,CloudFront,gRPC", "東京（フルリモート）", "68〜85万円/月",
     "バック4名・インフラ1名", "2回", FLOW_BE,
     "月間ユーザー100万人の音楽ストリーミングサービスのバックエンドAPIをGoで開発します。楽曲メタデータ管理・プレイリストCRUD・協調フィルタリングレコメンドAPI・ストリーミングURL発行を実装します。"),
]


# ──────────────────────────────────────────────
# 研修ダミーデータ 100件（変更なし）
# ──────────────────────────────────────────────
TRAININGS = [
    ("Python基礎講座", "Pythonの文法・データ構造・ファイル操作を実践的に学ぶ入門コース", "Python,プログラミング基礎", "2026-06-10 10:00〜17:00", "オンライン（Zoom）", "IT未経験者・文系新卒"),
    ("Javaオブジェクト指向入門", "クラス設計・継承・インターフェースをハンズオンで学ぶJava基礎研修", "Java,OOP", "2026-06-17 10:00〜17:00", "オンライン（Zoom）", "新卒エンジニア"),
    ("JavaScript基礎＆ES2023", "変数・関数・非同期処理(async/await)まで最新JSを体系的に学ぶ", "JavaScript,フロントエンド", "2026-06-24 10:00〜17:00", "オンライン（Zoom）", "フロントエンド志望者"),
    ("TypeScript実践入門", "型システム・ジェネリクス・decoratorを使いこなすTS実践コース", "TypeScript,JavaScript", "2026-07-01 10:00〜17:00", "オンライン（Zoom）", "JavaScript経験者"),
    ("Go言語基礎", "Goの並行処理・エラーハンドリング・テストを学ぶ入門研修", "Go,バックエンド", "2026-07-08 10:00〜17:00", "オンライン（Zoom）", "バックエンドエンジニア"),
    ("React実践ワークショップ", "Hooks・状態管理・パフォーマンス最適化を実際のアプリ開発で学ぶ", "React,TypeScript,フロントエンド", "2026-06-14 10:00〜18:00", "渋谷オフィス", "フロントエンドエンジニア"),
    ("Vue3コンポジションAPI研修", "Options APIからComposition APIへの移行と実践的なコンポーネント設計", "Vue3,TypeScript", "2026-06-21 10:00〜18:00", "渋谷オフィス", "Vue.js経験者"),
    ("FastAPI実践開発研修", "FastAPIによるREST API設計・認証・テスト・Dockerデプロイまで学ぶ", "Python,FastAPI,Docker", "2026-07-05 10:00〜18:00", "渋谷オフィス", "Pythonエンジニア"),
    ("Django REST Framework入門", "DjangでのモデルAPI設計・認証・ページネーションを体系的に学ぶ", "Python,Django,バックエンド", "2026-07-12 10:00〜17:00", "オンライン（Zoom）", "Pythonバックエンド志望"),
    ("Spring Boot 実践開発", "Spring BootによるRESTful API・セキュリティ・テスト設計の実践研修", "Java,Spring Boot,バックエンド", "2026-07-19 10:00〜18:00", "渋谷オフィス", "Javaエンジニア"),
    ("SQL基礎〜応用ワークショップ", "SELECT/JOIN/サブクエリ・ウィンドウ関数・インデックス設計まで学ぶ", "SQL,PostgreSQL,データベース", "2026-06-11 10:00〜17:00", "オンライン（Zoom）", "開発者全般"),
    ("PostgreSQL チューニング研修", "EXPLAIN ANALYZE・パーティショニング・バキューム設定の実践チューニング", "PostgreSQL,SQL,インフラ", "2026-06-25 10:00〜17:00", "オンライン（Zoom）", "中級以上エンジニア"),
    ("MongoDB入門", "ドキュメント指向DBの設計・集計パイプライン・インデックス最適化", "MongoDB,NoSQL", "2026-07-09 10:00〜17:00", "オンライン（Zoom）", "バックエンドエンジニア"),
    ("Redis実践活用講座", "キャッシュ戦略・Pub/Sub・Redis Stackの新機能を実務目線で学ぶ", "Redis,バックエンド,インフラ", "2026-07-16 10:00〜17:00", "オンライン（Zoom）", "バックエンドエンジニア"),
    ("AWS基礎認定対策講座", "EC2・S3・VPC・IAMをハンズオンで学ぶAWS CLF/SAA対策研修", "AWS,クラウド,インフラ", "2026-06-13 10:00〜18:00", "渋谷オフィス", "クラウド入門者"),
    ("AWS 上級アーキテクチャ研修", "Well-Architected Framework準拠のマルチアカウント設計を学ぶ", "AWS,Terraform,アーキテクチャ", "2026-07-04 10:00〜18:00", "渋谷オフィス", "AWSエンジニア（中級以上）"),
    ("Google Cloud 入門", "GCE・GCS・BigQuery・Cloud Runを体験するGCP入門ハンズオン", "GCP,クラウド,BigQuery", "2026-06-18 10:00〜17:00", "オンライン（Zoom）", "クラウド入門者"),
    ("Azure fundamentals研修", "Azure AD・VNet・App Service・AKSを実際に触れるAzure入門研修", "Azure,クラウド,インフラ", "2026-07-02 10:00〜17:00", "オンライン（Zoom）", "クラウド入門者"),
    ("マルチクラウド設計ワークショップ", "AWS/GCP/Azureの強み比較と適材適所のアーキテクチャ選択を学ぶ", "AWS,GCP,Azure,アーキテクチャ", "2026-07-23 10:00〜17:00", "渋谷オフィス", "クラウドエンジニア（中級）"),
    ("Docker基礎研修", "Dockerfileの書き方・マルチステージビルド・compose活用を学ぶ", "Docker,DevOps,インフラ", "2026-06-15 10:00〜17:00", "オンライン（Zoom）", "開発者全般"),
    ("Kubernetes実践入門", "Pod/Service/Ingress/HPA・Helmチャート活用まで段階的に学ぶ", "Kubernetes,Docker,DevOps", "2026-06-29 10:00〜18:00", "渋谷オフィス", "Dockerユーザー"),
    ("GitHub Actions CI/CD実践", "ブランチ戦略・テスト自動化・コンテナ自動デプロイまでのCI/CDパイプライン構築", "GitHub Actions,CI/CD,DevOps", "2026-07-06 10:00〜17:00", "オンライン（Zoom）", "開発者全般"),
    ("ArgoCD GitOps研修", "ArgoCDによるGitOpsワークフローとKubernetes継続的デリバリーの実践", "ArgoCD,Kubernetes,GitOps", "2026-07-13 10:00〜17:00", "オンライン（Zoom）", "Kubernetesユーザー"),
    ("Terraform IaC入門", "HCL文法・モジュール設計・state管理・CIとの連携を学ぶ", "Terraform,IaC,AWS", "2026-07-20 10:00〜17:00", "オンライン（Zoom）", "インフラエンジニア"),
    ("データ分析Python入門", "pandas・matplotlib・seabornを使った実データ探索的分析ハンズオン", "Python,pandas,データ分析", "2026-06-12 10:00〜17:00", "オンライン（Zoom）", "データ分析入門者"),
    ("機械学習基礎研修", "線形回帰・決定木・ランダムフォレスト・モデル評価をscikit-learnで学ぶ", "Python,scikit-learn,機械学習", "2026-06-26 10:00〜17:00", "オンライン（Zoom）", "データサイエンス志望"),
    ("ディープラーニング実践", "PyTorchによるCNN/RNNモデル構築・転移学習・ONNX変換を実践", "Python,PyTorch,ディープラーニング", "2026-07-10 10:00〜18:00", "渋谷オフィス", "機械学習エンジニア"),
    ("LLM活用開発研修", "OpenAI API・LangChain・RAGパターンを使った実アプリ開発", "Python,LangChain,LLM,OpenAI API", "2026-07-17 10:00〜18:00", "渋谷オフィス", "開発者全般"),
    ("MLOps実践ワークショップ", "MLflowとGitHub Actionsで学ぶモデルのバージョン管理・デプロイ・監視", "Python,MLflow,Kubernetes,DevOps", "2026-07-24 10:00〜18:00", "渋谷オフィス", "機械学習エンジニア"),
    ("BigQueryデータエンジニアリング", "BigQueryのスキーマ設計・dbt変換・スケジュールクエリ・コスト最適化", "BigQuery,dbt,SQL,GCP", "2026-07-31 10:00〜17:00", "オンライン（Zoom）", "データエンジニア"),
    ("情報セキュリティ基礎研修", "OWASP Top10・SQLインジェクション・XSS対策を演習形式で学ぶ", "セキュリティ,OWASP,Web", "2026-06-16 10:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
    ("クラウドセキュリティ実践", "AWS SecurityHub・GuardDuty・Configを使ったクラウド防御設計", "AWS,セキュリティ,クラウド", "2026-07-07 10:00〜17:00", "オンライン（Zoom）", "AWSエンジニア"),
    ("ペネトレーションテスト入門", "Kali Linux・Burp Suite・Nmap・Metasploitの基礎と倫理的ハッキング入門", "セキュリティ,Burp Suite,Linux", "2026-07-21 10:00〜17:00", "渋谷オフィス", "セキュリティ志望"),
    ("ゼロトラストアーキテクチャ設計", "ゼロトラスト原則に基づいたID管理・マイクロセグメンテーション設計", "セキュリティ,Azure AD,アーキテクチャ", "2026-08-04 10:00〜17:00", "オンライン（Zoom）", "インフラ・クラウドエンジニア"),
    ("React Native入門", "Expo環境でのコンポーネント設計・ナビゲーション・Firebase連携を学ぶ", "React Native,JavaScript,モバイル", "2026-06-20 10:00〜17:00", "オンライン（Zoom）", "React経験者"),
    ("Flutter実践ワークショップ", "Riverpodによる状態管理・アニメーション・Platform Channelを実践", "Flutter,Dart,モバイル", "2026-07-04 10:00〜18:00", "渋谷オフィス", "モバイル開発者"),
    ("Swift/SwiftUI入門", "SwiftUIのレイアウト・Combineフレームワーク・CoreDataを学ぶ", "Swift,SwiftUI,iOS", "2026-07-11 10:00〜17:00", "渋谷オフィス", "iOS開発志望"),
    ("Kotlin/Jetpack Compose実践", "Compose UIコンポーネント設計・Room・Retrofitを組み合わせた実践アプリ開発", "Kotlin,Jetpack Compose,Android", "2026-07-18 10:00〜17:00", "渋谷オフィス", "Android開発者"),
    ("クリーンアーキテクチャ実践", "依存性の逆転・ユースケース分離・テスト戦略をPythonコードで学ぶ", "アーキテクチャ,Python,設計", "2026-06-23 10:00〜17:00", "オンライン（Zoom）", "中級以上エンジニア"),
    ("ドメイン駆動設計(DDD)入門", "ドメインモデル・集約・リポジトリパターンを実例で学ぶDDD研修", "DDD,アーキテクチャ,設計", "2026-07-07 10:00〜17:00", "渋谷オフィス", "バックエンドエンジニア"),
    ("マイクロサービス設計パターン", "サービスメッシュ・サーキットブレーカー・イベントソーシングを学ぶ", "マイクロサービス,Kubernetes,設計", "2026-07-14 10:00〜17:00", "オンライン（Zoom）", "バックエンド・インフラ"),
    ("APIファーストデザイン研修", "OpenAPI仕様書作成・モック開発・バージョニング戦略の実践", "REST API,OpenAPI,設計", "2026-07-28 10:00〜17:00", "オンライン（Zoom）", "開発者全般"),
    ("TDD実践ワークショップ", "テスト駆動開発のサイクルをPythonとpytestで体験する半日研修", "TDD,Python,pytest,テスト", "2026-06-27 13:00〜17:00", "オンライン（Zoom）", "開発者全般"),
    ("自動テスト設計研修", "単体・結合・E2Eの各テスト層の設計指針とツール選定を学ぶ", "テスト,Playwright,pytest", "2026-07-11 10:00〜17:00", "渋谷オフィス", "開発者・QAエンジニア"),
    ("パフォーマンステスト実践", "Locustによる負荷テスト設計・ボトルネック分析・改善サイクルを学ぶ", "Python,Locust,パフォーマンス,テスト", "2026-07-25 10:00〜17:00", "オンライン（Zoom）", "バックエンドエンジニア"),
    ("エンジニアのためのドキュメント術", "技術仕様書・ADR・README・ポストモーテムの書き方をワークで学ぶ", "ドキュメント,コミュニケーション", "2026-06-19 13:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
    ("アジャイル開発実践研修", "スクラムイベント・バックログリファインメント・ベロシティ管理の実践", "アジャイル,スクラム,プロジェクト管理", "2026-07-03 10:00〜17:00", "渋谷オフィス", "全エンジニア"),
    ("技術的負債管理ワークショップ", "負債の可視化・リファクタリング計画・ステークホルダー説明の実践", "リファクタリング,アーキテクチャ,PM", "2026-07-17 13:00〜17:00", "オンライン（Zoom）", "テックリード・シニア"),
    ("GraphQL設計と実装", "スキーマファースト設計・DataLoader・認可パターンをNodeで実践", "GraphQL,Node.js,API", "2026-06-30 10:00〜17:00", "オンライン（Zoom）", "APIエンジニア"),
    ("gRPC実践研修", "Protocol BuffersによるIDL設計・双方向ストリーミング・Go実装を学ぶ", "gRPC,Go,マイクロサービス", "2026-07-14 10:00〜17:00", "渋谷オフィス", "バックエンドエンジニア"),
    ("WebSocket/リアルタイム通信設計", "Socket.IO・WebSocket・SSEの使い分けとスケール設計を実践", "WebSocket,Node.js,リアルタイム", "2026-07-21 10:00〜17:00", "オンライン（Zoom）", "バックエンドエンジニア"),
    ("Elasticsearch全文検索実装", "マッピング設計・アナライザー・スコアリング・集計を実践", "Elasticsearch,Python,検索", "2026-07-28 10:00〜17:00", "渋谷オフィス", "バックエンドエンジニア"),
    ("Kafka入門〜応用", "プロデューサー/コンシューマー設計・Kafka Streams・Schema Registry", "Kafka,ストリーミング,データ", "2026-08-05 10:00〜17:00", "オンライン（Zoom）", "データエンジニア"),
    ("Prometheus/Grafana監視実践", "メトリクス設計・アラートルール・ダッシュボード構築のハンズオン", "Prometheus,Grafana,SRE,監視", "2026-07-08 10:00〜17:00", "オンライン（Zoom）", "インフラ・SREエンジニア"),
    ("SLI/SLO策定ワークショップ", "サービスの信頼性目標設定とエラーバジェット運用の実践設計", "SRE,SLO,監視,Kubernetes", "2026-07-22 10:00〜17:00", "渋谷オフィス", "SRE・インフラエンジニア"),
    ("障害対応・ポストモーテム研修", "インシデント対応フロー・根本原因分析・ポストモーテム作成の実践", "SRE,インシデント管理,ドキュメント", "2026-08-12 10:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
    ("Raspberry Pi IoT入門", "センサーデータ取得・MQTT通信・クラウド連携をRaspberry Piで実践", "IoT,Python,MQTT,Linux", "2026-07-26 10:00〜17:00", "渋谷オフィス（実機あり）", "IoT・組み込み志望"),
    ("組み込みLinux開発研修", "Buildroot・YoctoによるカスタムLinuxイメージビルドとデバッグ", "Linux,組み込み,C,IoT", "2026-08-09 10:00〜17:00", "渋谷オフィス（実機あり）", "組み込みエンジニア"),
    ("Tableau入門ワークショップ", "Tableauのデータ接続・計算フィールド・ダッシュボード公開を実践", "Tableau,データ分析,BI", "2026-06-22 10:00〜17:00", "渋谷オフィス", "ビジネスアナリスト・SE"),
    ("Power BI実践研修", "Power QueryによるETL・DAX計算・Power Automateとの連携を学ぶ", "Power BI,DAX,Microsoft 365", "2026-07-06 10:00〜17:00", "オンライン（Zoom）", "データ分析担当者"),
    ("Looker Studio無償BI活用", "Google Looker Studioで始めるデータ可視化の基礎とチーム共有", "Looker,GCP,BI,データ分析", "2026-07-13 13:00〜17:00", "オンライン（Zoom）", "BI入門者"),
    ("エンジニアキャリアデザイン研修", "技術路線・マネジメント路線の選択と5年後のキャリアプランを設計する", "キャリア,スキルアップ", "2026-06-28 13:00〜17:00", "渋谷オフィス", "全エンジニア"),
    ("テックリードへのステップアップ", "コードレビュー・技術選定・採用面接・ロードマップ策定の実践スキルを学ぶ", "テックリード,マネジメント,キャリア", "2026-07-26 13:00〜18:00", "渋谷オフィス", "シニアエンジニア"),
    ("英語技術ドキュメント読解研修", "英語仕様書・RFC・GitHubイシューを効率よく読みこなす実践英語研修", "英語,ドキュメント,スキルアップ", "2026-07-19 13:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
    ("Rustシステムプログラミング入門", "所有権・借用・ライフタイムを基礎からWebAssembly出力まで実践", "Rust,システムプログラミング,WebAssembly", "2026-08-18 10:00〜17:00", "オンライン（Zoom）", "中級以上エンジニア"),
    ("C++モダン実践（C++20）", "コンセプト・レンジ・モジュール・コルーチンを使ったモダンC++実践", "C++,システムプログラミング", "2026-08-19 10:00〜17:00", "オンライン（Zoom）", "C++エンジニア"),
    ("OpenAI API活用ハンズオン", "Chat Completions・Function Calling・Assistants APIを実際に組み込む", "OpenAI API,Python,LLM", "2026-08-22 13:00〜17:00", "オンライン（Zoom）", "開発者全般"),
    ("HuggingFaceモデル活用研修", "Transformers・Datasets・PEFT（LoRA）を使ったLLMファインチューニング体験", "Python,HuggingFace,LLM,PyTorch", "2026-08-25 10:00〜17:00", "渋谷オフィス", "機械学習エンジニア"),
    ("LangGraph エージェント開発", "LangGraphによるステートフルなAIエージェント設計と実装", "Python,LangGraph,LLM,エージェント", "2026-08-26 10:00〜17:00", "渋谷オフィス", "AIエンジニア"),
    ("ベクトルデータベース実践", "Qdrant・Pinecone・pgvectorの比較とRAGシステムへの組み込み実践", "Python,Qdrant,RAG,LLM", "2026-08-27 10:00〜17:00", "オンライン（Zoom）", "AIエンジニア"),
    ("データガバナンス入門", "データカタログ・系譜管理・品質管理フレームワークを実務視点で学ぶ", "データガバナンス,SQL,BigQuery", "2026-08-28 10:00〜17:00", "オンライン（Zoom）", "データエンジニア・分析担当"),
    ("dbt実践データ変換研修", "dbtのモデル設計・テスト・ドキュメント生成・CI統合を一通り体験", "dbt,SQL,BigQuery,データエンジニアリング", "2026-09-01 10:00〜17:00", "オンライン（Zoom）", "データエンジニア"),
    ("Apache Spark入門", "RDD/DataFrame/Spark SQL・機械学習パイプラインをAWS EMRで実践", "Spark,Python,AWS,データエンジニアリング", "2026-09-02 10:00〜17:00", "オンライン（Zoom）", "データエンジニア"),
    ("Snowflake活用実践", "Snowflakeのアーキテクチャ・Time Travel・Data Sharing機能を活用", "Snowflake,SQL,クラウド", "2026-09-03 10:00〜17:00", "オンライン（Zoom）", "データエンジニア・DBA"),
    ("FinOpsクラウドコスト最適化", "AWS Cost Explorer・Savings Plans・リソース適正化のFinOps実践", "AWS,クラウド,FinOps,コスト管理", "2026-09-04 10:00〜17:00", "オンライン（Zoom）", "クラウドエンジニア"),
    ("Platform Engineering入門", "Internal Developer Platform設計とBackstageによるポータル構築", "Kubernetes,Backstage,DevOps,IaC", "2026-09-05 10:00〜17:00", "渋谷オフィス", "インフラ・SREエンジニア"),
    ("WebパフォーマンスCore Web Vitals改善", "LCP/CLS/FID計測・画像最適化・バンドル削減の実践ワークショップ", "フロントエンド,Performance,React", "2026-09-08 10:00〜17:00", "オンライン（Zoom）", "フロントエンドエンジニア"),
    ("アクセシビリティ（a11y）実践研修", "WCAG 2.1・スクリーンリーダーテスト・axe DevToolsによる診断実践", "アクセシビリティ,HTML,CSS,JavaScript", "2026-09-09 10:00〜17:00", "オンライン（Zoom）", "フロントエンドエンジニア"),
    ("デザインシステム構築研修", "コンポーネント設計・Storybook・デザイントークン・Figma連携の実践", "フロントエンド,Storybook,デザイン", "2026-09-10 10:00〜17:00", "渋谷オフィス", "フロントエンドエンジニア"),
    ("ネットワーク基礎研修", "TCP/IP・DNS・HTTP/2・TLS 1.3のしくみをパケットキャプチャで体験", "ネットワーク,Linux,インフラ", "2026-09-11 10:00〜17:00", "渋谷オフィス", "インフラ入門者・開発者"),
    ("Linux管理実践", "systemd・ファイルシステム・SELinux・crontab・シェルスクリプトを実践", "Linux,シェルスクリプト,インフラ", "2026-09-12 10:00〜17:00", "オンライン（Zoom）", "インフラエンジニア"),
    ("Git上級・ブランチ戦略研修", "Git internals・rebase/cherry-pick・GitFlow/GitHub Flowの使い分け", "Git,DevOps,チーム開発", "2026-09-15 13:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
    ("コードレビュー技法ワークショップ", "効果的なレビューコメント・心理的安全性・自動化ツール活用を学ぶ", "コードレビュー,チーム開発,品質", "2026-09-16 13:00〜17:00", "渋谷オフィス", "テックリード・シニアエンジニア"),
    ("リファクタリング実践研修", "レガシーコードの安全なリファクタリング手法とテスト整備を実践", "リファクタリング,Python,テスト", "2026-09-17 10:00〜17:00", "オンライン（Zoom）", "中級以上エンジニア"),
    ("エンジニアリングマネージャー入門", "1on1・OKR設定・採用・技術的判断への関わり方を学ぶEM入門研修", "マネジメント,キャリア,リーダーシップ", "2026-09-19 10:00〜17:00", "渋谷オフィス", "シニアエンジニア・TL"),
    ("プロダクトマネジメント基礎", "ユーザーインタビュー・優先順位付け・ロードマップ策定の基礎を学ぶ", "プロダクトマネジメント,PM,UX", "2026-09-22 10:00〜17:00", "渋谷オフィス", "PM志望エンジニア"),
    ("UXデザイン入門", "ユーザーリサーチ・ペルソナ・ジャーニーマップ・プロトタイプ作成", "UX,デザイン,Figma", "2026-09-23 10:00〜17:00", "渋谷オフィス", "エンジニア・デザイナー"),
    ("Figma開発者向け活用研修", "デザインハンドオフ・オートレイアウト・バリアブルの開発者視点での活用", "Figma,デザイン,フロントエンド", "2026-09-24 13:00〜17:00", "オンライン（Zoom）", "フロントエンドエンジニア"),
    ("データドリブンビジネス意思決定", "A/Bテスト設計・統計的有意性・ビジネス指標への落とし込みを学ぶ", "データ分析,統計,ビジネス", "2026-09-25 10:00〜17:00", "渋谷オフィス", "エンジニア・ビジネス職"),
    ("個人情報保護法・GDPR対応実践", "個人情報の定義・取得・管理・開示対応の法的要件と実装方法を学ぶ", "法令対応,セキュリティ,プライバシー", "2026-09-26 13:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
    ("特許・著作権エンジニア向け基礎", "ソフトウェア特許・OSSライセンス・著作権の基礎を実例で学ぶ", "法令,知財,OSS", "2026-09-29 13:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
    ("Webスクレイピング実践研修", "BeautifulSoup・Scrapy・Playwright活用のスクレイピングと倫理対応", "Python,Scrapy,Playwright,データ収集", "2026-09-30 10:00〜17:00", "オンライン（Zoom）", "データエンジニア・開発者"),
    ("開発生産性向上ツール活用研修", "GitHub Copilot・Cursor・Claude Code等AIコーディングツールの効果的な活用", "AI,開発ツール,生産性", "2026-10-02 10:00〜17:00", "渋谷オフィス", "全エンジニア"),
    ("Bashシェルスクリプト実践", "実務で使えるBash自動化スクリプト・cron・ログ解析・バックアップ処理", "Bash,Linux,自動化,DevOps", "2026-10-03 10:00〜17:00", "オンライン（Zoom）", "インフラ・バックエンドエンジニア"),
    ("コンテナセキュリティ実践", "Trivy・Falco・OPAを使ったコンテナイメージ脆弱性管理とランタイム保護", "Docker,Kubernetes,セキュリティ,DevSecOps", "2026-10-06 10:00〜17:00", "オンライン（Zoom）", "DevOps・インフラエンジニア"),
    ("技術ブログ・アウトプット力強化研修", "Zenn・Qiita記事執筆・登壇資料作成・OSSコントリビューションの始め方", "アウトプット,コミュニティ,キャリア", "2026-10-07 13:00〜17:00", "渋谷オフィス", "全エンジニア"),
    ("ソフトウェア見積もり技法", "ファンクションポイント・ストーリーポイント・三点見積もりを実務で活用", "PM,プロジェクト管理,アジャイル", "2026-09-18 13:00〜17:00", "オンライン（Zoom）", "PM・テックリード"),
    ("正規表現マスター研修", "grep/Python/JavaScriptで使う正規表現の体系的な理解と実践活用", "Python,JavaScript,正規表現", "2026-10-01 13:00〜17:00", "オンライン（Zoom）", "全エンジニア"),
]


def seed():
    db = SessionLocal()
    try:
        # 既存案件を全削除して再投入
        deleted_p = db.query(models.Project).delete()
        db.commit()
        print(f"案件削除: {deleted_p}件")

        for row in PROJECTS:
            (name, company, overview, skills, rate, employ, duration,
             pref_skills, location, reward, team_size, interview_count,
             work_process, description) = row
            db.add(models.Project(
                project_name     = name,
                company          = company,
                project_overview = overview,
                required_skills  = skills,
                match_rate       = rate,
                employ_type      = employ,
                project_duration = duration,
                preferred_skills = pref_skills,
                location         = location,
                reward           = reward,
                team_size        = team_size,
                interview_count  = interview_count,
                work_process     = work_process,
                description      = description,
            ))
        db.commit()
        print(f"案件追加: {len(PROJECTS)}件")

        # 研修（重複スキップ）
        added_t = 0
        for title, desc, tags, held_at, location, target in TRAININGS:
            if not db.query(models.Training).filter(models.Training.title == title).first():
                db.add(models.Training(title=title, description=desc, tags=tags,
                                       held_at=held_at, location=location, target=target))
                added_t += 1
        db.commit()
        print(f"研修追加: +{added_t}件")
    except Exception as e:
        db.rollback()
        print(f"エラー: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
