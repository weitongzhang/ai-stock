---
name: wechat-official-collector
description: 微信公众号文章采集、图文归档、图片下载、评论尝试抓取与每日摘要工作流。Use when Codex needs to collect or archive WeChat Official Account / mp.weixin.qq.com articles from user-provided links or exported HTML, preserve article text-image order, save raw HTML/images, extract title/account/author/publish time, fetch comments when an authorized session cookie is provided, and produce Markdown/CSV daily digests.
---

# WeChat Official Collector

Use this skill for requests like:

- “采集这个微信公众号文章”
- “保存公众号文章和图片”
- “把每天博主公众号内容归档”
- “提取文章评论”
- “生成微信公众号每日摘要”

## Boundaries

- Do not bypass WeChat login, paywalls, account permissions, rate limits, verification pages, or anti-scraping controls.
- Use only user-provided article URLs, exported HTML, copied article text, browser-opened pages, or authorized cookies/APIs supplied by the user.
- Do not reproduce full copyrighted article text in chat. Archive locally when requested; summarize in the final answer.
- Comments often require a valid logged-in `mp.weixin.qq.com` session. If no session is available, record the failure status instead of trying to evade it.

## Quick Start

Create an input file with one URL or local HTML path per line:

```text
https://mp.weixin.qq.com/s/QruXWVRkSnKAPFsOXFWfOQ
C:\path\to\exported_article.html
```

Run from the `wechat-official-collector` skill directory, or replace `scripts\...` with the script path in the current installation:

```powershell
python scripts\collect_wechat_articles.py --input links.txt --out-dir .\wechat-daily
```

If the user provides a valid logged-in cookie text file for comments:

```powershell
python scripts\collect_wechat_articles.py --input links.txt --out-dir .\wechat-daily --cookie-file wechat_cookie.txt
```

## Outputs

The script writes:

- `YYYY-MM-DD-wechat-digest.md`: daily index with metadata, summary, image count, comment status, and links to per-article files.
- `YYYY-MM-DD-wechat-articles.csv`: structured metadata table.
- `raw/YYYY-MM-DD/<article-title>/source.html`: saved raw article HTML.
- `raw/YYYY-MM-DD/<article-title>/article.md`: text-image ordered Markdown version.
- `raw/YYYY-MM-DD/<article-title>/images/`: downloaded article images.
- `raw/YYYY-MM-DD/<article-title>/comments.md`: comments if available, otherwise status such as `no session`.
- `raw/YYYY-MM-DD/<article-title>/comments.csv`: structured comments table.

## Workflow

1. Identify the source type:
   - `mp.weixin.qq.com` URL.
   - local exported `.html`.
   - copied text, which may need manual Markdown creation rather than the extractor.
2. Run `scripts/collect_wechat_articles.py`.
3. Inspect the generated digest and per-article `article.md`.
4. If images are missing, check whether the raw HTML contains image `data-src` URLs; if not, ask the user for a browser-exported complete HTML.
5. If comments show `comment_api_ret=-3: no session` or similar, explain that a valid logged-in session cookie is required and rerun with `--cookie-file` if supplied.
6. Summarize only the key metadata and output paths in chat.

## Interpretation

- `status=ok`: article HTML and metadata were collected.
- `may_require_browser_or_manual_export`: page likely returned verification/login content.
- `image_count=0`: no downloadable image URLs were found or image fetch failed.
- `comment_status=ok`: comments were fetched.
- `comment_status=no_comment_id`: article page did not expose a comment id.
- `comment_status=comment_api_ret=-3: no session`: WeChat comment API requires login/session.

## References

Read `references/collection-patterns.md` when designing daily recurring collection, choosing an archive layout, or troubleshooting missing images/comments.
