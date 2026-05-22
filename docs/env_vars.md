# 環境変数一覧

このプロジェクトで使用する環境変数の定義。  
`.env` ファイルに記述するか、シェルで `export` して使う。

## Snowflake 接続

| 変数名 | 必須 | デフォルト値 | 説明 |
|--------|------|-------------|------|
| `SNOWFLAKE_ACCOUNT` | ✅ | — | アカウント識別子（Snowsightの「Connect a tool」画面で確認） |
| `SNOWFLAKE_USER` | ✅ | — | ログインユーザー名（Admin > Users で確認） |
| `SNOWFLAKE_PASSWORD` | ✅ | — | ログインパスワード |
| `SNOWFLAKE_WAREHOUSE` | | `WH_DBT_TRIAL` | 使用するウェアハウス名 |
| `SNOWFLAKE_DATABASE` | | `ODS_TRIAL` | 接続先データベース名 |
| `SNOWFLAKE_SCHEMA` | | `RAW` | 接続先スキーマ名 |

## 設定例（.env）

```bash
SNOWFLAKE_ACCOUNT=<your-org>-<your-account>
SNOWFLAKE_USER=<your-login-name>
SNOWFLAKE_PASSWORD=<your-password>
SNOWFLAKE_WAREHOUSE=WH_DBT_TRIAL
SNOWFLAKE_DATABASE=ODS_TRIAL
SNOWFLAKE_SCHEMA=RAW
```

## 注意事項

- `.env` は `.gitignore` に含めること（認証情報のため）
- 認証方式はパスワード認証。`SNOWFLAKE_PASSWORD` に設定したパスワードを使用する
- GitHub Actions では Repository Secrets / Environment Variables として登録する
