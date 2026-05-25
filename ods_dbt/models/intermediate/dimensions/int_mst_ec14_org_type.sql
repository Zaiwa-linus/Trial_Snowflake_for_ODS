-- 経済センサス2014の経営組織区分（H26基準）
-- 階層: 000(総数) > 007(民営) > 008(個人)/009(法人) > 010(会社)/011(会社以外)/016(法人でない団体)
select distinct
    org_type_code,
    org_type_name,
    case
        when org_type_code = '000'              then '総数'
        when org_type_code in ('007', '009')    then '中間集計'
        else                                     '最細粒度'
    end as org_type_level
from {{ ref('stg_economic_census_2014') }}
order by org_type_code
