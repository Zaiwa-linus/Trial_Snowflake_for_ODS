with source as (
    select * from {{ source('raw', 'POPULATION_ESTIMATE') }}
),

renamed as (
    select
        "全国・都道府県_code"                    as region_code,
        "全国・都道府県"                         as region_name,
        "年齢5歳階級_code"                       as age_group_code,
        "年齢5歳階級"                            as age_group_name,
        "男女別_code"                            as sex_code,
        "男女別"                                 as sex_name,

        -- 表章項目_code/表章項目 は全行 001/'人口' の定数なので除去
        -- 時間軸（年月日現在）_code は '2005'〜'2009' の4桁文字列
        "時間軸（年月日現在）_code"::integer     as survey_year,

        -- unit は '千人'（定数）なので除去
        try_to_number("value")                  as value
    from source
)

select * from renamed
