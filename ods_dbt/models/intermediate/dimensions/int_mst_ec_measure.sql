-- 経済センサス2009と2014で表章項目コード体系が異なるためsurvey_yearで区別
with ec09 as (
    select distinct measure_code, measure_name, 2009 as survey_year
    from {{ ref('stg_economic_census_2009') }}
),

ec14 as (
    select distinct measure_code, measure_name, 2014 as survey_year
    from {{ ref('stg_economic_census_2014') }}
)

select * from ec09
union all
select * from ec14
order by survey_year, measure_code
