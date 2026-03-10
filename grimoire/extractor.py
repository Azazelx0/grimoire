"""HTML content extractor — words, emails, metadata, JS strings."""

import re
from collections import Counter
from bs4 import BeautifulSoup
from dataclasses import dataclass, field


@dataclass
class ExtractionResult:
    words: Counter = field(default_factory=Counter)
    emails: set = field(default_factory=set)
    metadata: dict = field(default_factory=dict)

    def merge(self, other: "ExtractionResult"):
        self.words.update(other.words)
        self.emails |= other.emails
        self.metadata.update(other.metadata)

    def word_list(self) -> list[str]:
        return list(self.words.keys())


EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
JS_STRING_RE = re.compile(r"""(?:"|')([^"']{2,})(?:"|')""")
WORD_SPLIT_RE = re.compile(r"[^a-zA-Z0-9'\-]+")


def extract(html_content: str, min_length: int = 5, max_length: int = 0,
            emails: bool = False, meta: bool = False, js_strings: bool = False,
            css_selector: str = "") -> ExtractionResult:
    result = ExtractionResult()
    soup = BeautifulSoup(html_content, "lxml")

    if meta:
        _extract_meta(soup, result)

    text_parts = []
    script_parts = []

    if css_selector:
        elements = soup.select(css_selector)
        for el in elements:
            text_parts.append(el.get_text(separator=" "))
    else:
        for tag in soup.find_all(["script", "style", "noscript"]):
            if js_strings and tag.name == "script" and tag.string:
                script_parts.append(tag.string)
            tag.decompose()

        for img in soup.find_all("img", alt=True):
            if img["alt"]:
                text_parts.append(img["alt"])

        text_parts.append(soup.get_text(separator=" "))

    full_text = " ".join(text_parts)
    _extract_words(full_text, result, min_length, max_length)

    if emails:
        _extract_emails(html_content, result)

    if js_strings:
        for script in script_parts:
            _extract_js_strings(script, result, min_length, max_length)

    return result


def extract_from_text(text: str, min_length: int = 5, max_length: int = 0) -> ExtractionResult:
    result = ExtractionResult()
    _extract_words(text, result, min_length, max_length)
    return result


def _extract_words(text: str, result: ExtractionResult, min_len: int, max_len: int):
    words = WORD_SPLIT_RE.split(text)
    for w in words:
        w = w.strip("'\".,;:!?()[]{}|/\\<>-_=+ \t\n\r")
        if not w:
            continue
        if min_len > 0 and len(w) < min_len:
            continue
        if max_len > 0 and len(w) > max_len:
            continue
        result.words[w.lower()] += 1


def _extract_emails(text: str, result: ExtractionResult):
    for match in EMAIL_RE.findall(text):
        result.emails.add(match.lower())


def _extract_meta(soup: BeautifulSoup, result: ExtractionResult):
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        result.metadata["title"] = title_tag.string.strip()

    for meta_tag in soup.find_all("meta"):
        name = meta_tag.get("name", meta_tag.get("property", "")).lower()
        content = meta_tag.get("content", "")
        if name and content:
            result.metadata[name] = content


def _extract_js_strings(script: str, result: ExtractionResult, min_len: int, max_len: int):
    for match in JS_STRING_RE.findall(script):
        s = match.strip()
        if len(s) < 3 or len(s) > 100:
            continue
        if any(c in s for c in "{}();=<>"):
            continue
        letter_count = sum(1 for c in s if c.isalpha())
        if letter_count <= len(s) // 2:
            continue
        words = WORD_SPLIT_RE.split(s)
        for w in words:
            w = w.strip()
            if not w or len(w) < 3:
                continue
            if min_len > 0 and len(w) < min_len:
                continue
            if max_len > 0 and len(w) > max_len:
                continue
            result.words[w.lower()] += 1
