-- 各コード列の実際の値を確認
select
    listagg(distinct "従業上の地位2010_code", ',') within group (order by "従業上の地位2010_code") as emp_status_codes,
    listagg(distinct "男女別2010_code", ',') within group (order by "男女別2010_code")           as sex_codes
from {{ source('raw', 'POPULATION_CENSUS_2010') }}
