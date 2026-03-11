"""OSINT scraper — extract keywords from public profiles."""

import json
import re
import requests
from bs4 import BeautifulSoup

ALL_PLATFORMS = ["github", "instagram", "x", "linkedin"]

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape_github(username: str) -> dict:
    result = {"bio": "", "repos": [], "keywords": [], "platform": "github"}
    try:
        resp = requests.get(f"https://github.com/{username}", headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "lxml")

        bio_el = soup.select_one(".p-note .js-user-profile-bio-contents")
        if bio_el:
            result["bio"] = bio_el.get_text(strip=True)

        name_el = soup.select_one("span.p-name")
        if name_el:
            result["keywords"].append(name_el.get_text(strip=True))

        location_el = soup.select_one("span.p-label")
        if location_el:
            loc = location_el.get_text(strip=True)
            if loc:
                result["keywords"].extend(_extract_keywords_from_text(loc))

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


def scrape_instagram(username: str) -> dict:
    result = {"bio": "", "name": "", "keywords": [], "platform": "instagram"}
    try:
        resp = requests.get(
            f"https://www.instagram.com/{username}/",
            headers=_HEADERS, timeout=15,
        )
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "html.parser")

        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            desc = og_desc["content"]
            result["bio"] = desc
            result["keywords"].extend(_extract_keywords_from_text(desc))

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
            name_match = re.match(r"^(.+?)\s*[\(@]", title)
            if name_match:
                name = name_match.group(1).strip()
                result["name"] = name
                result["keywords"].extend(name.lower().split())

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict):
                    for field in ("name", "alternateName", "description"):
                        val = data.get(field, "")
                        if val:
                            result["keywords"].extend(_extract_keywords_from_text(str(val)))
            except (json.JSONDecodeError, TypeError):
                pass

        hashtags = re.findall(r"#(\w{3,20})", result["bio"])
        result["keywords"].extend([h.lower() for h in hashtags])

    except Exception:
        pass
    return result


def scrape_twitter(username: str) -> dict:
    result = {"bio": "", "name": "", "location": "", "keywords": [], "platform": "x"}
    try:
        resp = requests.get(
            f"https://x.com/{username}",
            headers=_HEADERS, timeout=15, allow_redirects=True,
        )
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "html.parser")

        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            desc = og_desc["content"]
            result["bio"] = desc
            result["keywords"].extend(_extract_keywords_from_text(desc))

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
            name_match = re.match(r"^(.+?)\s*[\(@]", title)
            if name_match:
                name = name_match.group(1).strip()
                result["name"] = name
                result["keywords"].extend(name.lower().split())

        twitter_desc = soup.find("meta", attrs={"name": "description"})
        if twitter_desc and twitter_desc.get("content"):
            result["keywords"].extend(
                _extract_keywords_from_text(twitter_desc["content"])
            )

        hashtags = re.findall(r"#(\w{3,20})", result.get("bio", ""))
        result["keywords"].extend([h.lower() for h in hashtags])

        mentions = re.findall(r"@(\w{3,15})", result.get("bio", ""))
        result["keywords"].extend([m.lower() for m in mentions])

    except Exception:
        pass
    return result


def scrape_linkedin(username: str) -> dict:
    result = {"headline": "", "name": "", "keywords": [], "platform": "linkedin"}
    try:
        resp = requests.get(
            f"https://www.linkedin.com/in/{username}/",
            headers={**_HEADERS, "Accept-Language": "en-US,en;q=0.9"},
            timeout=15,
        )
        if resp.status_code != 200:
            return result
        soup = BeautifulSoup(resp.text, "html.parser")

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
            result["name"] = title
            parts = re.split(r"[\s\-–|,]+", title)
            result["keywords"].extend(
                [p.lower() for p in parts if len(p) > 2]
            )

        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            desc = og_desc["content"]
            result["headline"] = desc
            result["keywords"].extend(_extract_keywords_from_text(desc))

        twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
        if twitter_title and twitter_title.get("content"):
            result["keywords"].extend(
                _extract_keywords_from_text(twitter_title["content"])
            )

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict):
                    for field in ("name", "jobTitle", "worksFor", "description", "alumniOf"):
                        val = data.get(field, "")
                        if isinstance(val, dict):
                            val = val.get("name", "")
                        if val and isinstance(val, str):
                            result["keywords"].extend(_extract_keywords_from_text(val))
            except (json.JSONDecodeError, TypeError):
                pass

    except Exception:
        pass
    return result


def scrape_generic_page(url: str) -> list[str]:
    keywords = []
    try:
        resp = requests.get(url, timeout=15, headers=_HEADERS)
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


def gather_osint(username: str, platforms: list[str] | None = None) -> list[str]:
    if platforms is None:
        platforms = ALL_PLATFORMS

    all_keywords = set()
    results = {}

    scrapers = {
        "github": scrape_github,
        "instagram": scrape_instagram,
        "x": scrape_twitter,
        "linkedin": scrape_linkedin,
    }

    for platform in platforms:
        scraper = scrapers.get(platform.lower())
        if not scraper:
            continue
        data = scraper(username)
        results[platform] = data
        for kw in data.get("keywords", []):
            if kw and len(kw) > 2:
                all_keywords.add(kw.lower())
        for repo in data.get("repos", []):
            all_keywords.add(repo.lower())

    all_keywords.add(username.lower())

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
        "more", "like", "just", "than", "them", "some", "very",
        "when", "what", "know", "take", "come", "could", "here",
        "then", "other", "also", "back", "after", "only", "these",
        "give", "most", "find", "over", "such", "into", "year",
        "make", "see", "many", "well", "way", "may", "say", "she",
        "him", "his", "how", "its", "let", "too", "use", "who",
        "followers", "following", "posts", "likes", "photos",
        "videos", "instagram", "twitter", "linkedin", "github",
    }
    return [w.lower() for w in words if w.lower() not in stop_words]
