"""StackOverflow (및 기타 Stack Exchange 사이트) 우회 페처.

일부 기업/학교 네트워크에서 stackoverflow.com 도메인이 차단되어도
api.stackexchange.com 은 흔히 열려있다. 또한 공식 Stack Exchange API 는
인증 없이도 IP 당 하루 300회 요청을 허용하므로 일반적 용도에 충분하다.

엔드포인트:
    https://api.stackexchange.com/2.3/questions/{id}?site=stackoverflow&filter=withbody
    https://api.stackexchange.com/2.3/questions/{id}/answers?site=stackoverflow&filter=withbody
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx

from ..http import make_client
from ..markdown import html_to_markdown

_QUESTION_PATH = re.compile(r"^/questions/(\d+)")

# Stack Exchange 네트워크에서 URL 도메인 → API site 파라미터 매핑
_SITE_MAP = {
    "stackoverflow.com": "stackoverflow",
    "serverfault.com": "serverfault",
    "superuser.com": "superuser",
    "askubuntu.com": "askubuntu",
    "mathoverflow.net": "mathoverflow.net",
}


@dataclass
class Answer:
    id: int
    author: str
    score: int
    is_accepted: bool
    body_md: str


@dataclass
class Question:
    id: int
    site: str
    title: str
    author: str
    score: int
    tags: list[str]
    body_md: str
    link: str
    answers: list[Answer] = field(default_factory=list)


def parse_question_url(url: str) -> tuple[str, int] | None:
    """(site, question_id) 추출. Stack Exchange 사이트가 아니면 None."""
    p = urlparse(url)
    host = p.hostname or ""
    # *.stackexchange.com 은 subdomain 이 곧 site 이름
    if host.endswith(".stackexchange.com"):
        site = host.removesuffix(".stackexchange.com")
    else:
        site = _SITE_MAP.get(host)
        if not site:
            return None
    m = _QUESTION_PATH.match(p.path)
    if not m:
        return None
    return site, int(m.group(1))


async def fetch_question(url: str, *, max_answers: int = 5) -> Question:
    parsed = parse_question_url(url)
    if not parsed:
        raise ValueError(f"Stack Exchange 질문 URL 이 아닙니다: {url}")
    site, qid = parsed

    base = f"https://api.stackexchange.com/2.3/questions/{qid}"
    params = {"site": site, "filter": "withbody"}

    async with make_client() as client:
        q_resp = await client.get(base, params=params)
        q_resp.raise_for_status()
        q_data = q_resp.json()
        items = q_data.get("items") or []
        if not items:
            raise RuntimeError(f"질문 {qid} 를 찾지 못했습니다.")
        q = items[0]

        a_resp = await client.get(
            f"{base}/answers",
            params={**params, "order": "desc", "sort": "votes", "pagesize": max_answers},
        )
        a_resp.raise_for_status()
        a_items = a_resp.json().get("items") or []

    answers = [
        Answer(
            id=a["answer_id"],
            author=(a.get("owner") or {}).get("display_name", "anonymous"),
            score=int(a.get("score", 0)),
            is_accepted=bool(a.get("is_accepted")),
            body_md=html_to_markdown(a.get("body", "")),
        )
        for a in a_items
    ]

    return Question(
        id=q["question_id"],
        site=site,
        title=q.get("title", ""),
        author=(q.get("owner") or {}).get("display_name", "anonymous"),
        score=int(q.get("score", 0)),
        tags=list(q.get("tags") or []),
        body_md=html_to_markdown(q.get("body", "")),
        link=q.get("link", url),
        answers=answers,
    )


def format_question(q: Question) -> str:
    tag_str = " ".join(f"`{t}`" for t in q.tags)
    lines = [
        f"# {q.title}",
        "",
        f"**{q.site}** · by {q.author} · score {q.score} · {tag_str}",
        f"<{q.link}>",
        "",
        q.body_md.strip(),
        "",
        "## Answers",
        "",
    ]
    for a in q.answers:
        tag = " (accepted)" if a.is_accepted else ""
        lines.append(f"### Answer by {a.author} — score {a.score}{tag}")
        lines.append("")
        lines.append(a.body_md.strip())
        lines.append("")
    return "\n".join(lines)
