-- 2009年の従業者規模コード体系は2014と異なる
-- 001=1〜4人合計 / 002=1人 / 003=2人 / 004=3人 / 005=4人 / ...
select distinct
    employee_size_code,
    employee_size_name,
    -- 000=総数、001=1-4人合計（002+003+004+005の集計）は集計行
    employee_size_code in ('000', '001') as is_aggregate
from {{ ref('stg_economic_census_2009') }}
order by try_to_number(employee_size_code)
