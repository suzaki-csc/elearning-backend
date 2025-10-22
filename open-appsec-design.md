# open-appsec レポジトリの概要と基本設計

作成日: 2025年10月20日

---

## 目次

1. [概要](#1-概要)
2. [システムアーキテクチャ](#2-システムアーキテクチャ)
3. [基本設計](#3-基本設計)
4. [主要な技術スタック](#4-主要な技術スタック)
5. [セキュリティ監査](#5-セキュリティ監査)
6. [ディレクトリ構造概要](#6-ディレクトリ構造概要)
7. [今後の開発への示唆](#7-今後の開発への示唆)

---

## 1. 概要

### 1.1 プロジェクトの目的

open-appsecは、機械学習を活用したプリエンプティブなWebアプリケーション・API脅威保護を提供するオープンソースのWAF（Web Application Firewall）エンジンです。OWASP Top-10攻撃やゼロデイ攻撃に対する防御を実現します。

### 1.2 主要な特徴

- **機械学習ベースの脅威検出**: 2つのMLモデル（教師あり・教師なし）を使用
- **マルチプラットフォーム対応**: Linux、Docker、Kubernetes環境に対応
- **多様なWebサーバー統合**: NGINX、Kong、APISIX、Envoy、Istioをサポート
- **柔軟な管理方法**: 宣言的な設定ファイル、Kubernetes Helmチャート、SaaS Web UIによる管理
- **ライセンス**: Apache 2.0ライセンスのオープンソース

### 1.3 機械学習モデル

#### 1.3.1 教師ありモデル（Supervised Model）
数百万のリクエスト（悪意のある/良性）で事前学習されたモデル

- **Basicモデル**: テスト・監視環境向け（リポジトリに同梱）
- **Advancedモデル**: 本番環境推奨（ポータルからダウンロード）

#### 1.3.2 教師なしモデル（Unsupervised Model）
保護対象環境で特定のトラフィックパターンをリアルタイムで学習するモデル

---

## 2. システムアーキテクチャ

### 2.1 全体構成図

```
┌──────────────────────────────────────────────────────────────┐
│                     管理レイヤー                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Web UI      │  │ Local Policy │  │ K8s Helm     │        │
│  │ (SaaS)      │  │ YAML         │  │ Charts       │        │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘        │
└─────────┼─────────────────┼──────────────────┼───────────────┘
          │                 │                  │
          └─────────────────┼──────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Orchestration Service (cp-nano-agent)                 │  │
│  │  - ポリシー管理                                          │  │
│  │  - サービス制御                                          │  │
│  │  - パッケージハンドリング                                │  │
│  │  - ヘルスチェック                                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   Core Services Layer                         │
│  ┌──────────────────────┐  ┌──────────────────────┐          │
│  │ HTTP Transaction     │  │ Attachment           │          │
│  │ Handler Service      │  │ Registration Manager │          │
│  │ - トラフィック検査    │  │ - アタッチメント管理  │          │
│  └──────────────────────┘  └──────────────────────┘          │
│  ┌──────────────────────┐  ┌──────────────────────┐          │
│  │ Agent Cache Service  │  │ Prometheus Service   │          │
│  └──────────────────────┘  └──────────────────────┘          │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              Security Components Layer                        │
│  ┌──────────┐ ┌────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │ WAAP     │ │ IPS        │ │ Layer 7     │ │ Rate      │  │
│  │ Component│ │ Component  │ │ Access Ctrl │ │ Limit     │  │
│  └──────────┘ └────────────┘ └─────────────┘ └───────────┘  │
│  ┌──────────┐ ┌────────────┐ ┌─────────────┐                │
│  │ GeoFilter│ │ Anti-Bot   │ │ CSRF        │                │
│  └──────────┘ └────────────┘ └─────────────┘                │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  Attachment Layer                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ NGINX    │ │ Kong     │ │ APISIX   │ │ Envoy    │        │
│  │ Attachment│ │Attachment│ │Attachment│ │Attachment│        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└──────────────────────────────────────────────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                 Web Servers / API Gateway                     │
│        NGINX / Kong / APISIX / Envoy / Istio                  │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 主要コンポーネント

#### 2.2.1 Nodes (実行可能サービス)

| サービス名 | ディレクトリ | 役割 |
|-----------|-------------|------|
| **Orchestration** | `nodes/orchestration/` | エージェント全体の管理・ポリシー制御・サービスライフサイクル管理 |
| **HTTP Transaction Handler** | `nodes/http_transaction_handler/` | HTTPトラフィックの検査とセキュリティコンポーネントの統合 |
| **Attachment Registration Manager** | `nodes/attachment_registration_manager/` | WebサーバーアタッチメントとAgentの接続管理 |
| **Agent Cache** | `nodes/agent_cache/` | 学習データや設定のキャッシュ管理 |
| **Prometheus** | `nodes/prometheus/` | メトリクス収集・エクスポート |
| **Central NGINX Manager** | `nodes/central_nginx_manager/` | NGINX統合の集中管理 |

#### 2.2.2 Security Components (セキュリティ機能)

| コンポーネント | ディレクトリ | 機能 |
|---------------|-------------|------|
| **WAAP** | `components/security_apps/waap/` | Web Application & API Protection（機械学習エンジン、攻撃検出） |
| **IPS** | `components/security_apps/ips/` | Intrusion Prevention System（シグネチャベース検出） |
| **Layer 7 Access Control** | `components/security_apps/layer_7_access_control/` | アプリケーション層アクセス制御 |
| **Rate Limit** | `components/security_apps/rate_limit/` | レート制限・DDoS対策 |
| **HTTP Geo Filter** | `components/security_apps/http_geo_filter/` | 地理的フィルタリング |

#### 2.2.3 Core Infrastructure

| コンポーネント | ディレクトリ | 機能 |
|---------------|-------------|------|
| **HTTP Manager** | `components/http_manager/` | HTTPトランザクションの管理とイベントディスパッチ |
| **Core Library** | `core/` | 共通ライブラリ（ロギング、メッセージング、設定管理など） |
| **Attachments** | `attachments/` | Webサーバーとの統合レイヤー |

---

## 3. 基本設計

### 3.1 アーキテクチャパターン

#### 3.1.1 イベント駆動アーキテクチャ

システムは**イベントリスナーパターン**を採用しています。HTTPトランザクションのライフサイクルイベントを定義し、各セキュリティコンポーネントがこれらのイベントを購読して処理を実行します。

**主要なHTTPトランザクションイベント:**

```cpp
- NewHttpTransactionEvent      // 新規トランザクション開始
- HttpRequestHeaderEvent        // リクエストヘッダー受信
- HttpRequestBodyEvent          // リクエストボディ受信
- EndRequestEvent               // リクエスト終了
- ResponseCodeEvent             // レスポンスコード受信
- HttpResponseHeaderEvent       // レスポンスヘッダー受信
- HttpResponseBodyEvent         // レスポンスボディ受信
- EndTransactionEvent           // トランザクション終了
```

各セキュリティコンポーネントは`Listener<EventType>`として各イベントを購読し、検査を実行します。

**実装例:**

```cpp
class WaapComponent::Impl
    : public Listener<NewHttpTransactionEvent>,
      public Listener<HttpRequestHeaderEvent>,
      public Listener<HttpRequestBodyEvent>,
      public Listener<EndRequestEvent>,
      public Listener<ResponseCodeEvent>,
      public Listener<HttpResponseHeaderEvent>,
      public Listener<HttpResponseBodyEvent>,
      public Listener<EndTransactionEvent>
{
    // 各イベントハンドラーを実装
    EventVerdict respond(const NewHttpTransactionEvent &event) override;
    EventVerdict respond(const HttpRequestHeaderEvent &event) override;
    // ...
};
```

#### 3.1.2 Singleton & Dependency Injection

コンポーネント間の依存関係は**Singleton::Consume/Provide**パターンで管理されています。これにより、疎結合な設計と効率的なリソース共有を実現しています。

**実装例:**

```cpp
class WaapComponent :
    public Component,
    Singleton::Consume<I_Table>,           // データテーブル利用
    Singleton::Consume<I_TimeGet>,         // 時刻取得
    Singleton::Consume<I_Telemetry>,       // テレメトリ送信
    Singleton::Consume<I_DeepAnalyzer>,    // 深層分析エンジン
    Singleton::Consume<I_MainLoop>         // メインイベントループ
```

#### 3.1.3 Table-Based State Management

HTTPトランザクションの状態は`I_Table`インターフェースで管理されます:

- トランザクションごとに一意のキーで状態を保存
- 複数コンポーネント間での状態共有
- 自動的な有効期限管理
- スレッドセーフなアクセス

### 3.2 トラフィック処理フロー

```
1. Webサーバー（NGINX等）がHTTPリクエストを受信
              ↓
2. Attachment が HTTP Transaction Handler にリクエスト転送
   （共有メモリ経由で高速通信）
              ↓
3. HTTP Manager がトランザクションを作成、イベント発火
              ↓
4. セキュリティコンポーネントがイベントを処理:
   ┌─────────────────────────────────────┐
   │ • WAAP: 機械学習による攻撃検出       │
   │ • IPS: シグネチャマッチング          │
   │ • Layer7 Access Control: アクセス制御│
   │ • Rate Limit: レート制限チェック     │
   │ • Geo Filter: 地理的フィルタリング   │
   └─────────────────────────────────────┘
              ↓
5. 各コンポーネントがVerdict（判定）を返す:
   - ACCEPT: 通過許可
   - DROP: ブロック
   - INSPECT: さらなる検査が必要
   - WAIT: 非同期処理待ち
              ↓
6. HTTP Manager が最終判定を決定
              ↓
7. Attachment 経由でWebサーバーに結果を返す
              ↓
8. ブロック時: カスタムレスポンス返送
   許可時: アップストリームへ転送
```

### 3.3 機械学習エンジン（WAAP）のフロー

WAAPコンポーネントは2段階の機械学習モデルを使用して脅威を検出します。

```
┌────────────────────────────────────────────┐
│ 1. HTTPリクエストの解析・デコード            │
│    • URL, Body, Headers の抽出              │
│    • JSON/XML パース                        │
│    • エンコード解除                         │
│    • パラメータ正規化                       │
└────────────┬───────────────────────────────┘
             ↓
┌────────────────────────────────────────────┐
│ 2. 特徴量抽出                               │
│    • 攻撃インジケーター                     │
│    • IPアドレス、User-Agent                 │
│    • フィンガープリント                     │
│    • パターンマッチング結果                 │
│    • リクエストメタデータ                   │
└────────────┬───────────────────────────────┘
             ↓
┌────────────────────────────────────────────┐
│ 3. Phase 1: 教師ありモデル                  │
│    • グローバル攻撃パターンとの比較         │
│    • リスクスコア算出                       │
│    • 低リスク → ACCEPT                     │
│    • 高リスク → Phase 2へ                  │
└────────────┬───────────────────────────────┘
             ↓
        疑わしい？
             ↓ Yes
┌────────────────────────────────────────────┐
│ 4. Phase 2: 教師なしモデル                  │
│    • 環境固有のトラフィックパターン分析     │
│    • URL、ユーザー行動との比較              │
│    • 正常な振る舞いからの逸脱検出           │
│    • 最終信頼度スコア算出                   │
└────────────┬───────────────────────────────┘
             ↓
┌────────────────────────────────────────────┐
│ 5. 最終判定                                 │
│    • しきい値との比較                       │
│    • ポリシーモードの適用:                  │
│      - prevent-learn: ブロック + 学習       │
│      - detect-learn: ログのみ + 学習        │
│      - inactive: 無効                       │
│    • ログ生成とレポート送信                 │
└────────────────────────────────────────────┘
```

**主要なWAAPクラス:**

- `Waf2Transaction`: トランザクションごとの状態と判定処理
- `DeepAnalyzer`: 深層分析エンジン
- `WaapAssetState`: アセット（保護対象）ごとの学習状態
- `Scanner`: パターンスキャナー
- `DeepParser`: リクエストボディの深層解析

### 3.4 データフロー

#### 3.4.1 共有メモリ通信（Attachment ⇔ Agent）

- Webサーバープロセスとセキュリティエージェントプロセス間の高速通信
- `/dev/shm` を使用した共有メモリIPC
- `--ipc=host` フラグが必要（Docker環境）
- ゼロコピーでデータ転送
- パフォーマンスへの影響を最小化

#### 3.4.2 REST API通信（サービス間）

- Orchestration ⇔ 他のサービス間の通信
- ポート範囲: 12000-13000（デフォルト）
- 管理ポート: 7777（Primary）, 7778（Alternative）
- JSON形式でのメッセージング
- HTTPSによるセキュアな通信

#### 3.4.3 管理通信

- **SaaS管理**: HTTPSで管理ポータルと通信、トークンベース認証
- **ローカル管理**: YAMLファイルベースの設定
- **Kubernetes**: Helm Charts + Annotations による動的設定

### 3.5 主要インターフェース

#### 3.5.1 Core Interfaces (`core/include/services_sdk/interfaces/`)

| インターフェース | 説明 |
|----------------|------|
| `I_Table` | 状態管理テーブル、トランザクション状態の保存・取得 |
| `I_MainLoop` | イベントループ、タイマー管理 |
| `I_Messaging` | サービス間メッセージング |
| `I_Environment` | 環境変数・設定アクセス |
| `I_Logging` | 構造化ロギング |
| `I_RestApi` | REST APIサーバー・クライアント |
| `I_Intelligence_IS_V2` | インテリジェンスサービス統合 |
| `I_TimeGet` | タイムスタンプ取得 |
| `I_AgentDetails` | エージェント情報 |
| `I_Encryptor` | 暗号化・復号化 |

#### 3.5.2 HTTP Processing Interfaces

| インターフェース | 説明 |
|----------------|------|
| `I_HttpManager` | HTTPトランザクション管理 |
| `FilterVerdict` | トラフィック判定結果（ACCEPT/DROP/INSPECT/WAIT） |
| `EventVerdict` | イベント処理結果 |
| `HttpTransactionData` | HTTPトランザクションデータ |

#### 3.5.3 WAAP Specific Interfaces

| インターフェース | 説明 |
|----------------|------|
| `IWaf2Transaction` | WAAPトランザクション操作 |
| `I_DeepAnalyzer` | 深層分析エンジン |
| `I_WaapAssetStatesManager` | アセット状態管理 |

### 3.6 設定管理

#### 3.6.1 ポリシー構造

```yaml
policies:                    # セキュリティポリシー定義
  default:                   # デフォルトポリシー
    triggers:                # ロギングトリガー参照
      - appsec-default-log-trigger
    mode: prevent-learn      # 動作モード
    practices:               # 適用するプラクティス参照
      - webapp-default-practice
    custom-response:         # カスタムレスポンス参照
      appsec-default-web-user-response
  specific-rules: []         # 特定条件のルール

practices:                   # セキュリティプラクティス
  - name: webapp-default-practice
    web-attacks:             # Web攻撃保護設定
      max-body-size-kb: 1000000
      max-header-size-bytes: 102400
      max-object-depth: 40
      minimum-confidence: critical
      protections:
        csrf-protection: inactive
        error-disclosure: inactive
    anti-bot:                # ボット対策
      injected-URIs: []
      validated-URIs: []
    openapi-schema-validation:  # OpenAPIスキーマ検証
      configmap: []
    snort-signatures:        # IPSシグネチャ
      configmap: []

log-triggers:                # ロギング設定
  - name: appsec-default-log-trigger
    appsec-logging:
      all-web-requests: false
      detect-events: true
      prevent-events: true
    extended-logging:
      http-headers: false
      request-body: false

custom-responses:            # カスタムレスポンス定義
  - name: appsec-default-web-user-response
    mode: response-code-only
    http-response-code: 403
```

#### 3.6.2 設定の優先順位

1. Kubernetes Annotations（最優先）
2. Helm Chart Values
3. ローカルポリシーファイル
4. SaaS管理ポータル設定
5. デフォルト設定

### 3.7 デプロイメントモデル

#### 3.7.1 スタンドアローンモード

```bash
# 特徴
- ローカル設定ファイルで完全管理
- SaaS接続不要
- トークン不要

# 起動方法
./cp-nano-agent --standalone

# 用途
- オンプレミス環境
- エアギャップ環境
- 完全なローカル制御が必要な環境
```

#### 3.7.2 ハイブリッドモード（デフォルト）

```bash
# 特徴
- SaaS管理 + ローカル設定の組み合わせ
- 中央集中管理と柔軟性の両立
- トークンで管理ポータルと接続

# 起動方法
./cp-nano-agent --hybrid_mode --token <TOKEN>

# 用途
- 本番環境（推奨）
- 複数エージェントの集中管理
- ポリシーの一元配信
```

#### 3.7.3 Kubernetesモード

```bash
# 特徴
- Helm Chartsでデプロイ
- IngressController統合
- Annotationsで個別設定

# デプロイ方法
helm install open-appsec open-appsec/open-appsec-k8s-nginx-ingress

# 用途
- クラウドネイティブ環境
- 動的スケーリング
- マイクロサービスアーキテクチャ
```

### 3.8 HTTP Transaction Handler の主要コンポーネント構成

`nodes/http_transaction_handler/main.cc`で定義されている統合コンポーネント:

```cpp
NodeComponentsWithTable<
    SessionID,
    NginxAttachment,           // NGINX統合
    GradualDeployment,         // 段階的デプロイメント
    HttpManager,               // HTTPトランザクション管理
    Layer7AccessControl,       // L7アクセス制御
    RateLimit,                 // レート制限
    WaapComponent,             // WAAP（メイン）
    IPSComp,                   // IPS
    KeywordComp,               // キーワード検出
    GeoLocation,               // 地理情報
    HttpGeoFilter              // 地理的フィルタリング
> comps;
```

---

## 4. 主要な技術スタック

### 4.1 開発言語

| 言語 | 用途 |
|-----|------|
| **C++** | コアエンジン、セキュリティコンポーネント（C++11/14標準） |
| **C** | Attachmentレイヤー（パフォーマンス重視） |
| **Go** | smartsyncサービス（別リポジトリ） |
| **Shell Script** | インストーラー、デプロイメントスクリプト |
| **Python** | ビルド補助スクリプト |

### 4.2 ライブラリ・依存関係

#### 4.2.1 必須ライブラリ

| ライブラリ | バージョン | 用途 |
|-----------|-----------|------|
| **Boost** | 最新 | C++拡張ライブラリ（コンテナ、アルゴリズム等） |
| **OpenSSL** | 最新 | 暗号化、TLS/SSL通信 |
| **PCRE2** | 最新 | 正規表現マッチング |
| **libxml2** | 最新 | XML解析 |
| **cURL** | 最新 | HTTP/HTTPSクライアント |
| **Redis** | 最新 | キャッシュストア |
| **Hiredis** | 最新 | Redisクライアントライブラリ |
| **MaxmindDB** | 最新 | GeoIPデータベース |

#### 4.2.2 テスト・開発ライブラリ

| ライブラリ | 用途 |
|-----------|------|
| **GTest** | ユニットテストフレームワーク |
| **GMock** | モックオブジェクトライブラリ |
| **C-Mock** | Cコード用モックライブラリ |

#### 4.2.3 その他の依存関係

| ライブラリ | 用途 |
|-----------|------|
| **Cereal** | C++シリアライゼーション |
| **Picojson** | 軽量JSONライブラリ |
| **YAJL** | JSONパーサー |
| **GraphQL Parser** | GraphQLクエリ解析 |

### 4.3 ビルドシステム

#### 4.3.1 ビルドツール

- **CMake**: ビルド管理（バージョン 2.8.4以上）
- **Make**: ビルド実行
- **GCC/G++**: Cコンパイラ
- **Clang**: 代替コンパイラ（オプション）

#### 4.3.2 コンパイルオプション

```bash
# 最適化フラグ
-O2                    # 最適化レベル2
-fPIC                  # 位置独立コード
-Wall                  # 全警告有効
-Wno-terminate         # terminate警告無効

# Alpine Linux用
-Dalpine               # Alpine固有の定義
```

#### 4.3.3 パッケージング

- **CPack**: パッケージ生成（RPM、DEB等）
- **Makeself**: セルフインストーラー作成
- **Docker**: コンテナイメージ作成

### 4.4 コンテナ・デプロイメント

#### 4.4.1 ベースイメージ

- **Alpine Linux**: 軽量Linuxディストリビューション
- イメージサイズの最小化
- セキュリティアップデートの容易性

#### 4.4.2 コンテナ技術

- **Docker**: コンテナランタイム
- **Kubernetes**: オーケストレーション
- **Helm**: Kubernetesパッケージ管理

### 4.5 CI/CD & 品質保証

- **cppcheck**: 静的コード解析
- **Unit Tests**: 各コンポーネントのユニットテスト
- **GitHub Actions**: CI/CDパイプライン（推測）

---

## 5. セキュリティ監査

### 5.1 第三者監査

- **実施時期**: 2022年9月-10月
- **監査機関**: LEXFO（独立した第三者セキュリティ監査機関）
- **監査レポート**: `LEXFO-CHP20221014-Report-Code_audit-OPEN-APPSEC-v1.2.pdf`
- **範囲**: ソースコード全体のセキュリティレビュー

### 5.2 セキュリティポリシー

- **脆弱性報告先**: security-alert@openappsec.io
- **対応時間**: 24時間以内に確認メール送信
- **公開プロセス**: 内部検証後、適切な開示アクションを決定

### 5.3 ベストプラクティス

- **CII Best Practices Badge取得**: コアインフラストラクチャイニシアチブのベストプラクティス準拠
- **オープンソース**: 透明性の高いコード公開
- **定期的な更新**: セキュリティパッチの迅速な提供

---

## 6. ディレクトリ構造概要

```
openappsec/
├── CMakeLists.txt                    # ルートCMake設定
├── README.md                         # プロジェクト概要
├── LICENSE                           # Apache 2.0ライセンス
├── CONTRIBUTING.md                   # 貢献ガイドライン
├── CODE_OF_CONDUCT.md                # 行動規範
├── SECURITY.md                       # セキュリティポリシー
│
├── core/                             # コアライブラリ
│   ├── include/                      # ヘッダーファイル
│   │   ├── general/                  # 汎用機能
│   │   ├── services_sdk/             # サービスSDK
│   │   │   ├── interfaces/           # インターフェース定義
│   │   │   ├── resources/            # リソース
│   │   │   └── utilities/            # ユーティリティ
│   │   └── attachments/              # アタッチメント用
│   ├── logging/                      # ロギングシステム
│   ├── messaging/                    # メッセージングシステム
│   ├── rest/                         # RESTクライアント/サーバー
│   ├── config/                       # 設定管理
│   ├── table/                        # 状態管理テーブル
│   ├── mainloop/                     # イベントループ
│   ├── metric/                       # メトリクス
│   └── ...                           # その他のコア機能
│
├── components/                       # 機能コンポーネント
│   ├── security_apps/                # セキュリティアプリケーション
│   │   ├── waap/                     # WAAP（メインセキュリティエンジン）
│   │   │   ├── waap_clib/            # WAAPコアライブラリ
│   │   │   │   ├── Waf2Engine.h      # WAFエンジン
│   │   │   │   ├── DeepAnalyzer.h    # 深層分析
│   │   │   │   └── ...
│   │   │   ├── waap_component.cc     # WAAPコンポーネント実装
│   │   │   └── waap_component_impl.cc
│   │   ├── ips/                      # IPS（侵入防止システム）
│   │   ├── layer_7_access_control/   # L7アクセス制御
│   │   ├── rate_limit/               # レート制限
│   │   ├── http_geo_filter/          # 地理的フィルタリング
│   │   ├── orchestration/            # オーケストレーション機能
│   │   ├── local_policy_mgmt_gen/    # ローカルポリシー管理
│   │   └── prometheus/               # Prometheusメトリクス
│   ├── http_manager/                 # HTTPトランザクション管理
│   ├── attachment-intakers/          # アタッチメント受信
│   ├── gradual_deployment/           # 段階的デプロイメント
│   ├── utils/                        # ユーティリティ
│   └── include/                      # 共通ヘッダー
│
├── nodes/                            # 実行可能サービス
│   ├── orchestration/                # オーケストレーションサービス
│   │   ├── main.cc                   # エントリーポイント
│   │   ├── package/                  # パッケージング設定
│   │   └── scripts/                  # スクリプト
│   ├── http_transaction_handler/     # HTTPトランザクションハンドラー
│   │   ├── main.cc                   # エントリーポイント
│   │   └── package/
│   ├── attachment_registration_manager/  # アタッチメント登録マネージャー
│   ├── agent_cache/                  # エージェントキャッシュ
│   ├── prometheus/                   # Prometheusサービス
│   ├── central_nginx_manager/        # 集中NGINX管理
│   └── packaging.cmake               # パッケージング共通設定
│
├── attachments/                      # Webサーバー統合
│   ├── nginx/                        # NGINX attachment
│   │   └── nginx_attachment_util/
│   └── kernel_modules/               # カーネルモジュール（オプション）
│
├── build_system/                     # ビルド・デプロイシステム
│   ├── docker/                       # Dockerイメージ
│   │   ├── Dockerfile                # メインDockerfile
│   │   ├── entry.sh                  # エントリースクリプト
│   │   ├── install-*.sh              # インストールスクリプト
│   │   └── self_managed_openappsec_manifest.json
│   ├── charts/                       # Helm Charts
│   │   ├── open-appsec-k8s-nginx-ingress/
│   │   └── open-appsec-kong/
│   ├── apisix/                       # APISIX統合
│   └── tools/                        # ビルドツール
│       └── packaging/
│
├── deployment/                       # デプロイメント例
│   ├── nginx/                        # NGINXデプロイ例
│   ├── docker-compose/               # Docker Composeファイル
│   ├── apisix/                       # APISIXデプロイ例
│   └── swag/                         # Swagger/API定義
│
├── examples/                         # 設定例
│   ├── local_policy.yaml             # ローカルポリシー例
│   └── juiceshop/                    # サンプルアプリケーション
│
├── external/                         # 外部ライブラリ
│   ├── C-Mock/                       # Cモックライブラリ
│   ├── cereal/                       # シリアライゼーション
│   ├── picojson/                     # JSON
│   ├── yajl/                         # JSONパーサー
│   ├── graphqlparser/                # GraphQLパーサー
│   └── makeself/                     # セルフインストーラー
│
├── events/                           # イベント定義
│   └── include/
│
├── config/                           # 設定ファイル
│   ├── k8s/                          # Kubernetes設定
│   ├── linux/                        # Linux設定
│   └── crds/                         # カスタムリソース定義
│
├── contrib/                          # コミュニティ貢献
│   └── CONTRIBUTING.md
│
└── unit_test.cmake                   # ユニットテスト設定
```

### 6.1 主要ファイルの説明

#### 6.1.1 ルートレベル

- `CMakeLists.txt`: ビルドシステムの設定
- `cppcheck.cmake`: 静的コード解析設定
- `unit_test.cmake`: ユニットテスト設定
- `LEXFO-*.pdf`: セキュリティ監査レポート

#### 6.1.2 コア実装

- `core/include/`: 全コンポーネントで使用されるインターフェース定義
- `components/http_manager/`: HTTPトラフィック処理の中核
- `components/security_apps/waap/`: WAFエンジンの実装

#### 6.1.3 サービス実装

- `nodes/*/main.cc`: 各サービスのエントリーポイント
- `nodes/*/package/`: サービスのパッケージング設定

---

## 7. 今後の開発への示唆

### 7.1 アーキテクチャの強み

#### 7.1.1 モジュラー設計
- コンポーネントベースアーキテクチャにより、新しいセキュリティ機能を容易に追加可能
- 各コンポーネントが独立しているため、個別のテストと改善が可能
- プラグインアーキテクチャとして機能

#### 7.1.2 イベント駆動
- 新しいHTTPイベントやカスタムイベントの追加が容易
- リスナーパターンにより、既存コードへの影響を最小化
- 非同期処理への対応が容易

#### 7.1.3 多様なデプロイメント
- 異なる環境（オンプレミス、クラウド、Kubernetes）に柔軟に対応
- コンテナネイティブ設計
- マルチWebサーバーサポート

### 7.2 拡張可能性

#### 7.2.1 新しいセキュリティコンポーネントの追加

```cpp
// 新しいコンポーネントの実装例
class CustomSecurityComponent :
    public Component,
    public Listener<NewHttpTransactionEvent>,
    Singleton::Consume<I_Table>
{
public:
    EventVerdict respond(const NewHttpTransactionEvent &event) override {
        // カスタム検査ロジック
        return ACCEPT;
    }
};

// HTTP Transaction Handlerに追加
NodeComponentsWithTable<
    SessionID,
    // ... 既存のコンポーネント
    CustomSecurityComponent  // 新しいコンポーネント追加
> comps;
```

#### 7.2.2 新しいWebサーバー統合

- Attachmentインターフェースを実装
- 共有メモリプロトコルの実装
- 新しいnodeサービスとして追加

#### 7.2.3 機械学習モデルの進化

- モデルの定期的な更新メカニズム
- A/Bテストによるモデル比較
- カスタムモデルのトレーニングサポート

### 7.3 パフォーマンス最適化の方向性

#### 7.3.1 処理の並列化
- イベント処理の並列実行
- マルチスレッドによるスループット向上
- 非同期I/Oの活用

#### 7.3.2 キャッシュの活用
- 学習データのキャッシング
- 判定結果のキャッシング
- IPレピュテーションのキャッシング

#### 7.3.3 メモリ効率
- 共有メモリの最適化
- ゼロコピー技術の拡大
- メモリプールの活用

### 7.4 オープンソースコミュニティの活用

#### 7.4.1 貢献の受け入れ
- 明確な貢献ガイドライン
- コードレビュープロセス
- 問題報告と機能リクエストの管理

#### 7.4.2 ドキュメント改善
- APIドキュメントの充実
- アーキテクチャドキュメント
- 開発者ガイド

#### 7.4.3 エコシステムの拡大
- サードパーティ統合
- プラグイン開発
- ベストプラクティス共有

### 7.5 セキュリティの継続的改善

#### 7.5.1 脅威インテリジェンス
- 最新の攻撃パターンの統合
- グローバル脅威データの活用
- 自動更新メカニズム

#### 7.5.2 モデルの精度向上
- 誤検知率の低減
- 新しい攻撃タイプへの対応
- 環境特化型モデル

#### 7.5.3 監査とコンプライアンス
- 定期的なセキュリティ監査
- コンプライアンス要件への対応
- セキュリティベストプラクティスの実装

### 7.6 実装推奨事項

#### 7.6.1 開発環境セットアップ
```bash
# Alpine Linuxでの開発環境構築
apk update
apk add boost-dev openssl-dev pcre2-dev libxml2-dev \
        gtest-dev curl-dev hiredis-dev redis \
        libmaxminddb-dev yq cmake make g++

# ソースコードのクローンとビルド
git clone https://github.com/openappsec/openappsec.git
cd openappsec/
cmake -DCMAKE_INSTALL_PREFIX=build_out .
make install
make package
```

#### 7.6.2 新機能開発のワークフロー
1. イシューの作成と議論
2. フォークとブランチ作成
3. 機能実装とユニットテスト
4. ドキュメント更新
5. プルリクエスト作成
6. コードレビュー
7. マージと統合

#### 7.6.3 テストの重要性
- 各コンポーネントのユニットテスト実装
- 統合テストの実施
- パフォーマンステスト
- セキュリティテスト

---

## 8. まとめ

open-appsecは、機械学習を活用した次世代のWeb Application Firewallとして設計されています。その主な特徴は以下の通りです:

### 8.1 技術的優位性

1. **2段階機械学習**: グローバルな攻撃パターンと環境固有の正常動作の両方を学習
2. **イベント駆動アーキテクチャ**: 拡張性と保守性の高い設計
3. **マルチプラットフォーム**: 多様な環境での動作をサポート
4. **高性能**: 共有メモリ通信による低レイテンシー

### 8.2 運用上の利点

1. **柔軟な管理**: SaaS、ローカル、Kubernetesの各管理方法をサポート
2. **段階的導入**: 検知モード、学習モード、防御モードの選択可能
3. **詳細なログとメトリクス**: セキュリティイベントの可視化
4. **カスタマイズ可能**: ポリシーとレスポンスの細かな制御

### 8.3 コミュニティとエコシステム

1. **オープンソース**: Apache 2.0ライセンスによる自由な利用
2. **積極的な開発**: 継続的な機能追加と改善
3. **セキュリティ重視**: 第三者監査と透明性の確保
4. **充実したドキュメント**: 公式ドキュメントとチュートリアル

open-appsecは、モダンなWebアプリケーションとAPIを保護するための強力で柔軟なソリューションとして、今後も進化を続けることが期待されます。

---

## 参考リンク

- **プロジェクトWebサイト**: https://openappsec.io
- **公式ドキュメント**: https://docs.openappsec.io/
- **GitHubリポジトリ**: https://github.com/openappsec/openappsec
- **ビデオチュートリアル**: https://www.openappsec.io/tutorials
- **プレイグラウンド**: https://www.openappsec.io/playground

---

**ドキュメント作成日**: 2025年10月20日  
**バージョン**: 1.0  
**対象リポジトリ**: openappsec/openappsec (main branch)
