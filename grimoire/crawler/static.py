"""Static web crawler using requests + BeautifulSoup."""

import time
from urllib.parse import urljoin, urlparse
import requests
from grimoire.extractor import extract, ExtractionResult


def crawl_static(url: str, depth: int = 2, delay: float = 0,
                 proxy: str = "", cookie: str = "", headers: dict | None = None,
                 random_ua: bool = False, min_length: int = 5, max_length: int = 0,
                 emails: bool = False, meta: bool = False, js_strings: bool = False,
                 on_page=None, on_error=None) -> ExtractionResult:
    result = ExtractionResult()
    visited = set()
    base_host = urlparse(url).netloc

    session = requests.Session()
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
    if cookie:
        session.headers["Cookie"] = cookie
    if headers:
        session.headers.update(headers)

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    ua_index = [0]

    def get_ua():
        if random_ua:
            import random
            return random.choice(UA_LIST)
        ua = UA_LIST[ua_index[0] % len(UA_LIST)]
        ua_index[0] += 1
        return ua

    def _crawl(page_url: str, current_depth: int):
        if current_depth < 0 or page_url in visited:
            return
        visited.add(page_url)

        try:
            session.headers["User-Agent"] = get_ua()
            resp = session.get(page_url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            if on_error:
                on_error(page_url, e)
            return

        html_content = resp.text
        page_result = extract(
            html_content, min_length=min_length, max_length=max_length,
            emails=emails, meta=meta, js_strings=js_strings,
        )
        result.merge(page_result)

        if on_page:
            on_page(page_url, page_result)

        if current_depth > 0:
            links = _extract_links(html_content, page_url, base_host)
            for link in links:
                if delay > 0:
                    time.sleep(delay / 1000.0)
                _crawl(link, current_depth - 1)

    _crawl(url, depth)
    return result


def _extract_links(html: str, base_url: str, base_host: str) -> list[str]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith(("#", "javascript:", "mailto:")):
            continue
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == base_host and parsed.scheme in ("http", "https"):
            links.add(full_url.split("#")[0])
    return list(links)
