-- 地域区分（AREA）の保有値一覧と地域種別の分類
-- 81種類。コード体系:
--   00000          = 全国
--   002XX          = 大都市圏（14圏）
--   XX000 (XX=01-47)= 都道府県
--   XX1NN          = 政令指定都市・特別区（19大都市）
select
    area_code,
    area_name,
    case
        when area_code = '00000'              then '全国'
        when area_code like '002%'            then '大都市圏'
        when right(area_code, 3) = '000'      then '都道府県'
        else                                       '大都市'
    end                                       as area_type,
    left(area_code, 2)                        as pref_code,
    count(*)                                  as row_count
from {{ source('raw', 'ECONOMIC_CENSUS_2009') }}
group by area_code, area_name
order by area_code
