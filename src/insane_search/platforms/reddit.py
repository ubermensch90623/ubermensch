"""Reddit 우회 페처.

일반 www.reddit.com 는 기본 User-Agent 로 접근하면 429/403 을 던진다.
다만 Reddit 은 예전부터 공개 JSON 엔드포인트를 유지하고 있다:

    https://www.reddit.com/comments/<id>.json
    https://old.reddit.com/r/<sub>/comments/<id>/.json

사람같은 User-Agent 와 Accept 만 맞추면 인증 없이 접근할 수 있다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx

from ..http import make_client

_POST_PATH = re.compile(
    r"^/(?:r/[^/]+/)?comments/(?P<id>[a-z0-9]+)(?:/[^/]*)?/?$"
)
_SUB_PATH = re.compile(r"^/r/(?P<sub>[^/]+)/?$")


@dataclass
class Comment:
    author: str
    body: str
    score: int
    replies: list["Comment"] = field(default_factory=list)


@dataclass
class Post:
    id: str
    subreddit: str
    title: str
    author: str
    score: int
    url: str
    selftext: str
    permalink: str
    comments: list[Comment]


def _is_reddit_host(host: str | None) -> bool:
    return host in {
        "www.reddit.com",
        "reddit.com",
        "old.reddit.com",
        "new.reddit.com",
        "np.reddit.com",
    }


def parse_reddit_url(url: str) -> tuple[str, str | None]:
    """URL 에서 ('post'|'sub'|'other', 식별자) 를 추출한다."""
    p = urlparse(url)
    if not _is_reddit_host(p.hostname):
        raise ValueError(f"Reddit URL 이 아닙니다: {url}")
    m = _POST_PATH.match(p.path.lower())
    if m:
        return "post", m.group("id")
    m = _SUB_PATH.match(p.path.lower())
    if m:
        return "sub", m.group("sub")
    return "other", None


def _parse_comment(node: dict) -> Comment | None:
    if node.get("kind") != "t1":
        return None
    data = node.get("data", {})
    replies_raw = data.get("replies") or {}
    replies: list[Comment] = []
    if isinstance(replies_raw, dict):
        for child in replies_raw.get("data", {}).get("children", []):
            c = _parse_comment(child)
            if c:
                replies.append(c)
    return Comment(
        author=data.get("author", "[deleted]"),
        body=data.get("body", ""),
        score=int(data.get("score", 0) or 0),
        replies=replies,
    )


async def _get_json(client: httpx.AsyncClient, url: str) -> object:
    r = await client.get(url, headers={"Accept": "application/json"})
    r.raise_for_status()
    return r.json()


async def fetch_post(url: str, *, max_comments: int = 50) -> Post:
    kind, ident = parse_reddit_url(url)
    if kind != "post" or not ident:
        raise ValueError(f"Reddit 포스트 URL 이 아닙니다: {url}")

    api = f"https://www.reddit.com/comments/{ident}.json?raw_json=1&limit={max_comments}"
    async with make_client() as client:
        try:
            data = await _get_json(client, api)
        except httpx.HTTPStatusError:
            # old.reddit 으로 재시도 — 가끔 차단 정책이 다르다.
            data = await _get_json(
                client, f"https://old.reddit.com/comments/{ident}.json?raw_json=1"
            )

    if not isinstance(data, list) or len(data) < 2:
        raise RuntimeError("예상치 못한 Reddit 응답 형태입니다.")

    post_listing, comment_listing = data[0], data[1]
    post_children = post_listing.get("data", {}).get("children", [])
    if not post_children:
        raise RuntimeError("포스트를 찾을 수 없습니다.")
    p = post_children[0].get("data", {})

    comments: list[Comment] = []
    for child in comment_listing.get("data", {}).get("children", []):
        c = _parse_comment(child)
        if c:
            comments.append(c)

    return Post(
        id=p.get("id", ident),
        subreddit=p.get("subreddit", ""),
        title=p.get("title", ""),
        author=p.get("author", "[deleted]"),
        score=int(p.get("score", 0) or 0),
        url=p.get("url", url),
        selftext=p.get("selftext", ""),
        permalink=f"https://www.reddit.com{p.get('permalink','')}",
        comments=comments,
    )


def format_post(post: Post, *, max_comments: int = 20, max_depth: int = 3) -> str:
    lines = [
        f"# {post.title}",
        "",
        f"**r/{post.subreddit}** · u/{post.author} · score {post.score}",
        f"<{post.permalink}>",
        "",
    ]
    if post.selftext:
        lines.extend([post.selftext.strip(), ""])
    elif post.url and post.url != post.permalink:
        lines.extend([f"링크: {post.url}", ""])

    lines.append("## Comments")
    lines.append("")

    def walk(c: Comment, depth: int) -> None:
        if depth > max_depth:
            return
        indent = "  " * depth
        lines.append(f"{indent}- **u/{c.author}** ({c.score}): {c.body.strip()}")
        for r in c.replies:
            walk(r, depth + 1)

    shown = post.comments[:max_comments]
    for c in shown:
        walk(c, 0)
    if len(post.comments) > max_comments:
        lines.append("")
        lines.append(f"_...and {len(post.comments) - max_comments} more comments_")

    return "\n".join(lines) + "\n"
