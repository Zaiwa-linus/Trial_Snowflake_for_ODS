# プロジェクトルール

## ドキュメント

- 必要な環境変数の一覧は `docs/env_vars.md` に定義されている
- Snowflakeのソースデータの場所と概要は `docs/data_sources.md` に定義されている

## dbt の実行方法

- dbt はプロジェクトルートから `uv run` 経由で実行する
- `--project-dir` と `--profiles-dir` に `ods_dbt` を指定する

```bash
uv run dbt debug --project-dir ods_dbt --profiles-dir ods_dbt
uv run dbt run --project-dir ods_dbt --profiles-dir ods_dbt
```

## 環境変数

- Snowflake 接続に必要な環境変数は `~/.zshenv` に `export` で定義されている
- 変数の一覧は `docs/env_vars.md` を参照

## セキュリティ

- コード・ドキュメント・例示を問わず、実際の認証情報をファイルに書かない
  - 対象: アカウント識別子、ユーザー名、パスワード、トークン、組織名など
  - 例示が必要な場合は `<your-account>` `<your-username>` のようなプレースホルダーを使う
- `.env` ファイルを作成・使用・提案しない（コミット事故による認証情報漏洩を防ぐため）
