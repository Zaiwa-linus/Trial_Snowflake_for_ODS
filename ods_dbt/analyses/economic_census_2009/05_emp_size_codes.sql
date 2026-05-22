-- 従業者規模13区分（EMP_SIZE）の保有値一覧
-- 15種類（000=総数、001-004=個人単位、005-013=規模帯、014=派遣のみ）。
-- 001-004(1人/2人/3人/4人) と 005(1～4人) は重複集計に注意。
select
    emp_size_code,
    emp_size_name,
    count(*) as row_count
from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
group by emp_size_code, emp_size_name
order by try_to_number(emp_size_code)
