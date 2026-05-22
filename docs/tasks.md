# タスク一覧

## Phase 1: データの入手

- [ ] 使用するオープンデータを決める
- [ ] データの取得・確認（CSV等）
- [ ] `seeds/` に配置するかスクリプト取得かを決める

## Phase 2: Snowflake Trial 初期設定

- [ ] Snowflake Trial アカウントの作成
- [ ] Warehouse 作成（`WH_DBT_TRIAL`, XSMALL）
- [ ] Resource Monitor 設定（クレジット上限 20）
- [ ] Database / Schema 作成
  - `ODS_TRIAL.RAW`
  - `ODS_TRIAL.STAGING`
  - `ODS_TRIAL.INTERMEDIATE`
  - `ODS_TRIAL.MART`
  - `ODS_TRIAL.DATA_PRODUCTS`
  - `ODS_TRIAL.DATA_CATALOG`
- [ ] Service User 作成（`SVC_DBT_GITHUB`）
- [ ] Role 作成（`ROLE_DBT_CI`）
- [ ] 必要最小限の権限付与
- [ ] key-pair 認証の設定

## Phase 3: ディレクトリ・プロジェクトの作成

- [ ] dbt project 初期化（`dbt init`）
- [ ] ディレクトリ構成の作成
  - `models/sources/`
  - `models/staging/`
  - `models/intermediate/`
  - `models/marts/`
  - `models/data_products/`
  - `macros/`
  - `seeds/`
  - `tests/`
  - `scripts/`
  - `docs/`
- [ ] `.gitignore` 作成（`profiles.yml`, `.env`, `target/`, `dbt_packages/` 等）
- [ ] `profiles.yml.example` 作成
- [ ] `dbt_project.yml` 設定（`persist_docs`, schema設定 等）
- [ ] `packages.yml` 作成（`dbt_utils` 等）

## Phase 4: dbt プロジェクトの構築

- [ ] `models/sources/raw_sources.yml` 作成
- [ ] Staging モデル作成（`stg_orders`, `stg_customers`）
- [ ] Intermediate モデル作成（`int_order_items_enriched`）
- [ ] Mart モデル作成（`fct_orders`, `dim_customers`）
- [ ] Data Product モデル作成（`dp_sales_orders`, `dp_daily_sales`）
- [ ] `schema.yml` に description / data_type / meta を記述
- [ ] dbt model contracts の設定（Data Product層）
- [ ] dbt tests の追加（`not_null`, `unique`, `relationships` 等）
- [ ] `macros/apply_snowflake_tags.sql` 作成
- [ ] `dbt deps` / `dbt parse` / `dbt compile` で動作確認

## Phase 5: Snowflake との接続・実行

- [ ] `profiles.yml` をローカルに作成（gitignore済）
- [ ] `dbt debug` で接続確認
- [ ] `dbt seed` でサンプルデータ投入
- [ ] `dbt build` で全モデル実行
- [ ] Snowflake 上にオブジェクトが作成されることを確認
- [ ] `persist_docs` により COMMENT が反映されることを確認
- [ ] TAG の反映を確認

## Phase 6: DATA_CATALOG の構築

- [ ] `DATA_CATALOG` テーブル作成（`DATA_PRODUCTS`, `DATA_PRODUCT_COLUMNS`, `QUALITY_RESULTS`）
- [ ] dbt artifacts（`manifest.json`, `catalog.json`）の取得
- [ ] `scripts/export_dbt_artifacts_to_catalog.py` 作成
- [ ] カタログデータの投入確認

## Phase 7: GitHub Actions の設定

- [ ] `.github/workflows/pr-check.yml` 作成（`dbt parse` / `dbt compile`, Snowflake接続なし）
- [ ] `.github/workflows/deploy-dbt.yml` 作成（`dbt build`, main push時）
- [ ] GitHub Environment `snowflake-trial` の作成
- [ ] Variables / Secrets の登録
- [ ] Branch protection の設定（review必須, status checks必須）
- [ ] PR / main push でワークフローが動くことを確認

## MVP 完了条件

- [ ] GitHub public repo がある
- [ ] GitHub Actions で `dbt build` が動く
- [ ] Snowflake に Data Product 用 View が作られる
- [ ] `schema.yml` の description が Snowflake COMMENT に反映される
- [ ] dbt tests が通る
- [ ] Data Product のメタデータが `DATA_CATALOG` に入る
- [ ] README を見れば思想と実行方法が分かる
- [ ] Resource Monitor が設定済み
- [ ] Actions が `ACCOUNTADMIN` ではなく専用 role で動く
- [ ] PR から Snowflake Secrets が使われない
