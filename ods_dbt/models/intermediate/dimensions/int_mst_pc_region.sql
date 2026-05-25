select distinct
    region_code,
    region_name,
    case
        when region_code = '00000'              then '全国'
        when region_code in ('00001', '00002')  then '全国市郡部'
        when right(region_code, 3) = '000'      then '都道府県'
        when right(region_code, 3) = '001'      then '都道府県市部'
        else                                     '政令市等'
    end                                         as region_type,
    case
        when left(region_code, 2) = '00'        then null
        else left(region_code, 2)
    end                                         as pref_code
from {{ ref('stg_population_census_2010') }}
order by region_code
