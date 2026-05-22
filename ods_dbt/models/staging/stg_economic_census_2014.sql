with source as (
    select * from {{ source('raw', 'ECONOMIC_CENSUS_2014') }}
),

renamed as (
    select
        "表章項目_code"                       as measure_code,
        "表章項目"                            as measure_name,
        "H26_産業分類_code"                   as industry_code,
        "H26_産業分類"                        as industry_name,
        "H26_従業者規模_code"                 as employee_size_code,
        "H26_従業者規模"                      as employee_size_name,
        "H26_経営組織5区分_code"              as org_type_code,
        "H26_経営組織5区分"                   as org_type_name,
        "H26_地域_code"                       as region_code,
        "H26_地域"                            as region_name,

        left("時間軸_code", 4)::integer       as survey_year,

        try_to_number("value")               as value
    from source
)

select * from renamed
