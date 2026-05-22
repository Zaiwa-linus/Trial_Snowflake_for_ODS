-- 人口推計 RAW テーブル概要・コード値確認
select
    count(distinct "全国・都道府県_code")                           as n_regions,
    count(distinct "年齢5歳階級_code")                              as n_age_groups,
    count(distinct "男女別_code")                                   as n_sex,
    count(distinct "時間軸（年月日現在）_code")                     as n_years,
    listagg(distinct "時間軸（年月日現在）_code", ',')
        within group (order by "時間軸（年月日現在）_code")         as year_codes,
    listagg(distinct "男女別_code", ',')
        within group (order by "男女別_code")                       as sex_codes,
    count(case when try_to_number("value") is null
               and "value" is not null then 1 end)                  as non_numeric_values,
    count(*)                                                        as total_rows
from {{ source('raw', 'POPULATION_ESTIMATE') }}
