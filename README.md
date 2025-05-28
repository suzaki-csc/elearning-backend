# E-Learning System Backend

社内向けe-learningシステムのバックエンドAPI

## 技術スタック

- **Python**: 3.12
- **フレームワーク**: FastAPI
- **データベース**: MySQL 8.0
- **キャッシュ**: Redis
- **ORM**: SQLAlchemy 2.0
- **認証**: JWT + OAuth2
- **コンテナ**: Docker & Docker Compose
- **テスト**: pytest
- **コード品質**: Black, flake8, mypy, bandit

## 開発環境セットアップ

### 前提条件

- Python 3.12
- Poetry
- Docker & Docker Compose
- pyenv (推奨)

### 1. リポジトリクローン

```bash
git clone <repository-url>
cd elearning-backend
```

### 2. Python環境セットアップ

```bash
# pyenvでPython 3.12をインストール
pyenv install 3.12.0
pyenv local 3.12.0

# Poetryで依存関係をインストール
poetry install
```

### 3. 環境変数設定

```bash
cp .env.example .env
# .envファイルを適切に編集
```

### 4. Docker環境構築

```bash
# ビルド実行
./scripts/build.sh

# アプリケーション起動
./scripts/start.sh
```

### 5. テスト実行

```bash
./scripts/test.sh
```

## API仕様

アプリケーション起動後、以下のURLでAPI仕様を確認できます：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 主要エンドポイント

### ユーザ管理
- `GET /api/v1/users/` - ユーザ一覧取得
- `POST /api/v1/users/` - ユーザ作成
- `GET /api/v1/users/{user_id}` - ユーザ詳細取得
- `PUT /api/v1/users/{user_id}` - ユーザ更新
- `GET /api/v1/users/me` - 現在のユーザ情報取得

### コンテンツ管理
- `GET /api/v1/contents/` - コンテンツ一覧取得（検索・フィルタ対応）
- `POST /api/v1/contents/` - コンテンツ作成（管理者のみ）
- `GET /api/v1/contents/{content_id}` - コンテンツ詳細取得
- `PUT /api/v1/contents/{content_id}` - コンテンツ更新（管理者のみ）
- `DELETE /api/v1/contents/{content_id}` - コンテンツ削除（管理者のみ）
- `POST /api/v1/contents/{content_id}/publish` - コンテンツ公開（管理者のみ）
- `POST /api/v1/contents/{content_id}/unpublish` - コンテンツ非公開（管理者のみ）

### カテゴリ管理
- `GET /api/v1/contents/categories` - カテゴリ一覧取得
- `POST /api/v1/contents/categories` - カテゴリ作成（管理者のみ）
- `GET /api/v1/contents/categories/{category_id}` - カテゴリ詳細取得
- `PUT /api/v1/contents/categories/{category_id}` - カテゴリ更新（管理者のみ）
- `DELETE /api/v1/contents/categories/{category_id}` - カテゴリ削除（管理者のみ）

## 開発コマンド

### コード品質チェック

```bash
# フォーマット
poetry run black src tests

# リンティング
poetry run flake8 src tests

# 型チェック
poetry run mypy src

# セキュリティチェック
poetry run bandit -r src
```

### テスト

```bash
# 全テスト実行
poetry run pytest

# カバレッジ付きテスト
poetry run pytest --cov=src

# 特定のテストファイル実行
poetry run pytest tests/test_api/test_users.py
```

### データベース管理

```bash
# マイグレーション作成
poetry run alembic revision --autogenerate -m "migration message"

# マイグレーション実行
poetry run alembic upgrade head

# マイグレーション巻き戻し
poetry run alembic downgrade -1
```

## プロジェクト構成

```
elearning-backend/
├── build/              # Docker関連ファイル
├── scripts/            # 実行スクリプト
├── src/                # アプリケーションコード
│   ├── api/           # APIエンドポイント
│   ├── config/        # 設定ファイル
│   ├── models/        # データベースモデル
│   ├── schemas/       # Pydanticスキーマ
│   ├── services/      # ビジネスロジック
│   └── utils/         # ユーティリティ
└── tests/             # テストコード
```

## 本番環境デプロイ

### Docker本番用ビルド

```bash
docker build -f build/Dockerfile -t elearning-api:latest .
```

### 環境変数（本番環境）

```bash
# セキュリティ
SECRET_KEY=<strong-secret-key>
DEBUG=False

# データベース
DATABASE_URL=mysql+pymysql://user:password@host:port/database

# Redis
REDIS_URL=redis://host:port/0
```

## 今後の実装予定

- [ ] Google Workspace OAuth2連携
- [x] コンテンツ管理API
- [ ] 学習進捗管理API
- [ ] テスト・評価API
- [ ] 通知システム
- [ ] レポート機能
- [ ] ファイルアップロード機能
- [ ] AWS S3連携

## ライセンス

MIT License