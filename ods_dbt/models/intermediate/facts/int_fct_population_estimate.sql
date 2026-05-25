select
    survey_year,
    region_code,
    age_group_code,
    sex_code,
    value
from {{ ref('stg_population_estimate') }}
where
    -- 性別：男女計(000)を除外
    sex_code != '000'
    -- 年齢：総数(01000)を除外
    and age_group_code != '01000'
    -- 地域：全国(00000)を除外
    and region_code != '00000'
