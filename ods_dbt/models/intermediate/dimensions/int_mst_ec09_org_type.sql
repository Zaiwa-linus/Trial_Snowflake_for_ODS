-- 経済センサス2009の経営組織区分
-- 階層: 000(総数) > 001(民営) > 002(個人)/003(法人) > 004(会社)/005(会社以外)
select distinct
    org_type_code,
    org_type_name,
    case
        when org_type_code = '000'              then '総数'
        when org_type_code in ('001', '003')    then '中間集計'
        else                                     '最細粒度'
    end as org_type_level
from {{ ref('stg_economic_census_2009') }}
order by org_type_code
