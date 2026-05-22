"""
e-Stat CSVを汎用的にSnowflakeのODS_TRIAL.RAWへロードするスクリプト。
CSV列名をそのままSnowflakeのカラム名として使用する。

前提とする環境変数は docs/env_vars.md を参照。

実行方法:
    uv run python scripts/load_estat_to_snowflake_generic.py <stats_data_id> <table_name>

例:
    uv run python scripts/load_estat_to_snowflake_generic.py 0003111060 ECONOMIC_CENSUS_2014
"""

import csv
import os
import sys
from pathlib import Path

import snowflake.connector

PROJECT_ROOT = Path(__file__).parent.parent


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


def run(cur, sql: str, label: str = "") -> list:
    if label:
        print(f"  → {label}")
    cur.execute(sql)
    return cur.fetchall()


def main():
    if len(sys.argv) < 3:
        print("Usage: python load_estat_to_snowflake_generic.py <stats_data_id> <table_name>")
        sys.exit(1)

    stats_id   = sys.argv[1]
    table_name = sys.argv[2].upper()
    csv_path   = PROJECT_ROOT / "data" / stats_id / f"{stats_id}.csv"

    if not csv_path.exists():
        print(f"CSVが見つかりません: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # CSVヘッダーを読み込む
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)

    print(f"統計表ID : {stats_id}")
    print(f"テーブル  : {DATABASE}.{SCHEMA}.{table_name}")
    print(f"列数      : {len(headers)}")
    print(f"列名      : {headers}")

    # 列定義（日本語列名はダブルクォートで囲む）
    cols_ddl = ",\n                ".join(
        f'"{h.strip()}" VARCHAR' for h in headers
    )

    print("\nSnowflakeに接続中...")
    conn = snowflake.connector.connect(
        account=ACCOUNT,
        user=USER,
        password=PASSWORD,
        role="ACCOUNTADMIN",
    )
    cur = conn.cursor()

    try:
        print("\n[1/5] Warehouse / Database / Schema を確認")
        run(cur, f"CREATE WAREHOUSE IF NOT EXISTS {WAREHOUSE} WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE", f"WAREHOUSE {WAREHOUSE}")
        run(cur, f"USE WAREHOUSE {WAREHOUSE}")
        run(cur, f"CREATE DATABASE IF NOT EXISTS {DATABASE}", f"DATABASE {DATABASE}")
        run(cur, f"USE DATABASE {DATABASE}")
        run(cur, f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}", f"SCHEMA {SCHEMA}")
        run(cur, f"USE SCHEMA {SCHEMA}")

        print("\n[2/5] テーブルを作成（CREATE OR REPLACE）")
        run(cur, f"""
            CREATE OR REPLACE TABLE {table_name} (
                {cols_ddl}
            )
            COMMENT = 'e-Stat 統計表ID: {stats_id}'
        """, f"CREATE TABLE {table_name}")

        print("\n[3/5] 内部ステージを確認")
        run(cur, "CREATE STAGE IF NOT EXISTS ESTAT_STAGE", "STAGE ESTAT_STAGE")

        print(f"\n[4/5] CSVをアップロード中（{csv_path.stat().st_size / 1e6:.0f}MB）...")
        rows = run(cur, f"PUT file://{csv_path} @ESTAT_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        status = rows[0][6] if rows else "?"
        print(f"  → {status}")

        print(f"\n[5/5] COPY INTO {table_name} ...")
        rows = run(cur, f"""
            COPY INTO {table_name}
            FROM @ESTAT_STAGE/{csv_path.name}.gz
            FILE_FORMAT = (
                TYPE                         = CSV
                SKIP_HEADER                  = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                ENCODING                     = 'UTF-8'
                EMPTY_FIELD_AS_NULL          = TRUE
            )
        """)
        for r in rows:
            print(f"  ファイル: {r[0]}  ステータス: {r[1]}  ロード: {r[3]:,}件  エラー: {r[5]}件")

        count = run(cur, f"SELECT COUNT(*) FROM {table_name}")[0][0]
        print(f"\n完了: {DATABASE}.{SCHEMA}.{table_name} に {count:,} 件登録されました")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
