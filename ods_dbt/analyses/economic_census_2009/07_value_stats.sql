-- VALUE列の統計：指標種別ごとの分布
-- 全行が数値変換可能（non_numeric=0 を確認）。
-- 019（1事業所当たり従業者数）は小数あり・桁数が他と異なる点に注意。
select
    metric_code,
    metric_name,
    count(*)                       as row_count,
    min(try_to_number(value))      as min_val,
    max(try_to_number(value))      as max_val,
    avg(try_to_number(value))      as avg_val,
    median(try_to_number(value))   as median_val,
    count(case when value = '0' then 1 end) as zero_count,
    count(case when try_to_number(value) is null then 1 end) as non_numeric_count
from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
group by metric_code, metric_name
order by metric_code
