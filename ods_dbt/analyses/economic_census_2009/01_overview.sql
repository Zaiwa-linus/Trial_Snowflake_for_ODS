-- 経済センサス2009 RAW テーブル全体概要
-- 行数・各ディメンションのカーディナリティ・VALUE の数値範囲を確認する
select
    count(*)                                                   as total_rows,
    count(distinct metric_code)                                as n_metrics,
    count(distinct industry_code)                              as n_industries,
    count(distinct org_type_code)                              as n_org_types,
    count(distinct emp_size_code)                              as n_emp_sizes,
    count(distinct area_code)                                  as n_areas,
    count(distinct time_code)                                  as n_time_points,
    count(case when value is null then 1 end)                  as null_values,
    count(case when try_to_number(value) is null
               and value is not null then 1 end)               as non_numeric_values,
    min(try_to_number(value))                                  as min_value,
    max(try_to_number(value))                                  as max_value
from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
