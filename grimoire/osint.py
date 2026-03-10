"""OSINT scraper — extract keywords from public profiles."""

import re
import requests
from bs4 import BeautifulSoup


def scrape_github(username: str) -> dict:
    result = {"bio": "", "repos": [], "keywords": []}
    try:
        resp = requests.get(f"https://github.com/{username}", timeout=15)
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "lxml")

        bio_el = soup.select_one(".p-note .js-user-profile-bio-contents")
        if bio_el:
            result["bio"] = bio_el.get_text(strip=True)

        name_el = soup.select_one("span.p-name")
        if name_el:
            result["keywords"].append(name_el.get_text(strip=True))

        for repo in soup.select("a[itemprop='name codeRepository']"):
            repo_name = repo.get_text(strip=True)
            if repo_name:
                result["repos"].append(repo_name)
                result["keywords"].extend(_split_repo_name(repo_name))

        if result["bio"]:
            result["keywords"].extend(_extract_keywords_from_text(result["bio"]))

    except Exception:
        pass
    return result


def scrape_generic_page(url: str) -> list[str]:
    keywords = []
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        if resp.status_code != 200:
            return keywords
        soup = BeautifulSoup(resp.text, "lxml")

        for tag in soup.find_all(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator=" ")
        keywords = _extract_keywords_from_text(text)
    except Exception:
        pass
    return keywords


def gather_osint(username: str) -> list[str]:
    all_keywords = set()

    github = scrape_github(username)
    for kw in github.get("keywords", []):
        if kw and len(kw) > 2:
            all_keywords.add(kw.lower())
    for repo in github.get("repos", []):
        all_keywords.add(repo.lower())

    return sorted(all_keywords)


def _split_repo_name(name: str) -> list[str]:
    parts = re.split(r"[-_.]", name)
    return [p.lower() for p in parts if p and len(p) > 2]


def _extract_keywords_from_text(text: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z]{3,15}\b", text)
    stop_words = {
        "the", "and", "for", "are", "but", "not", "you", "all",
        "can", "had", "her", "was", "one", "our", "out", "has",
        "this", "that", "with", "have", "from", "will", "your",
        "been", "said", "each", "which", "their", "about", "would",
    }
    return [w.lower() for w in words if w.lower() not in stop_words]
