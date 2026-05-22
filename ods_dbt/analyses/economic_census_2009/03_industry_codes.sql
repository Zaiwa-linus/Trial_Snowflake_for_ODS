-- 産業分類（INDUSTRY）の保有値一覧
-- 121種類。大分類(A-S)と中分類(数値コード)が混在する階層構造。
-- code=000,001,002 は全産業・農林漁業等の集計行。
-- 大分類コード（アルファベット1文字から始まる名称）と中分類（数値から始まる名称）が混在。
select
    industry_code,
    industry_name,
    case
        when industry_name like '[A-Z]%'   then '大分類'
        when industry_code in ('000','001','002','026','027') then '集計行'
        else '中分類'
    end as hierarchy,
    count(*) as row_count
from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
group by industry_code, industry_name
order by industry_code
