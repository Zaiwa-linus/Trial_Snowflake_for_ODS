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

---

### `ECONOMIC_CENSUS_2014`

**入っているデータ**  
e-Statの経済センサス‐基礎調査（2014年・平成26年）。産業分類（中分類）×従業者規模（13区分）×経営組織（5区分）×地域（全国・都道府県・大都市）の組み合わせに対する事業所数・従業者数（男女別）・常用雇用者数・1事業所当たり従業者数。統計表ID: `0003111060`

**JOIN キー**  
`ECONOMIC_CENSUS_2009` と `H26_産業分類_code`・`H26_従業者規模_code`・`H26_経営組織5区分_code`・`H26_地域_code` で対応。2009→2014年の時系列変化分析に使用可能。

**データの作られ方**  
`scripts/load_estat_to_snowflake_generic.py` でe-StatのAPIから取得したCSVをSnowflakeにロードしたもの。データの詳細は `data/0003111060/column_summary.yml` を参照。

---

### `POPULATION_CENSUS_2010`

**入っているデータ**  
e-Statの国勢調査（2010年・平成22年）。産業（中分類）×従業上の地位（3区分）×男女別の15歳以上就業者数。地域は全国・都道府県・都道府県市部・人口50万以上の市区。統計表ID: `0003033029`

**JOIN キー**  
`ECONOMIC_CENSUS_2009/2014` と `産業分類2010_code`・`地域（2010）_code`（都道府県コード）で対応。事業所ベースの従業者数（経済センサス）と居住地ベースの就業者数（国勢調査）の比較に使用可能。

**データの作られ方**  
`scripts/load_estat_to_snowflake_generic.py` でe-StatのAPIから取得したCSVをSnowflakeにロードしたもの。データの詳細は `data/0003033029/column_summary.yml` を参照。

---

### `POPULATION_ESTIMATE`

**入っているデータ**  
e-Statの人口推計（年次）。都道府県×年齢（5歳階級）×男女別の総人口。2005年〜現在の時系列。統計表ID: `0004010049`

**JOIN キー**  
`ECONOMIC_CENSUS_2009/2014` と `全国・都道府県_code`（都道府県コード）で対応。人口10万人あたり事業所数・従業者数などの産業密度指標、産業特化係数（Location Quotient）の計算に使用可能。

**データの作られ方**  
`scripts/load_estat_to_snowflake_generic.py` でe-StatのAPIから取得したCSVをSnowflakeにロードしたもの。データの詳細は `data/0004010049/column_summary.yml` を参照。

---

### `WAGE_STARTING_SALARY_2009`

**入っているデータ**  
e-Statの賃金構造基本統計調査（2009年）。都道府県×産業（大分類）×企業規模（4区分）×性別×学歴別の新規学卒者初任給額。統計表ID: `0003031016`

**JOIN キー**  
`ECONOMIC_CENSUS_2009` と `都道府県_基本_code`・`産業分類_code`・`企業規模_4区分_code` で対応。産業×地域×規模別の初任給水準と事業所規模・雇用者数の相関分析に使用可能。

**データの作られ方**  
`scripts/load_estat_to_snowflake_generic.py` でe-StatのAPIから取得したCSVをSnowflakeにロードしたもの。データの詳細は `data/0003031016/column_summary.yml` を参照。
