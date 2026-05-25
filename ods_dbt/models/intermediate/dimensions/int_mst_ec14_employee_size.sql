-- 2014年の従業者規模コード体系は2009と異なる
-- 001=1人 / 002=2人 / 003=3人 / 004=4人 / 005=1〜4人合計 / 006=5〜9人 / ...
select distinct
    employee_size_code,
    employee_size_name,
    -- 000=総数、005=1-4人合計（001+002+003+004の集計）は集計行
    employee_size_code in ('000', '005') as is_aggregate
from {{ ref('stg_economic_census_2014') }}
order by try_to_number(employee_size_code)
