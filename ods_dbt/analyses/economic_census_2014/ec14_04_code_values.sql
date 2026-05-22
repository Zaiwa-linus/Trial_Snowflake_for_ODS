-- 各コード列の実際の値を確認
select
    listagg(distinct "表章項目_code", ',') within group (order by "表章項目_code")           as measure_codes,
    listagg(distinct "H26_経営組織5区分_code", ',') within group (order by "H26_経営組織5区分_code") as org_type_codes
from {{ source('raw', 'ECONOMIC_CENSUS_2014') }}
