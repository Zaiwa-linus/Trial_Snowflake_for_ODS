-- コード列の全値確認
select
    listagg(distinct "学歴_5区分_code", ',') within group (order by "学歴_5区分_code")         as education_codes,
    listagg(distinct "企業規模_4区分_code", ',') within group (order by "企業規模_4区分_code")  as company_size_codes,
    listagg(distinct "産業分類_code", ',') within group (order by "産業分類_code")             as industry_codes
from {{ source('raw', 'WAGE_STARTING_SALARY_2009') }}
