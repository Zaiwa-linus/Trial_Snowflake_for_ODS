# Snowflake + dbt による社内Data Product Catalog トライアル アクションノート

## 0. 目的

ODSの参照実装は使わず、ODSの設計思想である以下を参考にして、Snowflake + dbt で社内向けデータ開示基盤を試作する。

- Data Product: データそのものの提供単位
- Ontology Product: データの意味・定義・文脈の提供単位
- Discovery: 利用者がデータを発見できる仕組み
- Quality: 利用者がデータの信頼性を判断できる情報

今回の前提:

- DBMSはSnowflake
- 加工・変換はdbt
- 実行はGitHub Actions
- GitHubリポジトリはpublic
- データはオープンデータを使用
- 認証・認可の複雑な制御は不要
- ODS Middleware / SDK / Gateway は使わない

---

## 1. 基本方針

### 採用する考え方

```text
ODSの思想
  ↓
Snowflake + dbt に合わせて再実装
```

### 使うもの

- Snowflake Trial
- dbt
- GitHub public repository
- GitHub Actions
- Open Data
- Snowflake View / Dynamic Table
- Snowflake COMMENT / TAG
- dbt schema.yml
- dbt tests
- dbt model contracts
- dbt docs / artifacts
- 自前 DATA_CATALOG schema

### 使わないもの

- ODS Middleware
- ODS SDK for Semantics
- ODS L2 Web API Gateway
- Keycloak
- OpenFGA
- ODS準拠のRDF/Turtle厳密運用
- 社外データスペース連携機能

---

## 2. 全体アーキテクチャ

```text
GitHub public repo
  └─ dbt project
      ├─ models
      ├─ sources
      ├─ tests
      ├─ exposures
      ├─ semantic definitions
      ├─ macros
      └─ docs
            ↓
GitHub Actions
  - PR: dbt parse / compile only
  - main: dbt build
            ↓
Snowflake Trial
  ├─ RAW
  ├─ STAGING
  ├─ INTERMEDIATE
  ├─ MART
  ├─ DATA_PRODUCTS
  └─ DATA_CATALOG
            ↓
Consumers
  ├─ SQL users
  ├─ BI
  ├─ Notebook
  ├─ Internal app
  └─ AI Agent
```

---

## 3. dbt と Snowflake の責務分担

| 領域 | dbt | Snowflake |
|---|---|---|
| データ加工 | 主担当 | 実行基盤 |
| Data Product定義 | model SQL / schema.yml | View / Table / Dynamic Table |
| 型契約 | model contracts | 実スキーマ |
| 意味定義 | description / meta | COMMENT / TAG |
| 品質保証 | dbt tests | Data Metric Functions / 品質テーブル |
| Lineage | dbt DAG | query history / ACCOUNT_USAGE |
| Discovery | dbt docs / artifacts | DATA_CATALOG / Horizon |
| 指標定義 | dbt Semantic Layer候補 | Snowflake Semantic View候補 |
| 権限 | grants設定 | role / privilege |
| CI/CD | dbt commands | 実行対象 |

---

## 4. Snowflake側の構成

### Database / Schema案

```text
ODS_TRIAL
  ├─ RAW
  │   - 取込元のオープンデータ
  │
  ├─ STAGING
  │   - dbt stg_* models
  │
  ├─ INTERMEDIATE
  │   - dbt int_* models
  │
  ├─ MART
  │   - dbt fct_* / dim_* models
  │
  ├─ DATA_PRODUCTS
  │   - 利用者に公開するData Product
  │
  └─ DATA_CATALOG
      - Data Productのメタデータ
      - カラム定義
      - 業務用語
      - 品質結果
```

### 主要オブジェクト

```text
DATA_PRODUCTS
  ├─ PRODUCT_SALES
  │   ├─ DP_SALES_ORDERS
  │   ├─ DP_DAILY_SALES
  │   └─ SV_SALES
  │
  └─ PRODUCT_MARKETING
      ├─ DP_CAMPAIGNS
      └─ DP_LEADS
```

---

## 5. Data Productの作り方

### 基本ルール

Data Productは、Snowflake上の公開用View / Table / Dynamic Tableとして作る。

```text
dbt model
  ↓
Snowflake object
  ↓
Data Product
```

### レイヤ設計

```text
RAW
  ↓
STAGING
  stg_*
  ↓
INTERMEDIATE
  int_*
  ↓
MART
  fct_*, dim_*
  ↓
DATA_PRODUCTS
  dp_*
```

### materializationの使い分け

| 用途 | dbt materialization |
|---|---|
| 軽い整形・公開契約 | view |
| 重い集計・頻繁に参照 | table |
| 鮮度SLA付き継続更新 | dynamic_table |
| 中間処理 | ephemeral |
| 増分ロード | incremental |

### Data Product model例

```sql
-- models/data_products/sales/dp_sales_orders.sql

{{ config(
    materialized='view',
    schema='PRODUCT_SALES',
    alias='DP_SALES_ORDERS',
    contract={'enforced': true}
) }}

select
    order_id,
    customer_id,
    product_id,
    ordered_at,
    net_amount,
    gross_amount,
    currency,
    order_status
from {{ ref('fct_orders') }}
where is_deleted = false
```

---

## 6. Data Product契約

公開Data Productにはdbt model contractsを使う。

### schema.yml例

```yaml
models:
  - name: dp_sales_orders
    description: 受注明細データ。1行は1注文1明細を表す。
    config:
      contract:
        enforced: true
    meta:
      data_product_id: sales-orders-v1
      domain: commerce
      owner_team: sales-analytics
      lifecycle_status: active
      freshness_sla: daily
      primary_business_concept: SalesOrder
    columns:
      - name: order_id
        data_type: varchar
        description: 注文を一意に識別するID。
        tests:
          - not_null
          - unique
        meta:
          concept_uri: urn:company:commerce:OrderId
          business_name: 注文ID
          privacy_category: non_pii

      - name: customer_id
        data_type: varchar
        description: 顧客マスタ上の顧客ID。
        tests:
          - not_null
        meta:
          concept_uri: urn:company:commerce:CustomerId
          business_name: 顧客ID
          privacy_category: internal_id

      - name: ordered_at
        data_type: timestamp_ntz
        description: 注文が確定した日時。タイムゾーンはAsia/Tokyo。
        meta:
          concept_uri: urn:company:commerce:OrderedAt
          business_name: 注文確定日時

      - name: net_amount
        data_type: number
        description: 値引き後、税抜きの売上金額。返品控除前。
        tests:
          - not_null
        meta:
          concept_uri: urn:company:commerce:NetSalesAmount
          business_name: 税抜売上金額
          unit: JPY
          privacy_category: non_pii
```

---

## 7. 意味提供の設計

ODSでいうOntology Productは、dbt + Snowflakeでは以下で実現する。

```text
dbt schema.yml
  = 意味定義・型・テスト・metaの一次ソース

Snowflake COMMENT
  = dbt descriptionをSnowflakeに反映したもの

Snowflake TAG
  = domain / product_id / concept_uri / privacyなどの機械可読分類

DATA_CATALOG
  = 社内検索・AI Agent向けの構造化メタデータ

Semantic View
  = 指標・ディメンション・メトリクスの意味レイヤ
```

---

## 8. COMMENTの使い方

dbtのdescriptionをSnowflake COMMENTに反映する。

### dbt_project.yml

```yaml
models:
  ods_trial:
    +persist_docs:
      relation: true
      columns: true
```

### 反映イメージ

```text
dbt schema.yml description
  ↓
dbt build
  ↓
Snowflake COMMENT
  ↓
INFORMATION_SCHEMA / Catalog / 利用者が参照
```

### COMMENTに書く内容

| 対象 | 書く内容 |
|---|---|
| Model / View | 粒度、対象範囲、除外条件 |
| Column | 業務上の意味 |
| Metric列 | 算出式、控除条件、単位 |
| Date列 | どの時点の日時か |
| ID列 | 対応するマスタ・識別対象 |

---

## 9. TAGの使い方

TAGは機械可読な分類に使う。

### 付けたいタグ

```text
data_product_id
data_domain
owner_team
concept_uri
privacy_category
freshness_sla
lifecycle_status
```

### Snowflake TAG作成例

```sql
CREATE TAG IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.DATA_PRODUCT_ID;
CREATE TAG IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.DATA_DOMAIN;
CREATE TAG IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.OWNER_TEAM;
CREATE TAG IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.CONCEPT_URI;
CREATE TAG IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.PRIVACY_CATEGORY;
CREATE TAG IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.FRESHNESS_SLA;
CREATE TAG IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.LIFECYCLE_STATUS;
```

### dbt metaからTAGへ反映する方針

```yaml
models:
  - name: dp_sales_orders
    meta:
      tags:
        data_product_id: sales-orders-v1
        data_domain: commerce
        owner_team: sales-analytics
        lifecycle_status: active
```

post-hookまたは専用macroでSnowflake TAGに反映する。

```sql
{{ config(
    post_hook=[
      "{{ apply_snowflake_tags(this, model.meta.get('tags', {})) }}"
    ]
) }}
```

---

## 10. DATA_CATALOG設計

Snowflake内に自前のData Product Registryを持つ。

### 10.1 DATA_PRODUCTS

```sql
CREATE TABLE IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.DATA_PRODUCTS (
    product_id STRING,
    dbt_model_name STRING,
    snowflake_database STRING,
    snowflake_schema STRING,
    snowflake_object STRING,
    product_name STRING,
    domain STRING,
    owner_team STRING,
    description STRING,
    materialization STRING,
    freshness_sla STRING,
    lifecycle_status STRING,
    version STRING,
    dbt_unique_id STRING,
    updated_at TIMESTAMP_NTZ
);
```

### 10.2 DATA_PRODUCT_COLUMNS

```sql
CREATE TABLE IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.DATA_PRODUCT_COLUMNS (
    product_id STRING,
    dbt_model_name STRING,
    column_name STRING,
    data_type STRING,
    business_name STRING,
    description STRING,
    concept_uri STRING,
    unit STRING,
    privacy_category STRING,
    tests ARRAY,
    updated_at TIMESTAMP_NTZ
);
```

### 10.3 BUSINESS_TERMS

```sql
CREATE TABLE IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.BUSINESS_TERMS (
    concept_uri STRING,
    term_ja STRING,
    term_en STRING,
    definition STRING,
    domain STRING,
    parent_concept_uri STRING,
    synonyms ARRAY,
    owner_team STRING,
    version STRING,
    updated_at TIMESTAMP_NTZ
);
```

### 10.4 QUALITY_RESULTS

```sql
CREATE TABLE IF NOT EXISTS ODS_TRIAL.DATA_CATALOG.QUALITY_RESULTS (
    product_id STRING,
    object_name STRING,
    metric_name STRING,
    metric_value FLOAT,
    threshold_value FLOAT,
    status STRING,
    measured_at TIMESTAMP_NTZ
);
```

---

## 11. Discoveryの作り方

初期は以下で十分。

```text
dbt docs
+ dbt artifacts
+ Snowflake DATA_CATALOG
```

### dbt artifacts

```text
manifest.json
catalog.json
run_results.json
sources.json
```

これらを取り込み、`DATA_CATALOG.*` にロードする。

```text
dbt artifacts
  ↓
catalog loader
  ↓
Snowflake DATA_CATALOG.*
  ↓
社内ポータル / AI Agent / Notebook
```

---

## 12. 品質管理

品質はdbt testsを主、Snowflake DMFを補助にする。

### dbt tests

```yaml
columns:
  - name: order_id
    tests:
      - not_null
      - unique

  - name: customer_id
    tests:
      - not_null
      - relationships:
          to: ref('dim_customers')
          field: customer_id

  - name: net_amount
    tests:
      - not_null
```

### 品質項目

| 項目 | 実装 |
|---|---|
| NULLチェック | dbt not_null |
| 一意性 | dbt unique |
| 参照整合性 | dbt relationships |
| 値範囲 | dbt custom test |
| 件数異常 | custom SQL / DMF |
| 鮮度 | source freshness / metadata |
| 継続監視 | Snowflake DMF |
| カタログ表示 | QUALITY_RESULTS |

---

## 13. Semantic Layer

初期は必須ではない。

### Phase 1

```text
dbt schema.yml
+ COMMENT
+ TAG
+ DATA_CATALOG
```

### Phase 2

指標定義が固まったら追加。

候補:

```text
dbt Semantic Layer
または
Snowflake Semantic View
```

### 判断基準

| 条件 | 推奨 |
|---|---|
| dbt Cloud / MetricFlowを使う | dbt Semantic Layer |
| Snowflake内で完結させたい | Snowflake Semantic View |
| Cortex Analystなどを使いたい | Snowflake Semantic View |
| まだ指標が固まっていない | まだ入れない |

---

## 14. GitHub Actions設計

### 基本方針

public repoなので、PRからSnowflakeには接続しない。

```text
pull_request:
  - dbt parse
  - dbt compile
  - lint
  - Snowflake接続なし

push to main:
  - dbt build
  - Snowflake接続あり

workflow_dispatch:
  - 手動dbt build
  - full-refreshなどは手動限定
```

---

## 15. PR用Workflow

```yaml
name: pr-check

on:
  pull_request:

jobs:
  compile:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dbt
        run: pip install dbt-core dbt-snowflake

      - name: Install dbt packages
        run: dbt deps

      - name: Parse dbt project
        run: dbt parse

      - name: Compile dbt project
        run: dbt compile
```

---

## 16. main用Workflow

```yaml
name: deploy-dbt

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

jobs:
  dbt-build:
    runs-on: ubuntu-latest
    environment: snowflake-trial

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dbt
        run: pip install dbt-core dbt-snowflake

      - name: Install dbt packages
        run: dbt deps

      - name: Run dbt build
        run: dbt build --target prod
        env:
          SNOWFLAKE_ACCOUNT: ${{ vars.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ vars.SNOWFLAKE_USER }}
          SNOWFLAKE_ROLE: ${{ vars.SNOWFLAKE_ROLE }}
          SNOWFLAKE_WAREHOUSE: ${{ vars.SNOWFLAKE_WAREHOUSE }}
          SNOWFLAKE_DATABASE: ${{ vars.SNOWFLAKE_DATABASE }}
          SNOWFLAKE_SCHEMA: ${{ vars.SNOWFLAKE_SCHEMA }}
          SNOWFLAKE_PRIVATE_KEY: ${{ secrets.SNOWFLAKE_PRIVATE_KEY }}
          SNOWFLAKE_PRIVATE_KEY_PASSPHRASE: ${{ secrets.SNOWFLAKE_PRIVATE_KEY_PASSPHRASE }}
```

---

## 17. profiles.yml.example

実際の `profiles.yml` は置かない。  
exampleだけ置く。

```yaml
ods_trial:
  target: prod
  outputs:
    prod:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      role: "{{ env_var('SNOWFLAKE_ROLE') }}"
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}"
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}"
      schema: "{{ env_var('SNOWFLAKE_SCHEMA') }}"
      private_key: "{{ env_var('SNOWFLAKE_PRIVATE_KEY') }}"
      private_key_passphrase: "{{ env_var('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE') }}"
      threads: 4
      client_session_keep_alive: false
```

---

## 18. Snowflake Trial初期設定

### 18.1 Warehouse

```sql
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE WAREHOUSE WH_DBT_TRIAL
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;
```

### 18.2 Resource Monitor

```sql
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE RESOURCE MONITOR RM_TRIAL_LIMIT
  WITH CREDIT_QUOTA = 20
  FREQUENCY = MONTHLY
  TRIGGERS
    ON 50 PERCENT DO NOTIFY
    ON 80 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND
    ON 110 PERCENT DO SUSPEND_IMMEDIATE;

ALTER WAREHOUSE WH_DBT_TRIAL SET RESOURCE_MONITOR = RM_TRIAL_LIMIT;
```

### 18.3 Database / Schema

```sql
CREATE DATABASE IF NOT EXISTS ODS_TRIAL;

CREATE SCHEMA IF NOT EXISTS ODS_TRIAL.RAW;
CREATE SCHEMA IF NOT EXISTS ODS_TRIAL.STAGING;
CREATE SCHEMA IF NOT EXISTS ODS_TRIAL.INTERMEDIATE;
CREATE SCHEMA IF NOT EXISTS ODS_TRIAL.MART;
CREATE SCHEMA IF NOT EXISTS ODS_TRIAL.DATA_PRODUCTS;
CREATE SCHEMA IF NOT EXISTS ODS_TRIAL.DATA_CATALOG;
```

### 18.4 Role / User

```sql
CREATE ROLE IF NOT EXISTS ROLE_DBT_CI;

CREATE USER IF NOT EXISTS SVC_DBT_GITHUB
  DEFAULT_ROLE = ROLE_DBT_CI
  DEFAULT_WAREHOUSE = WH_DBT_TRIAL
  MUST_CHANGE_PASSWORD = FALSE;

GRANT ROLE ROLE_DBT_CI TO USER SVC_DBT_GITHUB;
```

### 18.5 Grants

```sql
GRANT USAGE ON WAREHOUSE WH_DBT_TRIAL TO ROLE ROLE_DBT_CI;

GRANT USAGE ON DATABASE ODS_TRIAL TO ROLE ROLE_DBT_CI;

GRANT USAGE ON ALL SCHEMAS IN DATABASE ODS_TRIAL TO ROLE ROLE_DBT_CI;
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE ODS_TRIAL TO ROLE ROLE_DBT_CI;

GRANT CREATE TABLE, CREATE VIEW, CREATE DYNAMIC TABLE
ON ALL SCHEMAS IN DATABASE ODS_TRIAL
TO ROLE ROLE_DBT_CI;

GRANT CREATE TABLE, CREATE VIEW, CREATE DYNAMIC TABLE
ON FUTURE SCHEMAS IN DATABASE ODS_TRIAL
TO ROLE ROLE_DBT_CI;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN DATABASE ODS_TRIAL
TO ROLE ROLE_DBT_CI;

GRANT SELECT, INSERT, UPDATE, DELETE
ON FUTURE TABLES IN DATABASE ODS_TRIAL
TO ROLE ROLE_DBT_CI;

GRANT SELECT
ON ALL VIEWS IN DATABASE ODS_TRIAL
TO ROLE ROLE_DBT_CI;

GRANT SELECT
ON FUTURE VIEWS IN DATABASE ODS_TRIAL
TO ROLE ROLE_DBT_CI;
```

---

## 19. リスクと対策

### 19.1 主なリスク

| リスク | 重要度 | 対策 |
|---|---:|---|
| オープンデータ流出 | 低 | 許容 |
| Snowflake認証情報漏洩 | 高 | key-pair / OIDC、Secrets制限 |
| Snowflakeクレジット浪費 | 高 | Resource Monitor、XSMALL、auto suspend |
| PR経由のSecrets漏洩 | 高 | PRではSnowflake接続しない |
| 任意SQL実行 | 中 | branch protection、review必須 |
| dbt full-refresh事故 | 中 | workflow_dispatch限定 |
| 依存Action改ざん | 中 | SHA pinning検討 |
| profiles.yml誤コミット | 中 | .gitignore、exampleのみ |
| trialと本番の混線 | 中 | account / database / roleを明確に分離 |

### 19.2 public repoで避けるもの

```text
profiles.yml
.env
private key
Snowflake password
API token
本番接続情報
個人アクセストークン
```

### 19.3 public repoに置いてよいもの

```text
dbt_project.yml
models/*.sql
models/**/*.yml
sample seeds
README
公開データ取得スクリプト
profiles.yml.example
```

---

## 20. GitHub側の設定

### 必須

```text
- main branch protection
- required review
- required status checks
- GitHub Secretsはenvironmentに限定
- PR workflowではSecretsを使わない
- Dependabot有効化
```

### GitHub Environment

```text
environment: snowflake-trial
```

Variables:

```text
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_ROLE
SNOWFLAKE_WAREHOUSE
SNOWFLAKE_DATABASE
SNOWFLAKE_SCHEMA
```

Secrets:

```text
SNOWFLAKE_PRIVATE_KEY
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE
```

---

## 21. 推奨リポジトリ構成

```text
snowflake-dbt-data-product-trial/
  README.md
  dbt_project.yml
  packages.yml
  profiles.yml.example
  .gitignore

  .github/
    workflows/
      pr-check.yml
      deploy-dbt.yml

  models/
    sources/
      raw_sources.yml

    staging/
      sales/
        stg_orders.sql
        stg_sales__schema.yml

    intermediate/
      sales/
        int_order_items_enriched.sql
        int_sales__schema.yml

    marts/
      sales/
        fct_orders.sql
        dim_customers.sql
        mart_sales__schema.yml

    data_products/
      sales/
        dp_sales_orders.sql
        dp_daily_sales.sql
        schema.yml
        exposures.yml

  macros/
    apply_snowflake_tags.sql
    export_catalog.sql
    validate_data_product_contract.sql

  seeds/
    sample_orders.csv
    sample_customers.csv

  tests/
    generic/
    singular/

  scripts/
    load_open_data.py
    export_dbt_artifacts_to_catalog.py

  docs/
    architecture.md
    data_product_guideline.md
```

---

## 22. 初期実装ステップ

### Step 1: Snowflake Trial準備

- Snowflake Trial契約
- `WH_DBT_TRIAL` 作成
- Resource Monitor設定
- `ODS_TRIAL` DB作成
- `RAW / STAGING / INTERMEDIATE / MART / DATA_PRODUCTS / DATA_CATALOG` schema作成
- `SVC_DBT_GITHUB` service user作成
- `ROLE_DBT_CI` role作成
- 必要最小限のgrants付与

### Step 2: GitHub public repo作成

- dbt project初期化
- `.gitignore` 作成
- `profiles.yml.example` 作成
- GitHub Environment `snowflake-trial` 作成
- Variables / Secrets登録
- branch protection設定

### Step 3: Open Data投入

選択肢:

```text
A. 小さいCSVをseedsとして置く
B. Actionsで公開URLから取得
C. Snowflake stage経由でロード
```

初期はAでよい。

### Step 4: dbtレイヤ作成

順番:

```text
sources
  ↓
staging
  ↓
intermediate
  ↓
marts
  ↓
data_products
```

最低1つのData Productを作る。

例:

```text
dp_sales_orders
dp_daily_sales
```

### Step 5: 意味情報を付与

- `schema.yml` にdescriptionを書く
- `columns[].description`を書く
- `columns[].data_type`を書く
- `meta` に以下を入れる

```text
data_product_id
domain
owner_team
lifecycle_status
freshness_sla
concept_uri
business_name
unit
privacy_category
```

### Step 6: 品質テストを追加

最低限:

```text
not_null
unique
relationships
accepted_values
custom test
```

### Step 7: GitHub Actions追加

- PRでは `dbt parse` / `dbt compile`
- mainでは `dbt build`
- full-refreshは手動workflow限定

### Step 8: DATA_CATALOG生成

初期はシンプルに以下を生成。

```text
DATA_CATALOG.DATA_PRODUCTS
DATA_CATALOG.DATA_PRODUCT_COLUMNS
DATA_CATALOG.QUALITY_RESULTS
```

入力元:

```text
manifest.json
catalog.json
run_results.json
schema.yml meta
```

### Step 9: README整備

READMEに以下を書く。

```text
- 目的
- アーキテクチャ
- dbt実行方法
- Data Productの定義方法
- schema.ymlの書き方
- GitHub Actionsの設計
- Snowflake Trialの注意点
```

---

## 23. 初期MVPの完了条件

MVPとしては以下ができればよい。

```text
1. GitHub public repoがある
2. GitHub Actionsでdbt buildが動く
3. SnowflakeにData Product用Viewが作られる
4. dbt schema.ymlのdescriptionがSnowflake COMMENTに反映される
5. dbt testsが通る
6. Data ProductのメタデータがDATA_CATALOGに入る
7. READMEを見れば思想と実行方法が分かる
8. Resource Monitorが設定済み
9. ActionsがACCOUNTADMINではなく専用roleで動く
10. PRからSnowflake Secretsが使われない
```

---

## 24. 初期MVPで作るData Product例

### Data Product

```text
sales-orders-v1
```

### Snowflake object

```text
ODS_TRIAL.DATA_PRODUCTS.DP_SALES_ORDERS
ODS_TRIAL.DATA_PRODUCTS.DP_DAILY_SALES
```

### 意味情報

```text
SalesOrder
OrderId
CustomerId
OrderedAt
NetSalesAmount
GrossSalesAmount
Currency
OrderStatus
```

### 品質テスト

```text
order_id not null
order_id unique
customer_id not null
net_amount not null
order_status accepted values
```

---

## 25. 後続拡張

MVP後に検討する。

```text
- Snowflake Semantic View
- dbt Semantic Layer
- Snowflake Data Metric Functions
- Horizon Catalog活用
- Catalog API
- Streamlit in SnowflakeでData Product Portal
- Slack bot / AI AgentからDATA_CATALOG検索
- OIDC / Workload Identity Federationへの移行
- GitHub ActionsのSHA pinning
- dbt package version pinning
- model versioning
```

---

## 26. 最終方針まとめ

今回のトライアルでは、ODSを「使う」のではなく、ODSの思想を以下のようにSnowflake + dbtに落とす。

```text
Data Product
  = dbtで定義されたSnowflake公開View / Table / Dynamic Table

Ontology Product
  = dbt schema.yml + meta + Snowflake COMMENT / TAG + DATA_CATALOG

Discovery
  = dbt docs + dbt artifacts + Snowflake DATA_CATALOG

Quality
  = dbt tests + QUALITY_RESULTS + 将来的にSnowflake DMF

Execution
  = GitHub Actions

Governance
  = GitHub branch protection + Snowflake minimal role + Resource Monitor
```

最初に作るべき最小構成:

```text
Snowflake Trial
+ dbt project
+ public GitHub repo
+ GitHub Actions
+ key-pair auth
+ Resource Monitor
+ Data Product model
+ schema.yml
+ dbt tests
+ persist_docs
+ DATA_CATALOG
```
