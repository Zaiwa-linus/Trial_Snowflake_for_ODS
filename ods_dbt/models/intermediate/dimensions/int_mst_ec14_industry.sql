select distinct
    industry_code,
    industry_name,
    case
        when regexp_like(industry_code, '^[A-Z]$')  then '大分類'
        when industry_code = '000'                   then '集計行'
        else                                          '中分類'
    end as industry_level
from {{ ref('stg_economic_census_2014') }}
order by industry_code
