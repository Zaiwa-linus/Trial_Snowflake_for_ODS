select distinct
    industry_code,
    industry_name,
    -- 01=産業計（全産業の集計）
    industry_code = '01' as is_aggregate
from {{ ref('stg_wage_starting_salary_2009') }}
order by industry_code
