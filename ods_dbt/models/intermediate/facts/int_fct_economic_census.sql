with ec09 as (
    select
        survey_year,
        '2009'             as source_survey,
        measure_code,
        industry_code,
        org_type_code,
        employee_size_code,
        region_code,
        value
    from {{ ref('stg_economic_census_2009') }}
    where
        -- 産業：大分類（1文字アルファベット）および集計行を除外し中分類のみ残す
        not regexp_like(industry_code, '^[A-Z]$')
        and industry_code not in ('000', '001', '002', '026', '027')
        -- 経営組織：総数(000)・民営集計(001)・法人集計(003)を除外
        and org_type_code not in ('000', '001', '003')
        -- 従業者規模：総数(000)・1-4人合計(001=002+003+004+005)を除外
        -- 2009では001が1-4人の集計行（2014の005に相当）
        and employee_size_code not in ('000', '001')
        -- 地域：全国集計を除外
        and region_code != '00000'
),

ec14 as (
    select
        survey_year,
        '2014'             as source_survey,
        measure_code,
        industry_code,
        org_type_code,
        employee_size_code,
        region_code,
        value
    from {{ ref('stg_economic_census_2014') }}
    where
        -- 産業：大分類（1文字アルファベット）および全産業集計行(000)を除外
        not regexp_like(industry_code, '^[A-Z]$')
        and industry_code != '000'
        -- 経営組織：総数(000)・民営集計(007)・法人集計(009)を除外
        and org_type_code not in ('000', '007', '009')
        -- 従業者規模：総数(000)・1-4人合計(005)を除外
        and employee_size_code not in ('000', '005')
        -- 地域：全国集計を除外
        and region_code != '00000'
)

select * from ec09
union all
select * from ec14
