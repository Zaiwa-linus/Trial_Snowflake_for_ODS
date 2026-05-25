select distinct
    region_code,
    region_name,
    case
        when region_code = '00000'  then '全国'
        else                         '都道府県'
    end as region_type
from {{ ref('stg_population_estimate') }}
order by region_code
