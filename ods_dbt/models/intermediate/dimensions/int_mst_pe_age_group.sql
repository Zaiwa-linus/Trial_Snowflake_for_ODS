select distinct
    age_group_code,
    age_group_name,
    age_group_code = '01000' as is_aggregate
from {{ ref('stg_population_estimate') }}
order by age_group_code
