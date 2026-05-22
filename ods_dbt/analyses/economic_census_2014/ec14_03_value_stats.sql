-- value の数値変換確認・非数値チェック
select
    count(*)                                                    as total_rows,
    count(case when "value" is null then 1 end)                 as null_values,
    count(case when try_to_number("value") is null
               and "value" is not null then 1 end)              as non_numeric_values,
    min(try_to_number("value"))                                 as min_value,
    max(try_to_number("value"))                                 as max_value,
    count(distinct "時間軸_code")                               as n_time_codes,
    min("時間軸_code")                                          as time_code_sample
from {{ source('raw', 'ECONOMIC_CENSUS_2014') }}
