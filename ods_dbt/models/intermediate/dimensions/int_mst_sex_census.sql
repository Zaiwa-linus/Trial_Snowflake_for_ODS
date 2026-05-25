-- 国勢調査・人口推計共通の性別コード（000/001/002体系）
select distinct
    sex_code,
    sex_name,
    sex_code = '000' as is_aggregate
from {{ ref('stg_population_estimate') }}
order by sex_code
