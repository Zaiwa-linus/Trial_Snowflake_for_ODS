-- 国勢調査2010 RAW テーブル概要・コード値確認
select
    count(distinct "産業分類2010_code")                             as n_industries,
    count(distinct "従業上の地位2010_code")                         as n_emp_statuses,
    count(distinct "男女別2010_code")                               as n_sex,
    count(distinct "地域（2010）_code")                             as n_regions,
    count(distinct "時間軸（年次）_code")                           as n_time_points,
    count(case when "value" = '-' then 1 end)                       as dash_values,
    count(case when try_to_number("value") is null
               and "value" != '-' then 1 end)                       as other_non_numeric,
    min("時間軸（年次）_code")                                      as time_code_sample,
    count(*)                                                        as total_rows
from {{ source('raw', 'POPULATION_CENSUS_2010') }}
