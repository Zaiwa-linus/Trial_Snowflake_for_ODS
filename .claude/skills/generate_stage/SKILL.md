---
description: RAWテーブルの実データを確認してから staging モデルを生成する。staging モデルを新規作成するときに使う。
disable-model-invocation: true
---

## 手順

1. `ods_dbt/analyses/<table_name>/` に調査用SQLを作成する
   - 既存の `ods_dbt/analyses/economic_census_2009/` を参考にする
   - カラム名・サンプル値・カーディナリティを確認するクエリを書く
2. `uv run dbt show --select <file_name> --project-dir ods_dbt --profiles-dir ods_dbt` で実行して実際のカラム名・値を確認する
3. 確認結果をもとに `models/staging/stg_<table_name>.sql` と `.yml` を作成する

## 禁止事項

- RAWの実データを確認せずに staging モデルを作らない
- `models/` 配下に調査用の一時モデル（`inv_` など）を作らない
