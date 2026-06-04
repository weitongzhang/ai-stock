#!/usr/bin/env python3
"""Collect CLS telegraph items from the public web endpoint."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


NODE_API_URL = "https://www.cls.cn/nodeapi/telegraphList"
ROLL_API_URL = "https://www.cls.cn/v1/roll/get_roll_list"
REFERER = "https://www.cls.cn/telegraph"


def api_sign(query: str) -> str:
    sha1 = hashlib.sha1(query.encode("utf-8")).hexdigest()
    return hashlib.md5(sha1.encode("utf-8")).hexdigest()


def build_urls(limit: int, last_time: int | None, category: str) -> list[str]:
    urls: list[str] = []

    roll = {
        "app": "CailianpressWeb",
        "category": category,
        "os": "web",
        "rn": str(limit),
    }
    if last_time:
        roll["last_time"] = str(last_time)
    roll_query = urllib.parse.urlencode(roll)
    urls.append(ROLL_API_URL + "?" + roll_query + "&sign=" + api_sign(roll_query))

    node = {
        "app": "CailianpressWeb",
        "os": "web",
        "refresh_type": "1",
        "rn": str(limit),
        "sv": "8.4.6",
    }
    urls.append(NODE_API_URL + "?" + urllib.parse.urlencode(node))

    signed = {
        "app": "CailianpressWeb",
        "last_time": str(last_time or int(time.time())),
        "os": "web",
        "rn": str(limit),
        "sv": "8.4.6",
    }
    query = urllib.parse.urlencode(signed)
    urls.append(NODE_API_URL + "?" + query + "&sign=" + api_sign(query))
    return urls


def fetch_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": REFERER,
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = resp.read().decode("utf-8", errors="replace")
    return json.loads(payload)


def fetch_telegraph(limit: int, last_time: int | None, category: str) -> tuple[dict[str, Any], str]:
    errors: list[str] = []
    for url in build_urls(limit, last_time, category):
        try:
            data = fetch_json(url)
        except Exception as exc:
            errors.append(f"{url}: {exc}")
            continue
        items = ((data.get("data") or {}).get("roll_data") or [])
        if isinstance(items, list):
            return data, url
        errors.append(f"{url}: missing data.roll_data")
    raise RuntimeError("; ".join(errors) or "unknown fetch failure")


def clean_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def item_time(value: Any) -> tuple[str, str]:
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return "", ""
    return str(ts), datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def title_from_content(content: str) -> str:
    bracket = re.match(r"^【([^】]{2,80})】", content)
    if bracket:
        return bracket.group(1).strip()
    sentence = re.split(r"[。！？]", content, maxsplit=1)[0].strip()
    return sentence[:80]


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    ctime, ctime_text = item_time(item.get("ctime"))
    title = clean_text(item.get("title"))
    content = clean_text(item.get("content") or item.get("brief") or title)
    if not title and content:
        title = title_from_content(content)
    share_url = clean_text(item.get("shareurl") or item.get("share_url") or "")
    item_id = str(item.get("id") or item.get("article_id") or "")
    if not share_url and item_id:
        share_url = f"https://www.cls.cn/detail/{item_id}"
    return {
        "id": item_id,
        "ctime": ctime,
        "time": ctime_text,
        "title": title,
        "content": content,
        "shareurl": share_url,
        "category": clean_text(item.get("category") or item.get("category_name")),
        "author": clean_text(item.get("author") or item.get("source")),
        "is_red": str(item.get("is_red") or item.get("red") or ""),
        "level": clean_text(item.get("level")),
        "raw": item,
    }


def apply_filters(rows: list[dict[str, Any]], keywords: list[str], since_ts: int | None) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    lowered = [k.lower() for k in keywords if k]
    for row in rows:
        if since_ts and row.get("ctime"):
            try:
                if int(row["ctime"]) < since_ts:
                    continue
            except ValueError:
                pass
        haystack = f"{row.get('title', '')} {row.get('content', '')}".lower()
        if lowered and not any(k in haystack for k in lowered):
            continue
        filtered.append(row)
    return filtered


def write_outputs(rows: list[dict[str, Any]], raw_payload: dict[str, Any], source_url: str, out_dir: Path) -> tuple[Path, Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    raw_dir = out_dir / "raw" / date
    raw_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / f"{date}-cls-telegraph.csv"
    json_path = out_dir / f"{date}-cls-telegraph.json"
    md_path = out_dir / f"{date}-cls-telegraph.md"
    raw_path = raw_dir / "telegraph-response.json"

    fields = ["id", "ctime", "time", "title", "content", "shareurl", "category", "author", "level", "is_red"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    json_path.write_text(
        json.dumps(
            {
                "source": "cls-telegraph",
                "source_url": source_url,
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "count": len(rows),
                "items": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# {date} CLS Telegraph Digest",
        "",
        f"- 来源：{source_url}",
        f"- 数量：{len(rows)}",
        "",
    ]
    for row in rows:
        title = row.get("title") or "Untitled"
        content = row.get("content") or "-"
        lines.extend(
            [
                f"## {row.get('time') or '-'} {title}",
                "",
                content,
                "",
                f"- 链接：{row.get('shareurl') or '-'}",
                f"- 级别：{row.get('level') or '-'}",
                f"- 高亮：{row.get('is_red') or '-'}",
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, json_path, md_path, raw_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="cls-telegraph", help="Output directory")
    parser.add_argument("--limit", type=int, default=100, help="Number of items to request")
    parser.add_argument("--category", default="", help="CLS category, such as red, important, watch, or jpush")
    parser.add_argument("--keyword", action="append", default=[], help="Keyword filter; repeatable")
    parser.add_argument("--since-ts", type=int, default=None, help="Keep items with ctime >= this Unix timestamp")
    parser.add_argument("--last-time", type=int, default=None, help="Optional API pagination timestamp")
    args = parser.parse_args()

    limit = max(1, min(args.limit, 200))
    try:
        payload, source_url = fetch_telegraph(limit, args.last_time, args.category)
        raw_items = (payload.get("data") or {}).get("roll_data") or []
        rows = [normalize_item(item) for item in raw_items if isinstance(item, dict)]
        rows = [row for row in rows if row.get("title") or row.get("content")]
        rows = apply_filters(rows, args.keyword, args.since_ts)
        csv_path, json_path, md_path, raw_path = write_outputs(rows, payload, source_url, Path(args.out_dir))
        status = "ok" if rows else "no_items"
        print(
            json.dumps(
                {
                    "status": status,
                    "count": len(rows),
                    "csv": str(csv_path),
                    "json": str(json_path),
                    "markdown": str(md_path),
                    "raw": str(raw_path),
                    "source_url": source_url,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if rows else 2
    except Exception as exc:
        print(json.dumps({"status": "fetch_failed", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
