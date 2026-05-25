select distinct
    employment_status_code,
    employment_status_name,
    employment_status_code = '000' as is_aggregate
from {{ ref('stg_population_census_2010') }}
order by employment_status_code
