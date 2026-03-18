"""
案件(Project)・研修(Training) ダミーデータ 各100件投入スクリプト
実行: cd src && python seed_dummy.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
from database import SessionLocal
import models

# ──────────────────────────────────────────────
# 案件ダミーデータ 100件
# ──────────────────────────────────────────────
PROJECTS = [
    # --- Web / フロントエンド ---
    ("ReactによるECサイトリニューアル",          "株式会社ウェブコマース",    "React/TypeScriptを用いたECサイトのUI全面刷新",              "React,TypeScript,CSS Modules,Storybook",       82, "フルリモート",  date(2026,6,1)),
    ("Vue3 管理画面開発",                          "株式会社アドテック",        "広告配信管理ダッシュボードのVue3移行と機能追加",              "Vue3,Pinia,Vite,TypeScript",                   78, "週3リモート",   date(2026,5,15)),
    ("Next.js コーポレートサイト構築",             "株式会社クリエイティブ",    "Next.js App RouterによるSEO対応コーポレートサイト",          "Next.js,TypeScript,Tailwind CSS",              75, "フルリモート",  date(2026,7,1)),
    ("Angular金融ポータル開発",                    "株式会社フィンポータル",    "Angularベースの資産管理ポータルサイト開発",                   "Angular,RxJS,NgRx,TypeScript",                 80, "一部リモート",  date(2026,6,15)),
    ("Nuxt3 旅行予約サービス",                     "旅行テック株式会社",        "Nuxt3 SSRによる旅行予約フロントエンド開発",                   "Nuxt3,Vue3,TypeScript,GraphQL",                77, "フルリモート",  date(2026,8,1)),
    # --- バックエンド ---
    ("FastAPI マイクロサービス開発",               "株式会社クラウドビズ",      "決済システムのマイクロサービス化とAPI設計",                   "Python,FastAPI,PostgreSQL,Docker",             85, "フルリモート",  date(2026,6,1)),
    ("Spring Boot 基幹システム改修",               "製造業DX株式会社",          "製造ラインの在庫管理システムをSpring Bootで刷新",             "Java,Spring Boot,MySQL,Maven",                 70, "週2リモート",   date(2026,5,1)),
    ("Go言語APIサーバー開発",                      "株式会社スピードテック",    "高トラフィック対応のREST APIをGoで構築",                      "Go,Gin,PostgreSQL,Redis",                      88, "フルリモート",  date(2026,7,1)),
    ("Django RESTfulシステム",                     "株式会社エデュテック",      "学習管理システムのバックエンドAPI開発",                        "Python,Django,DRF,PostgreSQL",                 76, "フルリモート",  date(2026,6,15)),
    ("Ruby on Rails ECバックエンド",               "株式会社コマースラボ",      "大規模ECサイトのバックエンド機能拡張",                         "Ruby,Rails,MySQL,Sidekiq",                     73, "週3リモート",   date(2026,5,15)),
    # --- データ基盤 / ML ---
    ("BigQueryデータウェアハウス構築",             "株式会社データドリブン",    "小売業のBigQuery移行と分析基盤整備",                          "BigQuery,dbt,Python,Airflow",                  90, "フルリモート",  date(2026,6,1)),
    ("機械学習レコメンドエンジン",                 "株式会社AIコマース",        "ユーザー購買履歴を活用したリアルタイム推薦モデル",             "Python,scikit-learn,TensorFlow,Spark",         86, "フルリモート",  date(2026,7,1)),
    ("自然言語処理チャットボット",                 "株式会社カスタマーAI",      "社内問い合わせ対応チャットボットのLLM活用開発",               "Python,LangChain,OpenAI API,FastAPI",          83, "フルリモート",  date(2026,8,1)),
    ("Databricks MLパイプライン",                  "株式会社分析ラボ",          "DatabricksによるMLOpsパイプライン構築",                        "Python,Databricks,MLflow,Spark",               87, "週2リモート",   date(2026,6,15)),
    ("画像認識システム開発",                       "株式会社ビジョンテック",    "製造ラインの外観検査AIモデルの開発と展開",                    "Python,PyTorch,OpenCV,Docker",                 84, "一部リモート",  date(2026,7,15)),
    # --- インフラ / クラウド ---
    ("AWSマイグレーション支援",                    "株式会社クラウドマイグ",    "オンプレミスサーバーのAWS移行設計と実装",                     "AWS,Terraform,Ansible,Linux",                  79, "フルリモート",  date(2026,5,1)),
    ("Kubernetes基盤構築",                         "株式会社コンテナプロ",      "本番EKSクラスタの設計・構築・運用自動化",                     "Kubernetes,Helm,ArgoCD,Terraform",             91, "フルリモート",  date(2026,6,1)),
    ("GCPデータ基盤整備",                          "株式会社クラウドデータ",    "Google CloudによるデータレイクとBIダッシュボード構築",         "GCP,BigQuery,Dataflow,Looker",                 85, "フルリモート",  date(2026,7,1)),
    ("Azureセキュリティ強化",                      "株式会社エンタープライズ",  "Azure AD・Defender活用によるゼロトラスト移行支援",             "Azure,Terraform,PowerShell,Sentinel",          77, "週3リモート",   date(2026,5,15)),
    ("CI/CDパイプライン整備",                      "株式会社DevOpsプロ",        "GitHub ActionsとArgoCD活用の自動デプロイ基盤構築",             "GitHub Actions,ArgoCD,Docker,Kubernetes",      82, "フルリモート",  date(2026,6,15)),
    # --- モバイル ---
    ("Reactネイティブ健康管理アプリ",              "株式会社ヘルスデジタル",    "iOS/Android対応の健康トラッキングアプリ開発",                 "React Native,TypeScript,Firebase",             76, "フルリモート",  date(2026,7,1)),
    ("Flutterフィンテックアプリ",                  "株式会社モバイルフィン",    "家計管理とクレジットスコア表示のFlutterアプリ",               "Flutter,Dart,Firebase,REST API",               74, "週3リモート",   date(2026,6,1)),
    ("iOSネイティブ物流アプリ",                    "株式会社ロジテック",        "配送員向けSwiftUIアプリのリニューアル",                        "Swift,SwiftUI,CoreData,MapKit",                71, "一部リモート",  date(2026,5,1)),
    ("AndroidKotlin在庫管理",                      "株式会社リテールDX",        "倉庫スタッフ向けAndroidアプリの新規開発",                     "Kotlin,Jetpack Compose,Room,Retrofit",         73, "週2リモート",   date(2026,7,15)),
    # --- セキュリティ ---
    ("脆弱性診断・ペネトレーションテスト",         "株式会社セキュアテック",    "WebアプリケーションのOWASP基準脆弱性診断",                    "Python,Burp Suite,OWASP ZAP,Nmap",             69, "フルリモート",  date(2026,6,1)),
    ("SOCアナリスト支援",                          "株式会社サイバーガード",    "SIEMアラート分析とインシデント対応手順整備",                  "Splunk,Elastic SIEM,Python,Linux",             72, "週3リモート",   date(2026,5,15)),
    # --- QA / テスト ---
    ("自動テスト基盤構築（E2E）",                  "株式会社クオリティラボ",    "PlaywrightによるE2Eテスト自動化とCI統合",                     "Playwright,TypeScript,GitHub Actions",         78, "フルリモート",  date(2026,6,15)),
    ("APIテスト自動化",                            "株式会社テストプロ",        "PostmanとPython pytestによるAPIリグレッションテスト整備",     "Python,pytest,Postman,Docker",                 75, "フルリモート",  date(2026,7,1)),
    # --- データエンジニアリング ---
    ("Airflowデータパイプライン構築",              "株式会社データフロー",      "複数ソースのETL処理をAirflowでオーケストレーション",          "Python,Airflow,Spark,PostgreSQL",              84, "フルリモート",  date(2026,6,1)),
    ("Kafkaリアルタイム分析基盤",                  "株式会社ストリーミングDX",  "Kafka + Flink構成のリアルタイムイベント分析基盤",             "Kafka,Flink,Python,Kubernetes",                89, "フルリモート",  date(2026,7,1)),
    # --- ERP / 業務システム ---
    ("SalesforceカスタマイズとAPI連携",            "株式会社CRMソリューション", "Salesforce Apexによる業務フロー自動化と外部API連携",          "Salesforce,Apex,SOQL,REST API",                68, "週2リモート",   date(2026,5,1)),
    ("SAP保守・エンハンス",                        "株式会社ERPコンサル",       "SAP S/4HANAの財務モジュール機能拡張",                         "SAP ABAP,SAP Fiori,HANA SQL",                  65, "一部リモート",  date(2026,6,1)),
    ("kintoneアプリ開発",                          "株式会社スモールDX",        "中小企業向けkintoneカスタマイズと外部連携API開発",            "kintone,JavaScript,REST API,Node.js",          67, "フルリモート",  date(2026,7,1)),
    # --- ブロックチェーン / Web3 ---
    ("Solidityスマートコントラクト開発",           "株式会社Web3ラボ",          "NFTマーケットプレイスのスマートコントラクト実装",             "Solidity,Hardhat,TypeScript,ethers.js",        72, "フルリモート",  date(2026,8,1)),
    ("DeFiプロトコル監査補助",                     "株式会社ブロックセキュア",  "DeFiプロトコルのコードレビューと脆弱性調査",                  "Solidity,Python,Foundry,MythX",                70, "フルリモート",  date(2026,7,15)),
    # --- ゲーム ---
    ("Unityモバイルゲーム開発",                    "株式会社ゲームスタジオ",    "スマホ向けカジュアルゲームの新機能実装とパフォーマンス改善",  "Unity,C#,Firebase,Addressables",               74, "週3リモート",   date(2026,6,1)),
    ("Unrealエンジン映像演出",                     "株式会社XRクリエイト",      "Unreal Engine 5を用いたXR映像コンテンツ制作支援",             "Unreal Engine 5,Blueprint,C++",                71, "一部リモート",  date(2026,7,1)),
    # --- AI / LLM ---
    ("RAGシステム構築",                            "株式会社ナレッジAI",        "社内ドキュメントを活用したRAGシステムの設計と実装",           "Python,LangChain,Qdrant,FastAPI",              88, "フルリモート",  date(2026,6,1)),
    ("LLMファインチューニング",                    "株式会社AIラボ",            "業界特化LLMのファインチューニングと評価パイプライン構築",     "Python,PyTorch,HuggingFace,PEFT",              86, "フルリモート",  date(2026,8,1)),
    ("AIエージェント基盤開発",                     "株式会社エージェントAI",    "LLMベースの自律エージェント設計とツール統合",                 "Python,LangGraph,FastAPI,Docker",              90, "フルリモート",  date(2026,7,15)),
    # --- BI / 分析 ---
    ("Tableau BI基盤構築",                         "株式会社ビジネスBI",        "全社KPI可視化のためのTableauダッシュボード整備",              "Tableau,SQL,Python,PostgreSQL",                76, "週2リモート",   date(2026,5,15)),
    ("Power BIレポート開発",                       "株式会社ビジBX",            "Microsoft Fabricと連携したPower BIレポート自動化",            "Power BI,DAX,Python,Azure",                    74, "週3リモート",   date(2026,6,1)),
    # --- ネットワーク ---
    ("SD-WAN導入支援",                             "株式会社ネットワークPro",   "多拠点SD-WANの設計・構築・運用移行支援",                      "Cisco,SD-WAN,Python,Linux",                    68, "一部リモート",  date(2026,5,1)),
    # --- 組み込み / IoT ---
    ("IoTゲートウェイ開発",                        "株式会社スマートファクト",  "工場センサーデータ収集IoTゲートウェイのファームウェア開発",   "C,Linux,MQTT,Python",                          73, "週2リモート",   date(2026,6,1)),
    ("ROS2ロボット制御",                           "株式会社ロボティクスラボ",  "産業用ロボットアームのROS2ベース制御システム開発",            "ROS2,C++,Python,Ubuntu",                       76, "一部リモート",  date(2026,7,1)),
    # --- クラウドネイティブ ---
    ("サーバーレスアーキテクチャ移行",             "株式会社ラムダクラウド",    "AWS LambdaとAPI Gatewayへのモノリス分解",                     "AWS Lambda,API Gateway,Python,DynamoDB",       81, "フルリモート",  date(2026,6,15)),
    ("マルチクラウド運用自動化",                   "株式会社オムニクラウド",    "AWS/GCP/Azureを横断する統合監視・コスト最適化基盤",          "Terraform,Python,Datadog,Grafana",             83, "フルリモート",  date(2026,7,1)),
    # --- ヘルスケア ---
    ("電子カルテシステム機能追加",                 "株式会社メディカルDX",      "電子カルテへの予約管理APIと患者ポータルUI追加",              "Java,Spring Boot,React,PostgreSQL",            72, "週3リモート",   date(2026,5,15)),
    ("医療画像AI解析",                             "株式会社メドAI",            "胸部X線画像の異常検知AIモデル開発",                          "Python,PyTorch,MONAI,FastAPI",                 85, "フルリモート",  date(2026,7,1)),
    # --- 教育 ---
    ("オンライン学習プラットフォーム開発",         "株式会社エデュプラット",    "動画配信・問題演習・進捗管理機能を持つLMS構築",              "React,Node.js,PostgreSQL,AWS",                 79, "フルリモート",  date(2026,6,1)),
    # --- フィンテック ---
    ("決済API開発",                                "株式会社ペイテック",        "3Dセキュア対応クレジット決済APIの新規開発",                  "Python,FastAPI,PostgreSQL,Redis",               87, "フルリモート",  date(2026,7,1)),
    ("ブロックチェーン決済基盤",                   "株式会社チェーンペイ",      "ステーブルコインを活用したB2B決済システム設計",              "Solidity,Go,PostgreSQL,Kubernetes",             80, "フルリモート",  date(2026,8,1)),
    # --- 物流 ---
    ("配送最適化アルゴリズム開発",                 "株式会社ロジAI",            "AIを用いた配送ルート最適化エンジンの開発",                   "Python,OR-Tools,FastAPI,PostgreSQL",            82, "フルリモート",  date(2026,6,15)),
    ("倉庫管理システム刷新",                       "株式会社ウェアハウスDX",    "RF端末連携の新倉庫管理システム開発",                         "Java,Spring Boot,MySQL,Android",                74, "一部リモート",  date(2026,5,1)),
    # --- HR Tech ---
    ("採用管理SaaS開発",                           "株式会社HRクラウド",        "AIスクリーニング付き採用管理プラットフォームのAPI開発",       "Python,FastAPI,PostgreSQL,OpenAI API",          81, "フルリモート",  date(2026,6,1)),
    ("勤怠・給与システム統合",                     "株式会社ペイロールDX",      "勤怠システムと給与計算エンジンのAPI連携基盤構築",            "Java,Spring Boot,REST API,PostgreSQL",          69, "週2リモート",   date(2026,5,15)),
    # --- マーケティング ---
    ("CRMデータ分析基盤",                          "株式会社マーケDX",          "顧客行動データの収集・集計・可視化基盤構築",                 "Python,Spark,BigQuery,Looker",                  83, "フルリモート",  date(2026,7,1)),
    ("MA連携API開発",                              "株式会社マーケオート",      "Marketo・Salesforce連携のオートメーションAPI開発",            "Python,REST API,PostgreSQL,Docker",             76, "フルリモート",  date(2026,6,1)),
    # --- 社内DX ---
    ("社内ポータル刷新",                           "製造業DX株式会社",          "SharePointベースの社内情報共有ポータルリニューアル",          "React,TypeScript,SharePoint,REST API",          71, "週3リモート",   date(2026,5,1)),
    ("RPA・業務自動化",                            "株式会社オートメーション",  "UiPathによる経理・人事業務のRPA化",                          "UiPath,Python,Excel VBA,REST API",              66, "週2リモート",   date(2026,5,15)),
    # --- クラウドデータ ---
    ("Snowflakeデータ基盤",                        "株式会社SnowDX",            "SnowflakeによるDWH統合と分析クエリ最適化",                   "Snowflake,dbt,Python,Airflow",                  86, "フルリモート",  date(2026,7,1)),
    ("Redshift移行支援",                           "株式会社AWSデータ",         "オンプレDWHのAmazon Redshiftへの移行とクエリ最適化",         "AWS Redshift,Python,dbt,SQL",                   82, "フルリモート",  date(2026,6,15)),
    # --- グリーンテック ---
    ("再エネ予測AIシステム",                       "株式会社グリーンAI",        "太陽光発電量予測モデルの開発と運用基盤構築",                 "Python,scikit-learn,FastAPI,PostgreSQL",         80, "フルリモート",  date(2026,7,15)),
    # --- 追加50件 ---
    ("Node.js WebSocket リアルタイムチャット",     "株式会社コミュニティラボ",  "Node.jsとSocket.IOを用いたチャットシステムのスケール改善",   "Node.js,Socket.IO,Redis,Docker",                77, "フルリモート",  date(2026,6,1)),
    ("PostgreSQL パフォーマンスチューニング",       "株式会社DBプロ",            "大規模PostgreSQLのインデックス最適化とクエリ改善",           "PostgreSQL,PgBouncer,Linux,Python",             75, "フルリモート",  date(2026,5,15)),
    ("GraphQL APIゲートウェイ構築",                "株式会社APIファースト",     "複数マイクロサービスを束ねるGraphQL APIゲートウェイ開発",    "GraphQL,Node.js,Apollo,TypeScript",             81, "フルリモート",  date(2026,7,1)),
    ("ElasticsearchFull-text検索基盤",             "株式会社サーチDX",          "ECサイト向けElasticsearch全文検索基盤の構築と最適化",        "Elasticsearch,Kibana,Python,Docker",            79, "フルリモート",  date(2026,6,15)),
    ("メール配信基盤リニューアル",                 "株式会社メールマーケ",      "大量メール配信システムの耐障害性向上とSPF/DKIM対応",         "Python,Celery,Redis,AWS SES",                   73, "フルリモート",  date(2026,5,1)),
    ("マイクロフロントエンド移行",                 "株式会社モジュラーWeb",     "モノリシックSPAをマイクロフロントエンドへ分割移行",          "React,Module Federation,Webpack,TypeScript",    84, "フルリモート",  date(2026,7,1)),
    ("WebAssembly パフォーマンス改善",             "株式会社WASMラボ",          "CADビューワーをWASM化してブラウザ上でネイティブ速度実現",    "Rust,WebAssembly,TypeScript,C++",               78, "フルリモート",  date(2026,8,1)),
    ("OpenTelemetry可観測性基盤",                  "株式会社オブザーバビリティ","OpenTelemetryによる分散トレーシングと可観測性基盤導入",      "OpenTelemetry,Jaeger,Prometheus,Grafana",       85, "フルリモート",  date(2026,6,1)),
    ("Terraform IaC統一化",                        "株式会社IaCコンサル",       "マルチアカウントAWS環境のTerraform IaC化と標準化",           "Terraform,AWS,Python,GitHub Actions",           83, "フルリモート",  date(2026,6,15)),
    ("SREエラーバジェット管理基盤",                "株式会社SREプロ",           "SLI/SLO/エラーバジェット管理ダッシュボードの構築",           "Prometheus,Grafana,Python,Kubernetes",          87, "フルリモート",  date(2026,7,1)),
    ("Stripeサブスクリプション課金",               "株式会社SaaSスタート",      "StripeによるSaaS課金・プラン管理APIの実装",                  "Node.js,TypeScript,Stripe,PostgreSQL",          79, "フルリモート",  date(2026,6,1)),
    ("Auth0認証基盤導入",                          "株式会社アイデンティティ",  "Auth0を用いたOIDC/SSOシングルサインオン基盤の導入",          "Auth0,Node.js,TypeScript,React",                76, "フルリモート",  date(2026,5,15)),
    ("GISマッピングシステム開発",                  "株式会社マップDX",          "地図データ可視化と経路分析GISシステムの開発",                "Python,GeoPandas,PostGIS,React",                77, "フルリモート",  date(2026,7,15)),
    ("AR/MR業務支援アプリ",                        "株式会社スペーシャルDX",    "HoloLens向けの現場作業支援ARアプリ開発",                     "Unity,C#,MRTK,Azure Spatial Anchors",           72, "一部リモート",  date(2026,7,1)),
    ("デジタルツイン製造ライン",                   "株式会社デジタルマニュ",    "Unity/Unreal Engineによる製造ラインデジタルツイン構築",      "Unity,C#,REST API,InfluxDB",                    74, "一部リモート",  date(2026,8,1)),
    ("量子コンピューティング研究支援",             "株式会社量子ラボ",          "Qiskitを用いた量子アルゴリズムプロトタイプ実装補助",         "Python,Qiskit,NumPy,Jupyter",                   68, "フルリモート",  date(2026,9,1)),
    ("スマートコントラクト監査ツール",             "株式会社DeFiセキュリティ",  "Solidityコードの静的解析ツール開発",                         "Python,Slither,Solidity,Docker",                71, "フルリモート",  date(2026,7,1)),
    ("OSSコントリビューション支援",                "株式会社オープンソースラボ","Pythonコミュニティライブラリのバグ修正と機能追加",           "Python,GitHub,pytest,Sphinx",                   69, "フルリモート",  date(2026,6,1)),
    ("低遅延動画ストリーミング基盤",               "株式会社メディアストリーム", "WebRTCとHLSを活用した低遅延ライブ配信基盤の構築",            "WebRTC,FFmpeg,Node.js,AWS CloudFront",          82, "フルリモート",  date(2026,6,15)),
    ("音声認識AIシステム",                         "株式会社ボイスAI",          "コールセンター向け音声認識・議事録自動生成システム開発",      "Python,Whisper,FastAPI,PostgreSQL",             84, "フルリモート",  date(2026,7,1)),
    ("レガシーCOBOL移行",                          "株式会社レガシーDX",        "金融基幹COBOLシステムのJava/Pythonへのリライト支援",         "COBOL,Java,Python,SQL",                         64, "週3リモート",   date(2026,5,1)),
    ("プロダクトアナリティクス基盤",               "株式会社プロダクトDX",      "Mixpanel/Amplitude連携のユーザー行動分析基盤構築",           "Python,Mixpanel,BigQuery,dbt",                  80, "フルリモート",  date(2026,6,1)),
    ("サプライチェーン可視化",                     "株式会社SCMテック",         "サプライチェーンデータの統合・可視化ダッシュボード開発",     "Python,Spark,Tableau,PostgreSQL",               78, "フルリモート",  date(2026,7,1)),
    ("ESGデータ管理システム",                      "株式会社サステナDX",        "ESG指標収集・集計・レポート自動生成システムの開発",          "Python,FastAPI,PostgreSQL,React",               76, "フルリモート",  date(2026,6,15)),
    ("アクセシビリティ改善コンサル",               "株式会社インクルーシブWeb",  "既存WebサービスのWCAG 2.1 AA準拠対応とテスト",               "HTML,CSS,JavaScript,axe DevTools",              70, "フルリモート",  date(2026,5,15)),
    ("PWA開発",                                    "株式会社プログレッシブWeb",  "オフライン対応の注文管理PWAアプリ開発",                      "React,TypeScript,Service Worker,IndexedDB",     77, "フルリモート",  date(2026,6,1)),
    ("マルチテナントSaaS基盤",                     "株式会社SaaSアーキ",        "テナント分離・課金・RBAC対応マルチテナントSaaSの設計実装",   "Python,FastAPI,PostgreSQL,Kubernetes",          88, "フルリモート",  date(2026,7,1)),
    ("データカタログ構築",                         "株式会社データガバナンス",  "Atlan/OpenMetadataによるデータカタログ導入と整備",           "Python,OpenMetadata,PostgreSQL,Airflow",         82, "フルリモート",  date(2026,6,1)),
    ("フィーチャーストア構築",                     "株式会社MLOpsプロ",         "Feasutフィーチャーストアの導入とML基盤への統合",             "Python,Feast,Redis,PostgreSQL",                 83, "フルリモート",  date(2026,7,1)),
    ("ドキュメント自動生成ツール",                 "株式会社テックライト",      "OpenAI APIを活用したAPI仕様書・設計書の自動生成ツール開発",  "Python,FastAPI,OpenAI API,Jinja2",              79, "フルリモート",  date(2026,6,15)),
    ("海外EC多通貨対応",                           "株式会社グローバルEC",      "多通貨・多言語対応ECサイトのバックエンド拡張",               "Python,Django,Stripe,PostgreSQL",               75, "フルリモート",  date(2026,7,15)),
    ("クロスプラットフォームデスクトップアプリ",   "株式会社デスクトップDX",    "ElectronによるWindowsおよびmacOS向け業務ツール開発",         "Electron,React,TypeScript,SQLite",              74, "フルリモート",  date(2026,6,1)),
    ("データプライバシー対応基盤",                 "株式会社プライバシーDX",    "GDPRおよび個人情報保護法対応のデータ匿名化基盤構築",         "Python,PostgreSQL,FastAPI,Docker",              78, "フルリモート",  date(2026,5,15)),
    ("ノーコード連携プラットフォーム",             "株式会社ノーコードDX",      "Make/Zapierと社内システムのノーコード連携基盤開発",          "Node.js,REST API,PostgreSQL,Docker",            71, "フルリモート",  date(2026,6,1)),
    ("リアルタイム協調編集ツール開発",             "株式会社コラボDX",          "OperationalTransformation/CRDTを用いたリアルタイム共同編集",  "Node.js,WebSocket,TypeScript,Redis",            80, "フルリモート",  date(2026,7,1)),
    ("Notionライク社内ナレッジ基盤",               "株式会社ナレッジDX",        "ブロックエディタ型の社内Wiki・ドキュメント管理システム開発",  "React,TypeScript,Node.js,PostgreSQL",           78, "フルリモート",  date(2026,6,15)),
    ("音楽ストリーミングバックエンド",             "株式会社ミュージックテック",  "楽曲配信・プレイリスト・レコメンドAPIのバックエンド開発",    "Go,PostgreSQL,Redis,AWS S3",                    76, "フルリモート",  date(2026,7,15)),
]

# ──────────────────────────────────────────────
# 研修ダミーデータ 100件
# ──────────────────────────────────────────────
TRAININGS = [
    # --- プログラミング基礎 ---
    ("Python基礎講座",                        "Pythonの文法・データ構造・ファイル操作を実践的に学ぶ入門コース",                 "Python,プログラミング基礎",               "2026-06-10 10:00〜17:00", "オンライン（Zoom）",        "IT未経験者・文系新卒"),
    ("Javaオブジェクト指向入門",              "クラス設計・継承・インターフェースをハンズオンで学ぶJava基礎研修",               "Java,OOP",                                "2026-06-17 10:00〜17:00", "オンライン（Zoom）",        "新卒エンジニア"),
    ("JavaScript基礎＆ES2023",               "変数・関数・非同期処理(async/await)まで最新JSを体系的に学ぶ",                   "JavaScript,フロントエンド",               "2026-06-24 10:00〜17:00", "オンライン（Zoom）",        "フロントエンド志望者"),
    ("TypeScript実践入門",                    "型システム・ジェネリクス・decoratorを使いこなすTS実践コース",                    "TypeScript,JavaScript",                   "2026-07-01 10:00〜17:00", "オンライン（Zoom）",        "JavaScript経験者"),
    ("Go言語基礎",                            "Goの並行処理・エラーハンドリング・テストを学ぶ入門研修",                        "Go,バックエンド",                         "2026-07-08 10:00〜17:00", "オンライン（Zoom）",        "バックエンドエンジニア"),
    # --- Webフレームワーク ---
    ("React実践ワークショップ",               "Hooks・状態管理・パフォーマンス最適化を実際のアプリ開発で学ぶ",                 "React,TypeScript,フロントエンド",         "2026-06-14 10:00〜18:00", "渋谷オフィス",              "フロントエンドエンジニア"),
    ("Vue3コンポジションAPI研修",             "Options APIからComposition APIへの移行と実践的なコンポーネント設計",             "Vue3,TypeScript",                         "2026-06-21 10:00〜18:00", "渋谷オフィス",              "Vue.js経験者"),
    ("FastAPI実践開発研修",                   "FastAPIによるREST API設計・認証・テスト・Dockerデプロイまで学ぶ",               "Python,FastAPI,Docker",                   "2026-07-05 10:00〜18:00", "渋谷オフィス",              "Pythonエンジニア"),
    ("Django REST Framework入門",             "DjangでのモデルAPI設計・認証・ページネーションを体系的に学ぶ",                  "Python,Django,バックエンド",              "2026-07-12 10:00〜17:00", "オンライン（Zoom）",        "Pythonバックエンド志望"),
    ("Spring Boot 実践開発",                  "Spring BootによるRESTful API・セキュリティ・テスト設計の実践研修",              "Java,Spring Boot,バックエンド",           "2026-07-19 10:00〜18:00", "渋谷オフィス",              "Javaエンジニア"),
    # --- データベース ---
    ("SQL基礎〜応用ワークショップ",           "SELECT/JOIN/サブクエリ・ウィンドウ関数・インデックス設計まで学ぶ",              "SQL,PostgreSQL,データベース",             "2026-06-11 10:00〜17:00", "オンライン（Zoom）",        "開発者全般"),
    ("PostgreSQL チューニング研修",           "EXPLAIN ANALYZE・パーティショニング・バキューム設定の実践チューニング",         "PostgreSQL,SQL,インフラ",                 "2026-06-25 10:00〜17:00", "オンライン（Zoom）",        "中級以上エンジニア"),
    ("MongoDB入門",                           "ドキュメント指向DBの設計・集計パイプライン・インデックス最適化",                 "MongoDB,NoSQL",                           "2026-07-09 10:00〜17:00", "オンライン（Zoom）",        "バックエンドエンジニア"),
    ("Redis実践活用講座",                     "キャッシュ戦略・Pub/Sub・Redis Stackの新機能を実務目線で学ぶ",                 "Redis,バックエンド,インフラ",             "2026-07-16 10:00〜17:00", "オンライン（Zoom）",        "バックエンドエンジニア"),
    # --- クラウド ---
    ("AWS基礎認定対策講座",                   "EC2・S3・VPC・IAMをハンズオンで学ぶAWS CLF/SAA対策研修",                      "AWS,クラウド,インフラ",                   "2026-06-13 10:00〜18:00", "渋谷オフィス",              "クラウド入門者"),
    ("AWS 上級アーキテクチャ研修",            "Well-Architected Framework準拠のマルチアカウント設計を学ぶ",                   "AWS,Terraform,アーキテクチャ",            "2026-07-04 10:00〜18:00", "渋谷オフィス",              "AWSエンジニア（中級以上）"),
    ("Google Cloud 入門",                     "GCE・GCS・BigQuery・Cloud Runを体験するGCP入門ハンズオン",                     "GCP,クラウド,BigQuery",                   "2026-06-18 10:00〜17:00", "オンライン（Zoom）",        "クラウド入門者"),
    ("Azure fundamentals研修",                "Azure AD・VNet・App Service・AKSを実際に触れるAzure入門研修",                   "Azure,クラウド,インフラ",                 "2026-07-02 10:00〜17:00", "オンライン（Zoom）",        "クラウド入門者"),
    ("マルチクラウド設計ワークショップ",      "AWS/GCP/Azureの強み比較と適材適所のアーキテクチャ選択を学ぶ",                  "AWS,GCP,Azure,アーキテクチャ",            "2026-07-23 10:00〜17:00", "渋谷オフィス",              "クラウドエンジニア（中級）"),
    # --- コンテナ / DevOps ---
    ("Docker基礎研修",                        "Dockerfileの書き方・マルチステージビルド・compose活用を学ぶ",                   "Docker,DevOps,インフラ",                  "2026-06-15 10:00〜17:00", "オンライン（Zoom）",        "開発者全般"),
    ("Kubernetes実践入門",                    "Pod/Service/Ingress/HPA・Helmチャート活用まで段階的に学ぶ",                    "Kubernetes,Docker,DevOps",                "2026-06-29 10:00〜18:00", "渋谷オフィス",              "Dockerユーザー"),
    ("GitHub Actions CI/CD実践",              "ブランチ戦略・テスト自動化・コンテナ自動デプロイまでのCI/CDパイプライン構築",  "GitHub Actions,CI/CD,DevOps",             "2026-07-06 10:00〜17:00", "オンライン（Zoom）",        "開発者全般"),
    ("ArgoCD GitOps研修",                     "ArgoCDによるGitOpsワークフローとKubernetes継続的デリバリーの実践",               "ArgoCD,Kubernetes,GitOps",                "2026-07-13 10:00〜17:00", "オンライン（Zoom）",        "Kubernetesユーザー"),
    ("Terraform IaC入門",                     "HCL文法・モジュール設計・state管理・CIとの連携を学ぶ",                          "Terraform,IaC,AWS",                       "2026-07-20 10:00〜17:00", "オンライン（Zoom）",        "インフラエンジニア"),
    # --- データ / AI ---
    ("データ分析Python入門",                  "pandas・matplotlib・seabornを使った実データ探索的分析ハンズオン",               "Python,pandas,データ分析",                "2026-06-12 10:00〜17:00", "オンライン（Zoom）",        "データ分析入門者"),
    ("機械学習基礎研修",                      "線形回帰・決定木・ランダムフォレスト・モデル評価をscikit-learnで学ぶ",          "Python,scikit-learn,機械学習",            "2026-06-26 10:00〜17:00", "オンライン（Zoom）",        "データサイエンス志望"),
    ("ディープラーニング実践",                "PyTorchによるCNN/RNNモデル構築・転移学習・ONNX変換を実践",                      "Python,PyTorch,ディープラーニング",       "2026-07-10 10:00〜18:00", "渋谷オフィス",              "機械学習エンジニア"),
    ("LLM活用開発研修",                       "OpenAI API・LangChain・RAGパターンを使った実アプリ開発",                        "Python,LangChain,LLM,OpenAI API",         "2026-07-17 10:00〜18:00", "渋谷オフィス",              "開発者全般"),
    ("MLOps実践ワークショップ",               "MLflowとGitHub Actionsで学ぶモデルのバージョン管理・デプロイ・監視",            "Python,MLflow,Kubernetes,DevOps",         "2026-07-24 10:00〜18:00", "渋谷オフィス",              "機械学習エンジニア"),
    ("BigQueryデータエンジニアリング",        "BigQueryのスキーマ設計・dbt変換・スケジュールクエリ・コスト最適化",            "BigQuery,dbt,SQL,GCP",                    "2026-07-31 10:00〜17:00", "オンライン（Zoom）",        "データエンジニア"),
    # --- セキュリティ ---
    ("情報セキュリティ基礎研修",              "OWASP Top10・SQLインジェクション・XSS対策を演習形式で学ぶ",                    "セキュリティ,OWASP,Web",                  "2026-06-16 10:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    ("クラウドセキュリティ実践",              "AWS SecurityHub・GuardDuty・Configを使ったクラウド防御設計",                   "AWS,セキュリティ,クラウド",               "2026-07-07 10:00〜17:00", "オンライン（Zoom）",        "AWSエンジニア"),
    ("ペネトレーションテスト入門",            "Kali Linux・Burp Suite・Nmap・Metasploitの基礎と倫理的ハッキング入門",          "セキュリティ,Burp Suite,Linux",           "2026-07-21 10:00〜17:00", "渋谷オフィス",              "セキュリティ志望"),
    ("ゼロトラストアーキテクチャ設計",        "ゼロトラスト原則に基づいたID管理・マイクロセグメンテーション設計",              "セキュリティ,Azure AD,アーキテクチャ",   "2026-08-04 10:00〜17:00", "オンライン（Zoom）",        "インフラ・クラウドエンジニア"),
    # --- モバイル ---
    ("React Native入門",                      "Expo環境でのコンポーネント設計・ナビゲーション・Firebase連携を学ぶ",            "React Native,JavaScript,モバイル",        "2026-06-20 10:00〜17:00", "オンライン（Zoom）",        "React経験者"),
    ("Flutter実践ワークショップ",             "Riverpodによる状態管理・アニメーション・Platform Channelを実践",               "Flutter,Dart,モバイル",                   "2026-07-04 10:00〜18:00", "渋谷オフィス",              "モバイル開発者"),
    ("Swift/SwiftUI入門",                     "SwiftUIのレイアウト・Combineフレームワーク・CoreDataを学ぶ",                    "Swift,SwiftUI,iOS",                       "2026-07-11 10:00〜17:00", "渋谷オフィス",              "iOS開発志望"),
    ("Kotlin/Jetpack Compose実践",            "Compose UIコンポーネント設計・Room・Retrofitを組み合わせた実践アプリ開発",     "Kotlin,Jetpack Compose,Android",          "2026-07-18 10:00〜17:00", "渋谷オフィス",              "Android開発者"),
    # --- アーキテクチャ / 設計 ---
    ("クリーンアーキテクチャ実践",            "依存性の逆転・ユースケース分離・テスト戦略をPythonコードで学ぶ",               "アーキテクチャ,Python,設計",              "2026-06-23 10:00〜17:00", "オンライン（Zoom）",        "中級以上エンジニア"),
    ("ドメイン駆動設計(DDD)入門",             "ドメインモデル・集約・リポジトリパターンを実例で学ぶDDD研修",                  "DDD,アーキテクチャ,設計",                 "2026-07-07 10:00〜17:00", "渋谷オフィス",              "バックエンドエンジニア"),
    ("マイクロサービス設計パターン",          "サービスメッシュ・サーキットブレーカー・イベントソーシングを学ぶ",              "マイクロサービス,Kubernetes,設計",        "2026-07-14 10:00〜17:00", "オンライン（Zoom）",        "バックエンド・インフラ"),
    ("APIファーストデザイン研修",             "OpenAPI仕様書作成・モック開発・バージョニング戦略の実践",                       "REST API,OpenAPI,設計",                   "2026-07-28 10:00〜17:00", "オンライン（Zoom）",        "開発者全般"),
    # --- テスト / 品質 ---
    ("TDD実践ワークショップ",                 "テスト駆動開発のサイクルをPythonとpytestで体験する半日研修",                   "TDD,Python,pytest,テスト",                "2026-06-27 13:00〜17:00", "オンライン（Zoom）",        "開発者全般"),
    ("自動テスト設計研修",                    "単体・結合・E2Eの各テスト層の設計指針とツール選定を学ぶ",                       "テスト,Playwright,pytest",                "2026-07-11 10:00〜17:00", "渋谷オフィス",              "開発者・QAエンジニア"),
    ("パフォーマンステスト実践",              "Locustによる負荷テスト設計・ボトルネック分析・改善サイクルを学ぶ",              "Python,Locust,パフォーマンス,テスト",    "2026-07-25 10:00〜17:00", "オンライン（Zoom）",        "バックエンドエンジニア"),
    # --- コミュニケーション / PM ---
    ("エンジニアのためのドキュメント術",      "技術仕様書・ADR・README・ポストモーテムの書き方をワークで学ぶ",               "ドキュメント,コミュニケーション",         "2026-06-19 13:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    ("アジャイル開発実践研修",                "スクラムイベント・バックログリファインメント・ベロシティ管理の実践",             "アジャイル,スクラム,プロジェクト管理",    "2026-07-03 10:00〜17:00", "渋谷オフィス",              "全エンジニア"),
    ("技術的負債管理ワークショップ",          "負債の可視化・リファクタリング計画・ステークホルダー説明の実践",               "リファクタリング,アーキテクチャ,PM",     "2026-07-17 13:00〜17:00", "オンライン（Zoom）",        "テックリード・シニア"),
    # --- 専門技術 ---
    ("GraphQL設計と実装",                     "スキーマファースト設計・DataLoader・認可パターンをNodeで実践",                  "GraphQL,Node.js,API",                     "2026-06-30 10:00〜17:00", "オンライン（Zoom）",        "APIエンジニア"),
    ("gRPC実践研修",                          "Protocol BuffersによるIDL設計・双方向ストリーミング・Go実装を学ぶ",            "gRPC,Go,マイクロサービス",                "2026-07-14 10:00〜17:00", "渋谷オフィス",              "バックエンドエンジニア"),
    ("WebSocket/リアルタイム通信設計",        "Socket.IO・WebSocket・SSEの使い分けとスケール設計を実践",                      "WebSocket,Node.js,リアルタイム",          "2026-07-21 10:00〜17:00", "オンライン（Zoom）",        "バックエンドエンジニア"),
    ("Elasticsearch全文検索実装",             "マッピング設計・アナライザー・スコアリング・集計を実践",                        "Elasticsearch,Python,検索",               "2026-07-28 10:00〜17:00", "渋谷オフィス",              "バックエンドエンジニア"),
    ("Kafka入門〜応用",                       "プロデューサー/コンシューマー設計・Kafka Streams・Schema Registry",            "Kafka,ストリーミング,データ",             "2026-08-05 10:00〜17:00", "オンライン（Zoom）",        "データエンジニア"),
    # --- SRE / 監視 ---
    ("Prometheus/Grafana監視実践",            "メトリクス設計・アラートルール・ダッシュボード構築のハンズオン",                "Prometheus,Grafana,SRE,監視",             "2026-07-08 10:00〜17:00", "オンライン（Zoom）",        "インフラ・SREエンジニア"),
    ("SLI/SLO策定ワークショップ",             "サービスの信頼性目標設定とエラーバジェット運用の実践設計",                      "SRE,SLO,監視,Kubernetes",                "2026-07-22 10:00〜17:00", "渋谷オフィス",              "SRE・インフラエンジニア"),
    ("障害対応・ポストモーテム研修",          "インシデント対応フロー・根本原因分析・ポストモーテム作成の実践",               "SRE,インシデント管理,ドキュメント",       "2026-08-12 10:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    # --- 組み込み / IoT ---
    ("Raspberry Pi IoT入門",                  "センサーデータ取得・MQTT通信・クラウド連携をRaspberry Piで実践",               "IoT,Python,MQTT,Linux",                   "2026-07-26 10:00〜17:00", "渋谷オフィス（実機あり）",  "IoT・組み込み志望"),
    ("組み込みLinux開発研修",                 "Buildroot・YoctoによるカスタムLinuxイメージビルドとデバッグ",                   "Linux,組み込み,C,IoT",                    "2026-08-09 10:00〜17:00", "渋谷オフィス（実機あり）",  "組み込みエンジニア"),
    # --- BI / 可視化 ---
    ("Tableau入門ワークショップ",             "Tableauのデータ接続・計算フィールド・ダッシュボード公開を実践",                "Tableau,データ分析,BI",                   "2026-06-22 10:00〜17:00", "渋谷オフィス",              "ビジネスアナリスト・SE"),
    ("Power BI実践研修",                      "Power QueryによるETL・DAX計算・Power Automateとの連携を学ぶ",                 "Power BI,DAX,Microsoft 365",              "2026-07-06 10:00〜17:00", "オンライン（Zoom）",        "データ分析担当者"),
    ("Looker Studio無償BI活用",               "Google Looker Studioで始めるデータ可視化の基礎とチーム共有",                  "Looker,GCP,BI,データ分析",               "2026-07-13 13:00〜17:00", "オンライン（Zoom）",        "BI入門者"),
    # --- キャリア / スキルアップ ---
    ("エンジニアキャリアデザイン研修",        "技術路線・マネジメント路線の選択と5年後のキャリアプランを設計する",             "キャリア,スキルアップ",                   "2026-06-28 13:00〜17:00", "渋谷オフィス",              "全エンジニア"),
    ("テックリードへのステップアップ",        "コードレビュー・技術選定・採用面接・ロードマップ策定の実践スキルを学ぶ",        "テックリード,マネジメント,キャリア",      "2026-07-26 13:00〜18:00", "渋谷オフィス",              "シニアエンジニア"),
    ("英語技術ドキュメント読解研修",          "英語仕様書・RFC・GitHubイシューを効率よく読みこなす実践英語研修",               "英語,ドキュメント,スキルアップ",          "2026-07-19 13:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    # --- 追加30件 ---
    ("Rustシステムプログラミング入門",        "所有権・借用・ライフタイムを基礎からWebAssembly出力まで実践",                  "Rust,システムプログラミング,WebAssembly", "2026-08-18 10:00〜17:00", "オンライン（Zoom）",        "中級以上エンジニア"),
    ("C++モダン実践（C++20）",                "コンセプト・レンジ・モジュール・コルーチンを使ったモダンC++実践",               "C++,システムプログラミング",              "2026-08-19 10:00〜17:00", "オンライン（Zoom）",        "C++エンジニア"),
    ("Scala/Functional Programming基礎",      "Scalaで学ぶ関数型プログラミング・モナド・Cats/ZIO入門",                         "Scala,関数型,バックエンド",               "2026-08-20 10:00〜17:00", "オンライン（Zoom）",        "JVMエンジニア"),
    ("Elixir/Phoenixリアルタイムシステム",   "ElixirのOTP・Phoenix LiveViewによるリアルタイムWeb開発入門",                    "Elixir,Phoenix,リアルタイム",             "2026-08-21 10:00〜17:00", "オンライン（Zoom）",        "バックエンドエンジニア"),
    ("OpenAI API活用ハンズオン",              "Chat Completions・Function Calling・Assistants APIを実際に組み込む",            "OpenAI API,Python,LLM",                   "2026-08-22 13:00〜17:00", "オンライン（Zoom）",        "開発者全般"),
    ("HuggingFaceモデル活用研修",             "Transformers・Datasets・PEFT（LoRA）を使ったLLMファインチューニング体験",        "Python,HuggingFace,LLM,PyTorch",         "2026-08-25 10:00〜17:00", "渋谷オフィス",              "機械学習エンジニア"),
    ("LangGraph エージェント開発",            "LangGraphによるステートフルなAIエージェント設計と実装",                         "Python,LangGraph,LLM,エージェント",      "2026-08-26 10:00〜17:00", "渋谷オフィス",              "AIエンジニア"),
    ("ベクトルデータベース実践",              "Qdrant・Pinecone・pgvectorの比較とRAGシステムへの組み込み実践",               "Python,Qdrant,RAG,LLM",                   "2026-08-27 10:00〜17:00", "オンライン（Zoom）",        "AIエンジニア"),
    ("データガバナンス入門",                  "データカタログ・系譜管理・品質管理フレームワークを実務視点で学ぶ",               "データガバナンス,SQL,BigQuery",           "2026-08-28 10:00〜17:00", "オンライン（Zoom）",        "データエンジニア・分析担当"),
    ("dbt実践データ変換研修",                 "dbtのモデル設計・テスト・ドキュメント生成・CI統合を一通り体験",                 "dbt,SQL,BigQuery,データエンジニアリング", "2026-09-01 10:00〜17:00", "オンライン（Zoom）",        "データエンジニア"),
    ("Apache Spark入門",                      "RDD/DataFrame/Spark SQL・機械学習パイプラインをAWS EMRで実践",                 "Spark,Python,AWS,データエンジニアリング", "2026-09-02 10:00〜17:00", "オンライン（Zoom）",        "データエンジニア"),
    ("Snowflake活用実践",                     "Snowflakeのアーキテクチャ・Time Travel・Data Sharing機能を活用",               "Snowflake,SQL,クラウド",                  "2026-09-03 10:00〜17:00", "オンライン（Zoom）",        "データエンジニア・DBA"),
    ("FinOpsクラウドコスト最適化",            "AWS Cost Explorer・Savings Plans・リソース適正化のFinOps実践",                 "AWS,クラウド,FinOps,コスト管理",         "2026-09-04 10:00〜17:00", "オンライン（Zoom）",        "クラウドエンジニア"),
    ("Platform Engineering入門",              "Internal Developer Platform設計とBackstageによるポータル構築",                  "Kubernetes,Backstage,DevOps,IaC",         "2026-09-05 10:00〜17:00", "渋谷オフィス",              "インフラ・SREエンジニア"),
    ("WebパフォーマンスCore Web Vitals改善",  "LCP/CLS/FID計測・画像最適化・バンドル削減の実践ワークショップ",               "フロントエンド,Performance,React",        "2026-09-08 10:00〜17:00", "オンライン（Zoom）",        "フロントエンドエンジニア"),
    ("アクセシビリティ（a11y）実践研修",      "WCAG 2.1・スクリーンリーダーテスト・axe DevToolsによる診断実践",               "アクセシビリティ,HTML,CSS,JavaScript",   "2026-09-09 10:00〜17:00", "オンライン（Zoom）",        "フロントエンドエンジニア"),
    ("デザインシステム構築研修",              "コンポーネント設計・Storybook・デザイントークン・Figma連携の実践",              "フロントエンド,Storybook,デザイン",      "2026-09-10 10:00〜17:00", "渋谷オフィス",              "フロントエンドエンジニア"),
    ("ネットワーク基礎研修",                  "TCP/IP・DNS・HTTP/2・TLS 1.3のしくみをパケットキャプチャで体験",               "ネットワーク,Linux,インフラ",             "2026-09-11 10:00〜17:00", "渋谷オフィス",              "インフラ入門者・開発者"),
    ("Linux管理実践",                         "systemd・ファイルシステム・SELinux・crontab・シェルスクリプトを実践",           "Linux,シェルスクリプト,インフラ",         "2026-09-12 10:00〜17:00", "オンライン（Zoom）",        "インフラエンジニア"),
    ("Git上級・ブランチ戦略研修",             "Git internals・rebase/cherry-pick・GitFlow/GitHub Flowの使い分け",             "Git,DevOps,チーム開発",                   "2026-09-15 13:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    ("コードレビュー技法ワークショップ",      "効果的なレビューコメント・心理的安全性・自動化ツール活用を学ぶ",               "コードレビュー,チーム開発,品質",          "2026-09-16 13:00〜17:00", "渋谷オフィス",              "テックリード・シニアエンジニア"),
    ("リファクタリング実践研修",              "レガシーコードの安全なリファクタリング手法とテスト整備を実践",                  "リファクタリング,Python,テスト",          "2026-09-17 10:00〜17:00", "オンライン（Zoom）",        "中級以上エンジニア"),
    ("ソフトウェア見積もり技法",              "ファンクションポイント・ストーリーポイント・三点見積もりを実務で活用",           "PM,プロジェクト管理,アジャイル",          "2026-09-18 13:00〜17:00", "オンライン（Zoom）",        "PM・テックリード"),
    ("エンジニアリングマネージャー入門",      "1on1・OKR設定・採用・技術的判断への関わり方を学ぶEM入門研修",                  "マネジメント,キャリア,リーダーシップ",   "2026-09-19 10:00〜17:00", "渋谷オフィス",              "シニアエンジニア・TL"),
    ("プロダクトマネジメント基礎",            "ユーザーインタビュー・優先順位付け・ロードマップ策定の基礎を学ぶ",             "プロダクトマネジメント,PM,UX",            "2026-09-22 10:00〜17:00", "渋谷オフィス",              "PM志望エンジニア"),
    ("UXデザイン入門",                        "ユーザーリサーチ・ペルソナ・ジャーニーマップ・プロトタイプ作成",               "UX,デザイン,Figma",                       "2026-09-23 10:00〜17:00", "渋谷オフィス",              "エンジニア・デザイナー"),
    ("Figma開発者向け活用研修",               "デザインハンドオフ・オートレイアウト・バリアブルの開発者視点での活用",          "Figma,デザイン,フロントエンド",           "2026-09-24 13:00〜17:00", "オンライン（Zoom）",        "フロントエンドエンジニア"),
    ("データドリブンビジネス意思決定",        "A/Bテスト設計・統計的有意性・ビジネス指標への落とし込みを学ぶ",               "データ分析,統計,ビジネス",               "2026-09-25 10:00〜17:00", "渋谷オフィス",              "エンジニア・ビジネス職"),
    ("個人情報保護法・GDPR対応実践",          "個人情報の定義・取得・管理・開示対応の法的要件と実装方法を学ぶ",               "法令対応,セキュリティ,プライバシー",      "2026-09-26 13:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    ("特許・著作権エンジニア向け基礎",        "ソフトウェア特許・OSSライセンス・著作権の基礎を実例で学ぶ",                   "法令,知財,OSS",                           "2026-09-29 13:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    ("Webスクレイピング実践研修",              "BeautifulSoup・Scrapy・Playwright活用のスクレイピングと倫理・robots.txt対応",  "Python,Scrapy,Playwright,データ収集",    "2026-09-30 10:00〜17:00", "オンライン（Zoom）",        "データエンジニア・開発者"),
    ("正規表現マスター研修",                  "grep/Python/JavaScriptで使う正規表現の体系的な理解と実践活用",                 "Python,JavaScript,正規表現",              "2026-10-01 13:00〜17:00", "オンライン（Zoom）",        "全エンジニア"),
    ("開発生産性向上ツール活用研修",          "GitHub Copilot・Cursor・Claude Code等AIコーディングツールの効果的な活用",      "AI,開発ツール,生産性",                    "2026-10-02 10:00〜17:00", "渋谷オフィス",              "全エンジニア"),
    ("Bashシェルスクリプト実践",              "実務で使えるBash自動化スクリプト・cron・ログ解析・バックアップ処理",           "Bash,Linux,自動化,DevOps",               "2026-10-03 10:00〜17:00", "オンライン（Zoom）",        "インフラ・バックエンドエンジニア"),
    ("コンテナセキュリティ実践",              "Trivy・Falco・OPAを使ったコンテナイメージ脆弱性管理とランタイム保護",          "Docker,Kubernetes,セキュリティ,DevSecOps","2026-10-06 10:00〜17:00", "オンライン（Zoom）",        "DevOps・インフラエンジニア"),
    ("技術ブログ・アウトプット力強化研修",    "Zenn・Qiita記事執筆・登壇資料作成・OSSコントリビューションの始め方",          "アウトプット,コミュニティ,キャリア",      "2026-10-07 13:00〜17:00", "渋谷オフィス",              "全エンジニア"),
]


def seed():
    db = SessionLocal()
    try:
        # 既存データ件数確認
        existing_projects  = db.query(models.Project).count()
        existing_trainings = db.query(models.Training).count()
        print(f"既存: 案件 {existing_projects}件 / 研修 {existing_trainings}件")

        # 案件 投入
        added_p = 0
        for name, company, overview, skills, rate, employ, duration in PROJECTS:
            exists = db.query(models.Project).filter(models.Project.project_name == name).first()
            if not exists:
                db.add(models.Project(
                    project_name     = name,
                    company          = company,
                    project_overview = overview,
                    required_skills  = skills,
                    match_rate       = rate,
                    employ_type      = employ,
                    project_duration = duration,
                ))
                added_p += 1

        # 研修 投入
        added_t = 0
        for title, desc, tags, held_at, location, target in TRAININGS:
            exists = db.query(models.Training).filter(models.Training.title == title).first()
            if not exists:
                db.add(models.Training(
                    title       = title,
                    description = desc,
                    tags        = tags,
                    held_at     = held_at,
                    location    = location,
                    target      = target,
                ))
                added_t += 1

        db.commit()
        print(f"追加完了: 案件 +{added_p}件 / 研修 +{added_t}件")
    except Exception as e:
        db.rollback()
        print(f"エラー: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
