"""e-Stat API で統計表のメタ情報（分類軸・コード一覧）を取得するスクリプト。

使い方:
  uv run python scripts/get_meta.py 0003317252
  uv run python scripts/get_meta.py 0003317252 --json
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo"
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def get_app_id() -> str:
    for key in ("ESTAT_API_KEY", "ESTAT_API_APPID"):
        val = os.environ.get(key)
        if val:
            return val
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                for prefix in ("ESTAT_API_KEY=", "ESTAT_API_APPID="):
                    if line.startswith(prefix):
                        return line[len(prefix):].strip().strip('"').strip("'")
    print("エラー: ESTAT_API_KEY が設定されていません。", file=sys.stderr)
    print("  export ESTAT_API_KEY='あなたのAppID'", file=sys.stderr)
    sys.exit(1)


def fetch_meta(stats_data_id: str) -> dict:
    params = {
        "appId": get_app_id(),
        "lang": "J",
        "statsDataId": stats_data_id,
        "explanationGetFlg": "Y",
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def print_meta(data: dict) -> None:
    root = data.get("GET_META_INFO", {})
    result = root.get("RESULT", {})

    if result.get("STATUS") != 0:
        print(f"エラー: {result.get('ERROR_MSG')}", file=sys.stderr)
        sys.exit(1)

    metadata = root.get("METADATA_INF", {})
    table = metadata.get("TABLE_INF", {})

    stat_name = table.get("STAT_NAME", {})
    if isinstance(stat_name, dict):
        stat_name = stat_name.get("$", str(stat_name))

    title = table.get("TITLE", "")
    if isinstance(title, dict):
        title = title.get("$", str(title))

    gov_org = table.get("GOV_ORG", {})
    if isinstance(gov_org, dict):
        gov_org = gov_org.get("$", str(gov_org))

    print(f"\n{'=' * 80}")
    print(f"統計表ID:   {table.get('@id', '')}")
    print(f"統計名:     {stat_name}")
    print(f"タイトル:   {title}")
    print(f"提供機関:   {gov_org}")
    print(f"周期:       {table.get('CYCLE', '-')}")
    print(f"調査日:     {table.get('SURVEY_DATE', '-')}")
    print(f"公開日:     {table.get('OPEN_DATE', '-')}")
    print(f"更新日:     {table.get('UPDATED_DATE', '-')}")
    print(f"データ件数: {table.get('OVERALL_TOTAL_NUMBER', '-')}")
    print(f"{'=' * 80}")

    class_inf = metadata.get("CLASS_INF", {})
    class_objs = class_inf.get("CLASS_OBJ", [])
    if not isinstance(class_objs, list):
        class_objs = [class_objs]

    for obj in class_objs:
        obj_id = obj.get("@id", "")
        obj_name = obj.get("@name", "")
        classes = obj.get("CLASS", [])
        if not isinstance(classes, list):
            classes = [classes]

        print(f"\n--- {obj_name} ({obj_id}) --- {len(classes)} 件")
        print(f"  {'コード':<12}  {'名称':<40}  {'レベル':<6}  {'単位':<10}  {'親コード'}")
        print(f"  {'-' * 90}")

        for cls in classes:
            code = cls.get("@code", "")
            name = cls.get("@name", "")
            level = cls.get("@level", "")
            unit = cls.get("@unit", "")
            parent = cls.get("@parentCode", "")

            name_display = name[:38] + ".." if len(name) > 40 else name
            print(f"  {code:<12}  {name_display:<40}  {level:<6}  {unit:<10}  {parent}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="e-Stat API で統計表のメタ情報を取得する",
    )
    parser.add_argument("stats_data_id", help="統計表ID（search_stats.py の結果から取得）")
    parser.add_argument("--json", action="store_true", help="JSON形式で出力")

    args = parser.parse_args()
    data = fetch_meta(args.stats_data_id)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_meta(data)


if __name__ == "__main__":
    main()
