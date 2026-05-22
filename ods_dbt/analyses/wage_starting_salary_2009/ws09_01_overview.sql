-- 賃金構造基本統計調査2009 RAW テーブル概要・コード値確認
select
    count(distinct "産業分類_code")                                 as n_industries,
    count(distinct "都道府県_基本_code")                            as n_prefectures,
    count(distinct "企業規模_4区分_code")                           as n_company_sizes,
    count(distinct "性別_基本の3区分_code")                         as n_sex,
    count(distinct "学歴_5区分_code")                               as n_education,
    listagg(distinct "性別_基本の3区分_code", ',')
        within group (order by "性別_基本の3区分_code")             as sex_codes,
    listagg(distinct "学歴_5区分_code", ',')
        within group (order by "学歴_5区分_code")                   as education_codes,
    listagg(distinct "企業規模_4区分_code", ',')
        within group (order by "企業規模_4区分_code")               as company_size_codes,
    count(case when "value" = '-' then 1 end)                       as dash_values,
    count(case when try_to_number("value") is null
               and "value" != '-' then 1 end)                       as other_non_numeric,
    count(*)                                                        as total_rows
from {{ source('raw', 'WAGE_STARTING_SALARY_2009') }}
