# API リファレンス

このドキュメントは `app/` 配下の FastAPI バックエンドが提供する REST API についてまとめたものです。フロントエンド／Discord Bot 側の実装は対象外です。

## 目次

- [概要](#概要)
- [認証方式](#認証方式)
- [エンドポイント一覧](#エンドポイント一覧)
  - [ヘルスチェック](#ヘルスチェック)
  - [認証 (`/auth`)](#認証-auth)
  - [タスク管理 (`/task`)](#タスク管理-task)
  - [プロンプト解析 (`/prompt_ctl`)](#プロンプト解析-prompt_ctl)
- [データモデル](#データモデル)
- [既知の制限事項](#既知の制限事項)

---

## 概要

- フレームワーク: FastAPI
- DB: PostgreSQL（SQLAlchemy ORM）
- ルーター構成:
  - `app/routers/auth.py` → `/auth` プレフィックス
  - `app/routers/tasks.py` → `/task` プレフィックス
  - `app/routers/prompt_organize.py` → `/prompt_ctl` プレフィックス

---

## 認証方式

保護されたエンドポイントは `Authorization: Bearer <token>` ヘッダーを要求します（`app/auth_relation.py` の `auth_verification` 依存関数で検証）。トークンは以下の2種類が使えます。

| 種類 | 発行方法 | 特徴 |
|---|---|---|
| JWT（短命） | `/auth/login`, `/auth/google` | `ACCESS_TOKEN_EXPIRE_MINUTES` 分で失効。`sub`(email)/`iss`/`aud`/`exp` を含む |
| APIキー（長命） | `/auth/bot_token` | `APISessions` テーブルに保存される opaque な文字列。Bot連携など継続利用向け |

`auth_verification` は、渡されたトークンをまず JWT として検証し、失敗した場合は `APISessions` テーブルの `jwt_token` カラムと一致するか照合します。どちらか一方が成立すればそのユーザーとして認証されます。

---

## エンドポイント一覧

### ヘルスチェック

#### `GET /`

認証不要。稼働確認用。

```json
{"message": "Hello from FastAPI in Docker!"}
```

---

### 認証 (`/auth`)

#### `POST /auth/login`

メールアドレス／パスワードでログインし、JWTを発行します。

- 認証: 不要
- リクエスト形式: `application/x-www-form-urlencoded`（`OAuth2PasswordRequestForm`）
  - `username`: メールアドレス
  - `password`: パスワード
- レスポンス: [`Token`](#token)

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=xxxxx
```

失敗時: `401 Unauthorized`（ユーザーが見つからない／パスワード不一致）

#### `POST /auth/register`

新規ユーザー登録。

- 認証: 不要
- リクエストボディ: [`UserRegisterRequest`](#userregisterrequest)
- レスポンス: [`CreateUser`](#createuser)

```json
{
  "user": {
    "id": 0,
    "email": "user@example.com",
    "password": "xxxxx",
    "confirm_oauth": false
  }
}
```

失敗時: `400 Bad Request`（メールアドレス重複）

#### `GET /auth/google`

Google アカウントでのログイン／カレンダー連携を1つのフローで行うエンドポイント。

- 認証: 不要
- クエリパラメータ:
  - `code`（省略可）: Google からのリダイレクト時に付与される認可コード
- 動作:
  - `code` が無い場合 → Google の同意画面へ `302 Redirect`
  - `code` がある場合 → トークン交換を行い、`Users`/`OAuthToken` を作成または更新し、JWTを返す
- レスポンス（`code` あり時）: [`Token`](#token) 相当の `{"access_token": ..., "token_type": "bearer"}`

必要な環境変数: `CLIENT_ID`, `CLIENT_SECRET`, `CLIENT_AUTH_URI`, `CLIENT_TOKEN_URI`, `ENDPOINT`

#### `POST /auth/bot_token`

ログイン済みユーザーが、長期間有効なAPIキーを発行するためのエンドポイント（Discord Bot 等の外部クライアント連携用）。

- 認証: 必須（JWT）
- リクエストボディ: なし
- レスポンス:

```json
{"api_key": "生成された長期間有効なランダム文字列"}
```

発行されたキーは `APISessions` テーブルに保存され、以後 `Authorization: Bearer <api_key>` として他のエンドポイントにも使用できます。

---

### タスク管理 (`/task`)

すべて認証必須（`Authorization: Bearer <token>`）。

#### `GET /task/`

ログインユーザーの全タスクを取得します。

- レスポンス: [`EventCreate`](#eventcreate) の配列

#### `POST /task/add`

新規タスクを登録します。Google Calendar連携済みの場合、あわせて Google Calendar 側にもイベントを作成し、出発時刻（`departure`）を自動計算します（いずれも失敗時は無視され、ローカル登録自体は成功します）。

- リクエストボディ: [`EventCreate`](#eventcreate)
- レスポンス: [`EventCreate`](#eventcreate)（`google_event_id`/`departure` が付与された状態）

#### `GET /task/view_task`

タスクの詳細を1件取得します。

- クエリパラメータ:
  - `task_id`（int, 必須）
- レスポンス: [`EventCreate`](#eventcreate)

#### `POST /task/update`

既存タスクを更新します（現状は全フィールドを送る必要がある全体更新のみ）。Google Calendar連携済みの場合、あわせて同期・出発時刻の再計算を行います。

- リクエストボディ: [`EventCreate`](#eventcreate)（`id` で対象タスクを特定）
- レスポンス: [`EventCreate`](#eventcreate)

#### `DELETE /task/delete`

タスクを削除します。Google Calendar連携済みかつ `google_event_id` を持つ場合、Google Calendar側のイベントも削除します。

- リクエストボディ: [`EventCreate`](#eventcreate)（`id` のみ実質的に使用）
- レスポンス: 削除されたタスクの内容

#### `POST /task/sync`

Google Calendar への接続確認・サービスハンドルの取得用エンドポイント（内部確認用）。

- 前提: Google Calendar 連携済みであること（未接続の場合 `400 Bad Request`）

---

### プロンプト解析 (`/prompt_ctl`)

#### `POST /prompt_ctl/prompt_analyze`

自然文（日本語）からタスクの候補情報（日付・時刻・タグ・場所・URLなど）を正規表現ベースで抽出します。

- 認証: 必須
- クエリパラメータ:
  - `prompt`（str, 必須）: 解析対象の文章
- レスポンス: 抽出結果（JSON文字列）

```
POST /prompt_ctl/prompt_analyze?prompt=やること 2026/08/15 09:00 東京都渋谷区 通知あり
```

---

## データモデル

### `Token`

| フィールド | 型 | 説明 |
|---|---|---|
| `token_type` | str | 固定値 `"bearer"` |
| `access_token` | str \| null | JWT |
| `refresh_token` | str \| null | 現状未使用（常に `null`） |

### `CreateUser`

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | int | ユーザーID |
| `email` | EmailStr | メールアドレス |
| `name` | str \| null | 表示名（現状DBには保存されない） |
| `password` | SecretStr | パスワード（レスポンス時は値が伏せられる） |
| `confirm_oauth` | bool | Google OAuth連携情報も同時に登録するか |

### `UserRegisterRequest`

| フィールド | 型 | 説明 |
|---|---|---|
| `user` | [`CreateUser`](#createuser) | 登録するユーザー情報 |
| `oauth_tokens` | [`GOauthTokens`](#goauthtokens) \| null | `confirm_oauth=true` の場合に必要 |

### `GOauthTokens`

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | int | - |
| `user_id` | int | - |
| `access_token` | str \| null | - |
| `refresh_token` | str \| null | - |
| `expires_at` | datetime \| null | - |

### `EventCreate`

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | int | タスクID（更新・削除時に使用） |
| `plan_name` | str | 予定名 |
| `date` | `{start_date: str, finish_date: str}` | 開始日・終了日 |
| `time` | `{start_time: str, finish_time: str}` | 開始時刻・終了時刻 |
| `alarm` | bool | 通知の有無 |
| `repeats` | str \| null | 繰り返し設定 |
| `tags` | list[str] | タグ一覧 |
| `location` | str \| null | 場所（Google Calendar同期・出発時刻計算にも使用） |
| `url` | str \| null | 関連URL |
| `departure` | datetime \| null | 自動計算された出発時刻（読み取り専用相当） |
| `memo` | str \| null | メモ |

---

## 既知の制限事項

- `/auth/register` の `confirm_oauth=true` 経路（`GOauthTokens` 経由でのOAuth登録）は、`OAuthToken` テーブルの必須カラム（`provider_sub`）が設定されないため現状動作しません。Google連携は `/auth/google` の利用を推奨します。
- `/task/update` は部分更新に対応しておらず、常に全フィールドを送信する必要があります。
- `/prompt_ctl/prompt_analyze` の解析結果は正規表現ベースの簡易的なものであり、`EventCreate` の形式（`id` 必須、`url` は文字列）とは完全には一致しません。そのまま `/task/add` のボディとして使う場合は変換が必要です。
