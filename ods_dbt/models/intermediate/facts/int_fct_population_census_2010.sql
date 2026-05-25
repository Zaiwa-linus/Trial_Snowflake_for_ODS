select
    survey_year,
    industry_code,
    employment_status_code,
    sex_code,
    region_code,
    value
from {{ ref('stg_population_census_2010') }}
where
    -- 産業：大分類（1文字アルファベット）および総数(000)を除外し中分類のみ残す
    not regexp_like(industry_code, '^[A-Z]$')
    and industry_code != '000'
    -- 従業上の地位：総数(000)を除外
    and employment_status_code != '000'
    -- 性別：総数(000)を除外
    and sex_code != '000'
    -- 地域：全国(00000)・全国市部(00001)・全国郡部(00002)を除外
    and region_code not in ('00000', '00001', '00002')
