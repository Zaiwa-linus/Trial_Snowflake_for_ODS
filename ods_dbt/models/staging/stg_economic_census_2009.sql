with source as (
    select * from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
),

renamed as (
    select
        -- ディメンション：コード類はゼロパディングがあるため varchar のまま維持
        metric_code                          as measure_code,
        metric_name                          as measure_name,
        industry_code,
        industry_name,
        org_type_code,
        org_type_name,
        emp_size_code                        as employee_size_code,
        emp_size_name                        as employee_size_name,
        area_code                            as region_code,
        area_name                            as region_name,

        -- 時間軸：全行 '2009000000' の定数なので年（integer）に圧縮
        left(time_code, 4)::integer          as survey_year,

        -- 指標値：RAW は varchar だが全行数値変換可能
        try_to_number(value)                 as value
    from source
)

select * from renamed
