-- カラム名・サンプル値・value の数値変換確認
select
    "表章項目_code",
    "表章項目",
    "H26_産業分類_code",
    "H26_従業者規模_code",
    "H26_経営組織5区分_code",
    "H26_地域_code",
    left("時間軸_code", 4)                      as survey_year_str,
    "value",
    try_to_number("value")                      as value_num
from {{ source('raw', 'ECONOMIC_CENSUS_2014') }}
qualify row_number() over (order by 1) <= 5
