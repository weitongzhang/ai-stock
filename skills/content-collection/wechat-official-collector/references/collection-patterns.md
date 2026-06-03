# Collection Patterns

## Recommended Sources

- Best: user-provided `mp.weixin.qq.com/s/...` article links.
- Good: browser-exported complete HTML files.
- Good: copied article text for manual summary.
- Avoid: automated enumeration of every post from a WeChat account without authorization.

## Daily Archive Layout

```text
wechat-daily/
  2026-06-03-wechat-digest.md
  2026-06-03-wechat-articles.csv
  raw/
    2026-06-03/
      2026-6-2-数据/
        source.html
        article.md
        comments.md
        comments.csv
        images/
          image-01.jpg
          image-02.png
```

## Metadata Fields

- `date_collected`
- `title`
- `account`
- `author`
- `publish_time`
- `url`
- `source_type`
- `summary`
- `raw_html`
- `article_markdown`
- `comments_csv`
- `comments_markdown`
- `comment_count`
- `comment_status`
- `images`
- `image_count`
- `status`

## Comment Notes

WeChat comments are not normally embedded as static article text. The article HTML may expose:

- `comment_id`
- `__biz`
- `mid` / `appmsgid`
- `idx`
- `sn`
- `appmsg_token`
- `pass_ticket`

The public page often has an empty `appmsg_token`, and the comment API can return `no session`. This is expected without a valid logged-in session cookie.

## Failure Handling

- If the URL returns a verification page, login page, empty response, or JavaScript shell, report `需要浏览器/手动导出`.
- If metadata is missing, keep the URL and mark inferred fields clearly.
- If images are missing but visible in browser, ask for complete saved HTML or browser-assisted capture.
- If comments require session, ask for an authorized cookie file; never ask the user to bypass access controls.
- Deduplicate by URL first, then title + publish date.
