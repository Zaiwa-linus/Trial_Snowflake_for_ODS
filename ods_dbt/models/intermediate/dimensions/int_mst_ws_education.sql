select distinct
    education_code,
    education_name,
    -- 01=学歴計
    education_code = '01' as is_aggregate
from {{ ref('stg_wage_starting_salary_2009') }}
order by education_code
