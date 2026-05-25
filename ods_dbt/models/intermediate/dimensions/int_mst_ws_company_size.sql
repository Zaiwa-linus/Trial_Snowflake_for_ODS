select distinct
    company_size_code,
    company_size_name,
    -- 01=企業規模計（10人以上全体の集計）
    company_size_code = '01' as is_aggregate
from {{ ref('stg_wage_starting_salary_2009') }}
order by company_size_code
