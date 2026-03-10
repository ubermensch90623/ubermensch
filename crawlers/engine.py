"""
병렬 크롤링 엔진
- 여러 사이트를 동시에 크롤링
- 결과를 JSON으로 저장
- 에러 처리 및 재시도
"""

import json
import os
import time
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict

import requests
from bs4 import BeautifulSoup


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass
class CrawlResult:
    """크롤링 결과"""
    url: str
    source_name: str
    source_type: str  # official_questions, exam_review, community, recruitment, etc.
    title: str = ""
    content: str = ""
    links: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    crawled_at: str = ""
    success: bool = True
    error: str = ""

    def to_dict(self):
        return asdict(self)


def fetch_page(url: str, timeout: int = 15, retries: int = 2) -> requests.Response | None:
    """페이지 가져오기 (재시도 포함)"""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt < retries:
                time.sleep(1 * (attempt + 1))
            else:
                return None
    return None


def parse_html(html: str, base_url: str = "") -> dict:
    """HTML을 파싱해서 텍스트와 링크 추출"""
    soup = BeautifulSoup(html, "lxml")

    # 스크립트, 스타일 제거
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # 제목
    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)

    # 본문 텍스트
    body = soup.find("body")
    text = ""
    if body:
        text = body.get_text(separator="\n", strip=True)
        # 빈 줄 정리
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines)

    # 링크 추출 (관련 링크만)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        link_text = a.get_text(strip=True)
        if not link_text or len(link_text) < 2:
            continue
        if href.startswith("/"):
            href = base_url.rstrip("/") + href
        if href.startswith("http"):
            links.append({"text": link_text[:100], "url": href})

    return {"title": title, "text": text[:10000], "links": links[:50]}


def crawl_single(url: str, source_name: str, source_type: str) -> CrawlResult:
    """단일 URL 크롤링"""
    result = CrawlResult(
        url=url,
        source_name=source_name,
        source_type=source_type,
        crawled_at=datetime.now().isoformat(),
    )

    resp = fetch_page(url)
    if resp is None:
        result.success = False
        result.error = f"Failed to fetch {url}"
        return result

    try:
        # 인코딩 처리 (한국 사이트는 EUC-KR인 경우도 있음)
        if resp.encoding and "euc" in resp.encoding.lower():
            resp.encoding = "euc-kr"
        elif resp.apparent_encoding:
            resp.encoding = resp.apparent_encoding

        parsed = parse_html(resp.text, url.split("/")[0] + "//" + url.split("/")[2])
        result.title = parsed["title"]
        result.content = parsed["text"]
        result.links = parsed["links"]
        result.metadata = {
            "status_code": resp.status_code,
            "content_length": len(resp.text),
            "encoding": resp.encoding,
        }
    except Exception as e:
        result.success = False
        result.error = str(e)

    return result


def crawl_parallel(targets: list[dict], max_workers: int = 5) -> list[CrawlResult]:
    """
    여러 URL을 병렬로 크롤링

    targets: [{"url": "...", "name": "...", "type": "..."}]
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for t in targets:
            future = executor.submit(
                crawl_single,
                url=t["url"],
                source_name=t.get("name", ""),
                source_type=t.get("type", "general"),
            )
            futures[future] = t

        for future in as_completed(futures):
            target = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(CrawlResult(
                    url=target["url"],
                    source_name=target.get("name", ""),
                    source_type=target.get("type", ""),
                    success=False,
                    error=str(e),
                    crawled_at=datetime.now().isoformat(),
                ))

    return results


def save_results(results: list[CrawlResult], label: str = "crawl") -> str:
    """크롤링 결과를 JSON으로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{label}_{timestamp}.json"
    filepath = os.path.join(DATA_DIR, filename)

    data = {
        "crawled_at": datetime.now().isoformat(),
        "total": len(results),
        "success": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [r.to_dict() for r in results],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def load_latest_results(label: str = "crawl") -> dict | None:
    """가장 최근 크롤링 결과 로드"""
    files = sorted(
        [f for f in os.listdir(DATA_DIR) if f.startswith(label) and f.endswith(".json")],
        reverse=True,
    )
    if not files:
        return None

    filepath = os.path.join(DATA_DIR, files[0])
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def crawl_all_sources() -> str:
    """모든 소스를 병렬로 크롤링하고 결과 저장"""
    from crawlers.sources import NCS_COMMON_SOURCES, TARGET_INSTITUTIONS

    targets = []

    # NCS 공통 소스
    for src in NCS_COMMON_SOURCES:
        targets.append({
            "url": src["url"],
            "name": src["name"],
            "type": src["type"],
        })

    # 기관별 채용 페이지
    for key, inst in TARGET_INSTITUTIONS.items():
        targets.append({
            "url": inst["recruit_url"],
            "name": f"{inst['name']} 채용공고",
            "type": "recruitment",
        })
        targets.append({
            "url": inst["website"],
            "name": f"{inst['name']} 홈페이지",
            "type": "institution_info",
        })

    print(f"[크롤링 시작] {len(targets)}개 사이트를 동시에 수집합니다...")
    results = crawl_parallel(targets, max_workers=8)

    filepath = save_results(results, "all_sources")

    success = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    print(f"[크롤링 완료] 성공: {success}, 실패: {failed}")
    print(f"[저장 완료] {filepath}")

    return filepath


if __name__ == "__main__":
    crawl_all_sources()
