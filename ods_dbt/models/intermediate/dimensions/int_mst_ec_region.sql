with ec09 as (
    select distinct region_code, region_name
    from {{ ref('stg_economic_census_2009') }}
),

ec14 as (
    select distinct region_code, region_name
    from {{ ref('stg_economic_census_2014') }}
),

combined as (
    select region_code, region_name from ec09
    union
    select region_code, region_name from ec14
),

-- 同一コードで表記揺れがある場合は2014の名称を優先
deduped as (
    select region_code, region_name
    from combined
    qualify row_number() over (
        partition by region_code
        order by case when region_name in (select region_name from ec14) then 0 else 1 end
    ) = 1
)

select
    region_code,
    region_name,
    case
        when region_code = '00000'          then '全国'
        when region_code like '002%'        then '大都市圏'
        when right(region_code, 3) = '000'  then '都道府県'
        else                                 '政令市等'
    end                                     as region_type,
    left(region_code, 2)                    as pref_code
from deduped
order by region_code
