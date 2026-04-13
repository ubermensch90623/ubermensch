"""네이버 블로그 iframe 풀기.

blog.naver.com/{id}/{logNo} 로 접근하면 실제 본문은 iframe 안에 로드된다:
    https://blog.naver.com/PostView.naver?blogId={id}&logNo={logNo}...

WebFetch 는 iframe src 를 따라가지 않으므로 본문이 비어 보인다. 여기서는
PostView.naver 를 직접 요청하거나, 모바일 뷰(m.blog.naver.com)를 사용해서
본문을 얻는다. 모바일 뷰는 광고/사이드바가 적어 훨씬 깔끔하다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

import httpx

from ..http import make_client
from ..markdown import html_to_markdown

_BLOG_PATH = re.compile(r"^/(?P<blog_id>[^/]+)/(?P<log_no>\d+)/?$")


@dataclass
class NaverPost:
    blog_id: str
    log_no: str
    title: str
    body_md: str
    url: str


def _extract_ids(url: str) -> tuple[str, str] | None:
    p = urlparse(url)
    host = p.hostname or ""
    if host not in {"blog.naver.com", "m.blog.naver.com"}:
        return None

    # PostView.naver?blogId=...&logNo=... 형태
    if p.path.rstrip("/").endswith("PostView.naver"):
        q = parse_qs(p.query)
        blog_id = (q.get("blogId") or [None])[0]
        log_no = (q.get("logNo") or [None])[0]
        if blog_id and log_no:
            return blog_id, log_no
        return None

    m = _BLOG_PATH.match(p.path)
    if m:
        return m.group("blog_id"), m.group("log_no")
    return None


def is_naver_blog(url: str) -> bool:
    return _extract_ids(url) is not None


async def fetch_post(url: str) -> NaverPost:
    parsed = _extract_ids(url)
    if not parsed:
        raise ValueError(f"네이버 블로그 URL 이 아닙니다: {url}")
    blog_id, log_no = parsed

    # 모바일 뷰가 가장 클린하다.
    mobile_url = f"https://m.blog.naver.com/{blog_id}/{log_no}"
    async with make_client(headers={"Referer": "https://m.blog.naver.com/"}) as client:
        r = await client.get(mobile_url)
        r.raise_for_status()
        html = r.text

        # 본문이 비어있는 경우 PostView.naver 로 폴백
        if "se-main-container" not in html and "post_ct" not in html:
            r = await client.get(
                "https://blog.naver.com/PostView.naver",
                params={"blogId": blog_id, "logNo": log_no, "redirect": "Dlog"},
            )
            r.raise_for_status()
            html = r.text

    # 제목 우선 se_title → h3.se_textarea → meta[property=og:title]
    from selectolax.parser import HTMLParser

    tree = HTMLParser(html)
    title = ""
    for sel in (
        ".se-title-text",
        ".se_title",
        "h3.se_textarea",
        "h3.tit_h3",
        'meta[property="og:title"]',
    ):
        node = tree.css_first(sel)
        if node:
            title = (node.attributes.get("content") or node.text(strip=True) or "").strip()
            if title:
                break

    # 본문 컨테이너 후보
    body_md = ""
    for sel in (".se-main-container", "#postViewArea", ".post_ct", "#viewTypeSelector"):
        extracted = html_to_markdown(html, selector=sel)
        if extracted.strip():
            body_md = extracted
            break
    if not body_md:
        body_md = html_to_markdown(html)

    return NaverPost(
        blog_id=blog_id,
        log_no=log_no,
        title=title,
        body_md=body_md,
        url=f"https://blog.naver.com/{blog_id}/{log_no}",
    )


def format_post(p: NaverPost) -> str:
    return (
        f"# {p.title or '(제목 없음)'}\n\n"
        f"<{p.url}>\n\n"
        f"{p.body_md.strip()}\n"
    )
