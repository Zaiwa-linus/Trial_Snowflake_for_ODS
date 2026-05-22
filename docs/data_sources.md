# RAWレイヤー データソース定義

dbtでsourceを定義する際はここを参照すること。

## ソースの場所

- Database: `ODS_TRIAL`
- Schema: `RAW`

## テーブル一覧

### `ECONOMIC_CENSUS_2009`

**入っているデータ**  
e-Statの経済センサス‐基礎調査（2009年）。産業分類×従業者規模×経営組織×地域の組み合わせに対する事業所数・従業者数。統計表ID: `0003032544`

**データの作られ方**  
`scripts/load_estat_to_snowflake.py` でe-StatのAPIから取得したCSVをSnowflakeにロードしたもの。データの詳細は `data/0003032544/column_summary.yml` を参照。
