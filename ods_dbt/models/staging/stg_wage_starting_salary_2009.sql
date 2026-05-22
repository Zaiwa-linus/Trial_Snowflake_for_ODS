with source as (
    select * from {{ source('raw', 'WAGE_STARTING_SALARY_2009') }}
),

renamed as (
    select
        "産業分類_code"                          as industry_code,
        "産業分類"                               as industry_name,
        "都道府県_基本_code"                     as prefecture_code,
        "都道府県_基本"                          as prefecture_name,
        "企業規模_4区分_code"                    as company_size_code,
        "企業規模_4区分"                         as company_size_name,
        "性別_基本の3区分_code"                  as sex_code,
        "性別_基本の3区分"                       as sex_name,
        "学歴_5区分_code"                        as education_code,
        "学歴_5区分"                             as education_name,

        -- 初任給額の区分_基本_code/基本 は全行 01/'確定' の定数なので除去
        -- 地域_code/地域 は全行 00000/'全国' の定数なので除去
        left("時間軸（年）_code", 4)::integer    as survey_year,

        -- unit は '千円'（定数）なので除去
        -- '-' が存在するため try_to_number で欠損扱いに変換
        try_to_number("value")                  as value
    from source
)

select * from renamed
