-- 経営組織5区分（ORG_TYPE）の保有値一覧
-- 6種類（000=総数 を含む）。000>001(民営)>002(個人)/003(法人)>004(会社)/005(会社以外) の包含関係。
select
    org_type_code,
    org_type_name,
    count(*) as row_count
from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
group by org_type_code, org_type_name
order by org_type_code
