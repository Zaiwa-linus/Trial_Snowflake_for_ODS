#!/usr/bin/env python3
"""
dbt artifacts を読み込み、Snowflake の DATA_CATALOG スキーマに
Data Product メタデータを投入するスクリプト。

使い方:
    uv run python scripts/export_dbt_artifacts_to_catalog.py

前提条件:
    - ods_dbt/target/ に manifest.json が存在すること（dbt build / dbt compile 後）
    - catalog.json は dbt docs generate 後に生成される（任意）
    - run_results.json は dbt build / dbt test 後に生成される（任意）
    - 環境変数 SNOWFLAKE_* が設定されていること（docs/env_vars.md 参照）
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import snowflake.connector


def get_conn() -> snowflake.connector.SnowflakeConnection:
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "WH_DBT_TRIAL"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "ODS_TRIAL"),
        schema="DATA_CATALOG",
    )


def ensure_tables(cur) -> None:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS DATA_PRODUCTS (
            product_id          STRING,
            dbt_model_name      STRING,
            snowflake_database  STRING,
            snowflake_schema    STRING,
            snowflake_object    STRING,
            product_name        STRING,
            domain              STRING,
            owner_team          STRING,
            description         STRING,
            materialization     STRING,
            freshness_sla       STRING,
            lifecycle_status    STRING,
            version             STRING,
            dbt_unique_id       STRING,
            updated_at          TIMESTAMP_NTZ
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS DATA_PRODUCT_COLUMNS (
            product_id       STRING,
            dbt_model_name   STRING,
            column_name      STRING,
            data_type        STRING,
            business_name    STRING,
            description      STRING,
            concept_uri      STRING,
            unit             STRING,
            privacy_category STRING,
            tests            ARRAY,
            updated_at       TIMESTAMP_NTZ
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS QUALITY_RESULTS (
            product_id      STRING,
            object_name     STRING,
            metric_name     STRING,
            metric_value    FLOAT,
            threshold_value FLOAT,
            status          STRING,
            measured_at     TIMESTAMP_NTZ
        )
    """)


def load_artifacts(target_dir: Path) -> tuple[dict, dict, dict]:
    manifest_path = target_dir / "manifest.json"
    catalog_path = target_dir / "catalog.json"
    run_results_path = target_dir / "run_results.json"

    if not manifest_path.exists():
        raise FileNotFoundError(
            f"manifest.json が見つかりません: {manifest_path}\n"
            "先に `uv run dbt build --project-dir ods_dbt --profiles-dir ods_dbt` を実行してください"
        )

    manifest = json.loads(manifest_path.read_text())
    catalog = json.loads(catalog_path.read_text()) if catalog_path.exists() else {}
    run_results = json.loads(run_results_path.read_text()) if run_results_path.exists() else {}

    return manifest, catalog, run_results


def build_column_test_map(nodes: dict) -> dict[str, dict[str, list[str]]]:
    """
    テストノードからモデル名→カラム名→テスト名リストのマッピングを構築する。
    戻り値: {model_name: {column_name: [test_name, ...]}}
    """
    mapping: dict[str, dict[str, list[str]]] = {}
    for node_id, node in nodes.items():
        if node.get("resource_type") != "test":
            continue
        test_meta = node.get("test_metadata", {})
        kwargs = test_meta.get("kwargs", {})
        col_name = kwargs.get("column_name", "")
        model_ref = kwargs.get("model", "")
        if not (col_name and model_ref):
            continue
        match = re.search(r"ref\(['\"]([^'\"]+)['\"]\)", model_ref)
        if not match:
            continue
        model_name = match.group(1)
        test_name = test_meta.get("name", node.get("name", ""))
        mapping.setdefault(model_name, {}).setdefault(col_name, []).append(test_name)
    return mapping


def upsert_products(cur, manifest: dict, catalog: dict, now: datetime) -> int:
    nodes = manifest.get("nodes", {})
    catalog_nodes = catalog.get("nodes", {})

    cur.execute("DELETE FROM DATA_PRODUCTS")

    rows = []
    for node_id, node in nodes.items():
        if node.get("resource_type") != "model":
            continue

        meta = node.get("meta", {})
        config = node.get("config", {})
        cat_meta = catalog_nodes.get(node_id, {}).get("metadata", {})

        rows.append((
            meta.get("data_product_id") or node["name"],
            node["name"],
            cat_meta.get("database") or os.environ.get("SNOWFLAKE_DATABASE", "ODS_TRIAL"),
            cat_meta.get("schema") or config.get("schema", ""),
            cat_meta.get("name") or node["name"].upper(),
            meta.get("business_name") or node["name"],
            meta.get("domain", ""),
            meta.get("owner_team", ""),
            node.get("description", ""),
            config.get("materialized", ""),
            meta.get("freshness_sla", ""),
            meta.get("lifecycle_status", ""),
            str(node.get("version") or ""),
            node_id,
            now,
        ))

    if rows:
        cur.executemany(
            "INSERT INTO DATA_PRODUCTS VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            rows,
        )

    return len(rows)


def upsert_columns(cur, manifest: dict, catalog: dict, now: datetime) -> int:
    nodes = manifest.get("nodes", {})
    catalog_nodes = catalog.get("nodes", {})
    col_test_map = build_column_test_map(nodes)

    cur.execute("DELETE FROM DATA_PRODUCT_COLUMNS")

    rows = []
    for node_id, node in nodes.items():
        if node.get("resource_type") != "model":
            continue

        meta = node.get("meta", {})
        product_id = meta.get("data_product_id") or node["name"]
        model_name = node["name"]
        manifest_cols = node.get("columns", {})
        cat_cols = catalog_nodes.get(node_id, {}).get("columns", {})
        tests_for_model = col_test_map.get(model_name, {})

        for col_name, col in manifest_cols.items():
            col_meta = col.get("meta", {})
            cat_col = cat_cols.get(col_name.upper(), {})
            test_names = tests_for_model.get(col_name, [])

            rows.append((
                product_id,
                model_name,
                col_name,
                cat_col.get("type") or col.get("data_type", ""),
                col_meta.get("business_name", ""),
                col.get("description", ""),
                col_meta.get("concept_uri", ""),
                col_meta.get("unit", ""),
                col_meta.get("privacy_category", ""),
                json.dumps(test_names, ensure_ascii=False),
                now,
            ))

    if rows:
        cur.executemany(
            "INSERT INTO DATA_PRODUCT_COLUMNS VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,PARSE_JSON(%s),%s)",
            rows,
        )

    return len(rows)


def upsert_quality_results(cur, run_results: dict, manifest: dict, now: datetime) -> int:
    results = run_results.get("results", [])
    nodes = manifest.get("nodes", {})

    test_results = [r for r in results if r.get("unique_id", "").startswith("test.")]
    if not test_results:
        return 0

    # モデル名→product_id のマッピングを事前構築
    model_to_product: dict[str, str] = {}
    for node_id, node in nodes.items():
        if node.get("resource_type") == "model":
            m = node.get("meta", {})
            model_to_product[node["name"]] = m.get("data_product_id") or node["name"]

    cur.execute("DELETE FROM QUALITY_RESULTS")

    rows = []
    for result in test_results:
        unique_id = result.get("unique_id", "")
        test_node = nodes.get(unique_id, {})
        refs = test_node.get("refs", [])
        model_name = refs[0].get("name", "") if refs else ""
        product_id = model_to_product.get(model_name, model_name)
        status = result.get("status", "")

        rows.append((
            product_id,
            model_name,
            test_node.get("name") or unique_id,
            float(result.get("failures") or 0),
            0.0,
            "pass" if status == "pass" else "fail",
            now,
        ))

    if rows:
        cur.executemany(
            "INSERT INTO QUALITY_RESULTS VALUES (%s,%s,%s,%s,%s,%s,%s)",
            rows,
        )

    return len(rows)


def main() -> None:
    target_dir = Path("ods_dbt/target")

    print("dbt artifacts 読み込み中...")
    try:
        manifest, catalog, run_results = load_artifacts(target_dir)
    except FileNotFoundError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    dbt_version = manifest.get("metadata", {}).get("dbt_version", "不明")
    n_nodes = len(manifest.get("nodes", {}))
    print(f"  dbt バージョン: {dbt_version} / ノード数: {n_nodes}")
    if not catalog:
        print("  catalog.json なし（dbt docs generate を実行すると Snowflake 上の型情報を取得できます）")
    if not run_results:
        print("  run_results.json なし（品質結果は登録されません）")

    print("Snowflake に接続中...")
    conn = get_conn()
    cur = conn.cursor()

    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        print("DATA_CATALOG テーブルを確認・作成中...")
        ensure_tables(cur)

        print("DATA_PRODUCTS を更新中...")
        n_products = upsert_products(cur, manifest, catalog, now)
        print(f"  {n_products} モデルを登録")

        print("DATA_PRODUCT_COLUMNS を更新中...")
        n_cols = upsert_columns(cur, manifest, catalog, now)
        print(f"  {n_cols} カラムを登録")

        print("QUALITY_RESULTS を更新中...")
        n_tests = upsert_quality_results(cur, run_results, manifest, now)
        print(f"  {n_tests} テスト結果を登録")

        conn.commit()
        print("完了")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
