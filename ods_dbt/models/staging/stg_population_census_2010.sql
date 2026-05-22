with source as (
    select * from {{ source('raw', 'POPULATION_CENSUS_2010') }}
),

renamed as (
    select
        "産業分類2010_code"                      as industry_code,
        "産業分類2010"                           as industry_name,
        "従業上の地位2010_code"                  as employment_status_code,
        "従業上の地位2010"                       as employment_status_name,
        "男女別2010_code"                        as sex_code,
        "男女別2010"                             as sex_name,
        "地域（2010）_code"                      as region_code,
        "地域（2010）"                           as region_name,

        -- 表章項目_code/表章項目 は全行 340/'15歳以上就業者数' の定数なので除去
        left("時間軸（年次）_code", 4)::integer  as survey_year,

        -- '-' が存在するため try_to_number で欠損扱いに変換
        try_to_number("value")                  as value
    from source
)

select * from renamed
