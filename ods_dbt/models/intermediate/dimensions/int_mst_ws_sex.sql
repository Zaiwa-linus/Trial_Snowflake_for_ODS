-- 賃金調査固有の性別コード（01/02/03体系）。国勢調査系(000/001/002)とは別体系
select distinct
    sex_code,
    sex_name,
    -- 01=男女計
    sex_code = '01' as is_aggregate
from {{ ref('stg_wage_starting_salary_2009') }}
order by sex_code
