select
    survey_year,
    industry_code,
    prefecture_code,
    company_size_code,
    sex_code,
    education_code,
    value
from {{ ref('stg_wage_starting_salary_2009') }}
where
    -- 産業：産業計(01)を除外
    industry_code != '01'
    -- 都道府県：全国(48)を除外
    and prefecture_code != '48'
    -- 企業規模：規模計(01)を除外
    and company_size_code != '01'
    -- 性別：男女計(01)を除外
    and sex_code != '01'
    -- 学歴：学歴計(01)を除外
    and education_code != '01'
