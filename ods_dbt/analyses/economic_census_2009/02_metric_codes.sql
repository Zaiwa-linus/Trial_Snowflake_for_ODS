-- 表章項目（METRIC）の保有値一覧
-- 8種類の指標。003=事業所数、004-006=従業者数(総/男/女)、007-009=常用雇用者(総/男/女)、019=1事業所当たり従業者数
select
    metric_code,
    metric_name,
    count(*) as row_count
from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
group by metric_code, metric_name
order by metric_code
