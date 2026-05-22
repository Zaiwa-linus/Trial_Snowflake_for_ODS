"""
e-Stat CSVをSnowflakeのODS_TRIAL.RAWへロードするスクリプト。

前提とする環境変数は docs/env_vars.md を参照。

実行方法:
    uv run --with snowflake-connector-python python scripts/load_estat_to_snowflake.py

ブラウザが開いてSSOログインを求められます。
"""

import os
import sys
from pathlib import Path

import snowflake.connector


def _require(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        print(f"エラー: 環境変数 {name} が設定されていません（docs/env_vars.md 参照）", file=sys.stderr)
        sys.exit(1)
    return v


ACCOUNT   = _require("SNOWFLAKE_ACCOUNT")
USER      = _require("SNOWFLAKE_USER")
PASSWORD  = _require("SNOWFLAKE_PASSWORD")
WAREHOUSE = os.environ.get("SNOWFLAKE_WAREHOUSE", "WH_DBT_TRIAL")
DATABASE  = os.environ.get("SNOWFLAKE_DATABASE", "ODS_TRIAL")
SCHEMA    = os.environ.get("SNOWFLAKE_SCHEMA",   "RAW")
TABLE     = "ECONOMIC_CENSUS_2009"

CSV_PATH = Path(__file__).parent.parent / "data" / "0003032544" / "0003032544.csv"


def run(cur, sql: str, label: str = "") -> list:
    if label:
        print(f"  → {label}")
    cur.execute(sql)
    return cur.fetchall()


def main():
    if not CSV_PATH.exists():
        print(f"CSVが見つかりません: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    print("Snowflakeに接続中（ブラウザが開きます）...")
    conn = snowflake.connector.connect(
        account=ACCOUNT,
        user=USER,
        password=PASSWORD,
        role="ACCOUNTADMIN",
    )
    cur = conn.cursor()

    try:
        print("\n[1/5] Warehouse / Database / Schema を作成")
        run(cur, f"""
            CREATE WAREHOUSE IF NOT EXISTS {WAREHOUSE}
            WITH WAREHOUSE_SIZE = 'XSMALL'
                 AUTO_SUSPEND   = 60
                 AUTO_RESUME    = TRUE
        """, f"CREATE WAREHOUSE {WAREHOUSE}")
        run(cur, f"USE WAREHOUSE {WAREHOUSE}")
        run(cur, f"CREATE DATABASE IF NOT EXISTS {DATABASE}", f"CREATE DATABASE {DATABASE}")
        run(cur, f"USE DATABASE {DATABASE}")
        run(cur, f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}", f"CREATE SCHEMA {SCHEMA}")
        run(cur, f"USE SCHEMA {SCHEMA}")

        print("\n[2/5] テーブルを作成")
        run(cur, f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                METRIC_CODE    VARCHAR COMMENT '表章項目コード',
                METRIC_NAME    VARCHAR COMMENT '表章項目名',
                INDUSTRY_CODE  VARCHAR COMMENT '産業分類コード（H21中分類）',
                INDUSTRY_NAME  VARCHAR COMMENT '産業分類名',
                ORG_TYPE_CODE  VARCHAR COMMENT '経営組織コード（5区分）',
                ORG_TYPE_NAME  VARCHAR COMMENT '経営組織名',
                EMP_SIZE_CODE  VARCHAR COMMENT '従業者規模コード（13区分）',
                EMP_SIZE_NAME  VARCHAR COMMENT '従業者規模名',
                AREA_CODE      VARCHAR COMMENT '地域コード（全国/都道府県/19大都市/14大都市圏）',
                AREA_NAME      VARCHAR COMMENT '地域名',
                TIME_CODE      VARCHAR COMMENT '時間軸コード',
                TIME_NAME      VARCHAR COMMENT '時間軸名',
                UNIT           VARCHAR COMMENT '単位',
                VALUE          VARCHAR COMMENT '値'
            )
            COMMENT = '経済センサス‐基礎調査2009 産業×従業者規模×経営組織×事業所数・従業者数（e-Stat: 0003032544）'
        """, f"CREATE TABLE {TABLE}")

        print("\n[3/5] 内部ステージを作成")
        run(cur, "CREATE STAGE IF NOT EXISTS ESTAT_STAGE", "CREATE STAGE ESTAT_STAGE")

        print(f"\n[4/5] CSVをアップロード中（{CSV_PATH.stat().st_size / 1e6:.0f}MB）...")
        rows = run(cur, f"PUT file://{CSV_PATH} @ESTAT_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        status = rows[0][6] if rows else "?"
        print(f"  → {status}")

        print(f"\n[5/5] COPY INTO {TABLE} ...")
        rows = run(cur, f"""
            COPY INTO {TABLE}
            FROM @ESTAT_STAGE/{CSV_PATH.name}.gz
            FILE_FORMAT = (
                TYPE                        = CSV
                SKIP_HEADER                 = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                ENCODING                    = 'UTF-8'
                EMPTY_FIELD_AS_NULL         = TRUE
            )
        """)
        for r in rows:
            print(f"  ファイル: {r[0]}  ロード: {r[1]}件  エラー: {r[2]}件  ステータス: {r[5]}")

        # 確認
        count = run(cur, f"SELECT COUNT(*) FROM {TABLE}")[0][0]
        print(f"\n完了: {DATABASE}.{SCHEMA}.{TABLE} に {count:,} 件登録されました")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
