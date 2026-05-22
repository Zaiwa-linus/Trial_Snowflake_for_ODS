-- 経済センサス2014 RAW テーブル全体概要
select
    count(*)                                                        as total_rows,
    count(distinct "表章項目_code")                                 as n_measures,
    count(distinct "H26_産業分類_code")                             as n_industries,
    count(distinct "H26_従業者規模_code")                           as n_emp_sizes,
    count(distinct "H26_経営組織5区分_code")                        as n_org_types,
    count(distinct "H26_地域_code")                                 as n_regions,
    count(distinct "時間軸_code")                                   as n_time_points,
    count(case when "value" is null then 1 end)                     as null_values,
    count(case when try_to_number("value") is null
               and "value" is not null then 1 end)                  as non_numeric_values,
    min(try_to_number("value"))                                     as min_value,
    max(try_to_number("value"))                                     as max_value
from {{ source('raw', 'ECONOMIC_CENSUS_2014') }}
