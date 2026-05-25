-- 賃金調査の都道府県コードは2桁（48=全国）。経済センサス系の5桁コード(XX000)とは別体系
select distinct
    prefecture_code,
    prefecture_name,
    -- 48=全国
    prefecture_code = '48' as is_aggregate
from {{ ref('stg_wage_starting_salary_2009') }}
order by prefecture_code
