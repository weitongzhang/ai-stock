#!/usr/bin/env python3
"""Collect metadata from WeChat Official Account article URLs or exported HTML files."""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def read_inputs(path: Path) -> list[str]:
    items: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            items.append(line)
    return items


def read_cookie(cookie_file: str) -> str:
    if not cookie_file:
        return ""
    path = Path(cookie_file)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def fetch_url(url: str) -> tuple[str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
        content_type = resp.headers.get("Content-Type", "")
    encoding = "utf-8"
    match = re.search(r"charset=([\w-]+)", content_type, re.I)
    if match:
        encoding = match.group(1)
    return raw.decode(encoding, errors="replace"), "url"


def read_source(item: str) -> tuple[str, str, str]:
    if item.startswith(("http://", "https://")):
        text, source_type = fetch_url(item)
        return text, source_type, item
    path = Path(item)
    text = path.read_text(encoding="utf-8", errors="replace")
    return text, "file", str(path.resolve())


def first_match(patterns: Iterable[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            value = match.group(1)
            value = re.sub(r"<[^>]+>", "", value)
            value = html.unescape(value)
            value = re.sub(r"\s+", " ", value).strip()
            if value:
                return value
    return ""


def js_var(name: str, text: str) -> str:
    return first_match([
        rf'\bvar\s+{re.escape(name)}\s*=\s*["\']([^"\']*)["\']',
        rf'\bwindow\.{re.escape(name)}\s*=\s*["\']([^"\']*)["\']',
        rf'\b{name}\s*:\s*["\']([^"\']*)["\']',
    ], text)


def plain_text(html_text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html_text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def safe_name(value: str, fallback: str = "article") -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value).strip()
    value = re.sub(r"\s+", "-", value)
    return (value[:80] or fallback).strip(".-")


def image_urls(html_text: str) -> list[str]:
    urls: list[str] = []
    for match in re.finditer(r'<img\b[^>]*(?:data-src|src)=["\']([^"\']+)["\']', html_text, re.I):
        url = html.unescape(match.group(1)).strip()
        if not url or url.startswith(("data:", "blob:")):
            continue
        if url.startswith("//"):
            url = "https:" + url
        if url.startswith("http") and url not in urls:
            urls.append(url)
    return urls


def image_ext(url: str, content_type: str) -> str:
    if "png" in content_type:
        return ".png"
    if "webp" in content_type:
        return ".webp"
    if "gif" in content_type:
        return ".gif"
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    parsed = urllib.parse.urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    return suffix if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"} else ".jpg"


def download_images(urls: list[str], image_dir: Path, referer: str) -> dict[str, str]:
    image_dir.mkdir(parents=True, exist_ok=True)
    saved: dict[str, str] = {}
    for idx, url in enumerate(urls, 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": referer if referer.startswith("http") else "https://mp.weixin.qq.com/",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                },
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read()
                ext = image_ext(url, resp.headers.get("Content-Type", ""))
            if len(content) < 128:
                continue
            path = image_dir / f"image-{idx:02d}{ext}"
            path.write_bytes(content)
            saved[url] = str(path.resolve()).replace("\\", "/")
        except Exception:
            continue
    return saved


def img_url(tag: Tag) -> str:
    url = html.unescape((tag.get("data-src") or tag.get("src") or "")).strip()
    if url.startswith("//"):
        url = "https:" + url
    return url


def block_text(tag: Tag) -> str:
    text = tag.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def node_to_markdown(node, image_map: dict[str, str], lines: list[str]) -> None:
    if isinstance(node, NavigableString):
        text = re.sub(r"\s+", " ", str(node)).strip()
        if text:
            lines.append(text)
            lines.append("")
        return

    if not isinstance(node, Tag):
        return

    if node.name == "img":
        url = img_url(node)
        path = image_map.get(url)
        if path:
            alt = block_text(node) or "image"
            lines.append(f"![{alt}]({path})")
            lines.append("")
        return

    if node.find("img"):
        for child in node.children:
            node_to_markdown(child, image_map, lines)
        return

    if node.name in {"p", "section", "div", "blockquote", "li", "h1", "h2", "h3", "h4"}:
        text = block_text(node)
        if text:
            if node.name in {"h1", "h2"}:
                lines.append(f"## {text}")
            elif node.name in {"h3", "h4"}:
                lines.append(f"### {text}")
            elif node.name == "li":
                lines.append(f"- {text}")
            else:
                lines.append(text)
            lines.append("")
        return

    for child in node.children:
        node_to_markdown(child, image_map, lines)


def article_markdown(html_text: str, title: str, meta: dict[str, str], image_map: dict[str, str]) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    content = soup.find(id="js_content") or soup.find(class_="rich_media_content") or soup.body
    lines = [
        f"# {title or 'Untitled'}",
        "",
        f"- 来源：{meta.get('account') or '-'}",
        f"- 作者：{meta.get('author') or '-'}",
        f"- 时间：{meta.get('publish_time') or '-'}",
        f"- 链接：{meta.get('url') or '-'}",
        "",
    ]
    if content:
        for child in content.children:
            node_to_markdown(child, image_map, lines)
    return "\n".join(line.rstrip() for line in lines).strip() + "\n"


def comment_params(html_text: str) -> dict[str, str]:
    return {
        "__biz": js_var("biz", html_text),
        "appmsgid": js_var("mid", html_text),
        "idx": js_var("idx", html_text),
        "sn": js_var("sn", html_text),
        "comment_id": js_var("comment_id", html_text),
        "appmsg_token": js_var("appmsg_token", html_text),
        "pass_ticket": js_var("pass_ticket", html_text),
    }


def normalize_comment(item: dict, source: str = "elected") -> dict[str, str]:
    content = item.get("content") or item.get("comment_content") or ""
    nick = item.get("nick_name") or item.get("nickname") or item.get("user_name") or ""
    create_time = item.get("create_time") or item.get("time") or ""
    like_num = item.get("like_num") or item.get("like_count") or item.get("like_id") or ""
    reply = item.get("reply") or item.get("reply_list") or []
    if isinstance(reply, list):
        reply_text = " | ".join(str((r or {}).get("content", "")) for r in reply if isinstance(r, dict))
    else:
        reply_text = str(reply or "")
    return {
        "source": source,
        "nickname": str(nick),
        "create_time": str(create_time),
        "like_num": str(like_num),
        "content": re.sub(r"\s+", " ", html.unescape(str(content))).strip(),
        "reply": re.sub(r"\s+", " ", html.unescape(reply_text)).strip(),
    }


def parse_comments_payload(data: dict) -> list[dict[str, str]]:
    comments: list[dict[str, str]] = []
    for key in ("elected_comment", "comment", "comment_list"):
        value = data.get(key)
        if isinstance(value, list):
            comments.extend(normalize_comment(item, key) for item in value if isinstance(item, dict))
    for key in ("elected_comment", "base_resp"):
        value = data.get(key)
        if isinstance(value, dict) and isinstance(value.get("comment"), list):
            comments.extend(normalize_comment(item, key) for item in value["comment"] if isinstance(item, dict))
    return [c for c in comments if c.get("content") or c.get("nickname")]


def fetch_comments(html_text: str, article_url: str, cookie: str) -> tuple[list[dict[str, str]], str, dict[str, str]]:
    params = comment_params(html_text)
    if not params.get("comment_id"):
        return [], "no_comment_id", params

    query = {
        "action": "getcomment",
        "scene": "0",
        "__biz": params.get("__biz", ""),
        "appmsgid": params.get("appmsgid", ""),
        "idx": params.get("idx", "1"),
        "comment_id": params.get("comment_id", ""),
        "offset": "0",
        "limit": "100",
        "uin": "",
        "key": "",
        "pass_ticket": params.get("pass_ticket", ""),
        "wxtoken": "777",
        "devicetype": "Windows 10 x64",
        "clientversion": "63090c19",
        "appmsg_token": params.get("appmsg_token", ""),
        "x5": "0",
        "f": "json",
    }
    url = "https://mp.weixin.qq.com/mp/appmsg_comment?" + urllib.parse.urlencode(query)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": article_url,
        "Accept": "application/json,text/plain,*/*",
    }
    if cookie:
        headers["Cookie"] = cookie

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
        data = json.loads(payload)
    except Exception as exc:
        return [], f"comment_fetch_failed: {exc}", params

    comments = parse_comments_payload(data)
    base_resp = data.get("base_resp") or data.get("BaseResponse") or {}
    ret = base_resp.get("ret") if isinstance(base_resp, dict) else data.get("ret")
    errmsg = base_resp.get("errmsg") if isinstance(base_resp, dict) else data.get("errmsg")
    if comments:
        return comments, "ok", params
    if ret not in (None, 0, "0"):
        return [], f"comment_api_ret={ret}: {errmsg or ''}".strip(), params
    return [], "no_comments_or_requires_login_token", params


def write_comments(comments: list[dict[str, str]], article_dir: Path, title: str, status: str, params: dict[str, str]) -> tuple[str, str]:
    comments_csv = article_dir / "comments.csv"
    comments_md = article_dir / "comments.md"
    fields = ["source", "nickname", "create_time", "like_num", "content", "reply"]
    with comments_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(comments)

    lines = [
        f"# {title or 'Untitled'} - Comments",
        "",
        f"- 状态：{status}",
        f"- comment_id：{params.get('comment_id') or '-'}",
        f"- 数量：{len(comments)}",
        "",
    ]
    for idx, comment in enumerate(comments, 1):
        lines.extend([
            f"## {idx}. {comment.get('nickname') or '匿名'}",
            "",
            f"- 时间：{comment.get('create_time') or '-'}",
            f"- 点赞：{comment.get('like_num') or '-'}",
            "",
            comment.get("content") or "",
            "",
        ])
        if comment.get("reply"):
            lines.extend(["回复：", "", comment["reply"], ""])
    comments_md.write_text("\n".join(lines), encoding="utf-8")
    return str(comments_csv.resolve()).replace("\\", "/"), str(comments_md.resolve()).replace("\\", "/")


def extract(item: str, raw_dir: Path, cookie: str = "") -> dict[str, str]:
    status = "ok"
    try:
        html_text, source_type, source = read_source(item)
    except Exception as exc:
        return {
            "date_collected": datetime.now().strftime("%Y-%m-%d"),
            "title": "",
            "account": "",
            "author": "",
            "publish_time": "",
            "url": item,
            "source_type": "error",
            "summary": "",
            "tags": "",
            "comments_csv": "",
            "comments_markdown": "",
            "comment_count": "0",
            "comment_status": "",
            "status": f"fetch_failed: {exc}",
        }

    title = first_match([
        r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+name=["\']twitter:title["\']\s+content=["\']([^"\']+)["\']',
        r"<title>(.*?)</title>",
        r'id=["\']activity-name["\'][^>]*>(.*?)</',
    ], html_text)
    account = first_match([
        r'var\s+nickname\s*=\s*["\']([^"\']+)["\']',
        r'id=["\']js_name["\'][^>]*>(.*?)</',
        r'<meta\s+property=["\']og:site_name["\']\s+content=["\']([^"\']+)["\']',
    ], html_text)
    author = first_match([
        r'var\s+author\s*=\s*["\']([^"\']*)["\']',
        r'id=["\']meta_content["\'][\s\S]*?作者[^<]*<[^>]+>(.*?)</',
    ], html_text)
    publish_time = first_match([
        r'var\s+publish_time\s*=\s*["\']([^"\']+)["\']',
        r'id=["\']publish_time["\'][^>]*>(.*?)</',
        r'(\d{4}-\d{1,2}-\d{1,2}(?:\s+\d{1,2}:\d{2})?)',
    ], html_text)

    text = plain_text(html_text)
    if any(token in text[:1000] for token in ["环境异常", "验证", "登录", "访问频繁"]):
        status = "may_require_browser_or_manual_export"
    summary = text[:260] + ("..." if len(text) > 260 else "")

    article_slug = safe_name(title or account or datetime.now().strftime("%H%M%S"))
    article_dir = raw_dir / article_slug
    article_dir.mkdir(parents=True, exist_ok=True)
    html_path = article_dir / "source.html"
    html_path.write_text(html_text, encoding="utf-8")
    saved_image_map = download_images(image_urls(html_text), article_dir / "images", source)
    saved_images = list(saved_image_map.values())
    article_md_path = article_dir / "article.md"
    comments, comment_status, cparams = fetch_comments(html_text, source, cookie)
    comments_csv, comments_md = write_comments(comments, article_dir, title, comment_status, cparams)

    row = {
        "date_collected": datetime.now().strftime("%Y-%m-%d"),
        "title": title,
        "account": account,
        "author": author,
        "publish_time": publish_time,
        "url": source,
        "source_type": source_type,
        "summary": summary,
        "tags": "",
        "raw_html": str(html_path.resolve()).replace("\\", "/"),
        "article_markdown": str(article_md_path.resolve()).replace("\\", "/"),
        "comments_csv": comments_csv,
        "comments_markdown": comments_md,
        "comment_count": str(len(comments)),
        "comment_status": comment_status,
        "images": "|".join(saved_images),
        "image_count": str(len(saved_images)),
        "status": status,
    }
    article_md_path.write_text(article_markdown(html_text, title, row, saved_image_map), encoding="utf-8")
    return row


def write_outputs(rows: list[dict[str, str]], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    csv_path = out_dir / f"{date}-wechat-articles.csv"
    md_path = out_dir / f"{date}-wechat-digest.md"

    fields = ["date_collected", "title", "account", "author", "publish_time", "url", "source_type", "summary", "tags", "raw_html", "article_markdown", "comments_csv", "comments_markdown", "comment_count", "comment_status", "images", "image_count", "status"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = [f"# {date} WeChat Digest", ""]
    for row in rows:
        lines.extend([
            f"### {row.get('title') or 'Untitled'}",
            "",
            f"- 来源：{row.get('account') or '-'}",
            f"- 作者：{row.get('author') or '-'}",
            f"- 时间：{row.get('publish_time') or '-'}",
            f"- 链接：{row.get('url') or '-'}",
            f"- 图文版：{row.get('article_markdown') or '-'}",
            f"- 评论：{row.get('comment_count') or '0'} 条，{row.get('comments_markdown') or '-'}",
            f"- 评论状态：{row.get('comment_status') or '-'}",
            f"- 状态：{row.get('status') or '-'}",
            f"- 图片：{row.get('image_count') or '0'} 张",
            f"- 摘要：{row.get('summary') or '-'}",
            "",
        ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="UTF-8 text file containing URLs or local HTML paths")
    parser.add_argument("--out-dir", default="wechat-daily", help="Output directory")
    parser.add_argument("--cookie-file", default="", help="Optional text file containing logged-in mp.weixin.qq.com Cookie")
    args = parser.parse_args()

    items = read_inputs(Path(args.input))
    raw_dir = Path(args.out_dir) / "raw" / datetime.now().strftime("%Y-%m-%d")
    cookie = read_cookie(args.cookie_file)
    rows = [extract(item, raw_dir, cookie) for item in items]
    csv_path, md_path = write_outputs(rows, Path(args.out_dir))
    print(json.dumps({"count": len(rows), "csv": str(csv_path), "markdown": str(md_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
