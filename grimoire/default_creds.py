"""Dynamic Default Credentials — fetches from online sources with local fallback."""

import csv
import io
import requests
from importlib import resources
from dataclasses import dataclass
from grimoire import banner as b


@dataclass
class CredEntry:
    vendor: str
    username: str
    password: str


_entries: list[CredEntry] = []
_fetched: bool = False

# Known reliable CSV mirrors for default credentials
SOURCES = [
    "https://raw.githubusercontent.com/ihebski/DefaultCreds-cheat-sheet/main/DefaultCreds-Cheat-Sheet.csv"
]


def _load():
    """Load credentials from remote sources, falling back to local csv."""
    global _entries, _fetched
    if _fetched:
        return

    fetched_text = ""
    for url in SOURCES:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                fetched_text = resp.text
                break
        except requests.RequestException:
            continue

    if fetched_text:
        # Parse the remote CSV
        reader = csv.reader(io.StringIO(fetched_text))
        for i, row in enumerate(reader):
            if len(row) < 3:
                continue
            # ihebski's CSV format: product, username, password, role, comments
            if i == 0 and "product" in row[0].lower() or "vendor" in row[0].lower():
                continue
            
            _entries.append(CredEntry(
                vendor=row[0].strip(),
                username=row[1].strip(),
                password=row[2].strip()
            ))
        _fetched = True
        return

    # Fallback to local
    b.warning("Could not fetch remote default credentials. Using local fallback.")
    try:
        data_file = resources.files("grimoire.data").joinpath("alecto.csv")
        text = data_file.read_text(encoding="utf-8")
        reader = csv.reader(io.StringIO(text))
        for i, row in enumerate(reader):
            if len(row) < 3:
                continue
            if i == 0 and row[0].strip().lower() == "vendor":
                continue
            _entries.append(CredEntry(
                vendor=row[0].strip(),
                username=row[1].strip(),
                password=row[2].strip(),
            ))
    except Exception as e:
        b.error(f"Fallback loading failed: {e}")
        _entries = []
    
    _fetched = True


def search(vendor: str) -> list[CredEntry]:
    _load()
    vendor = vendor.lower()
    return [e for e in _entries if vendor in e.vendor.lower()]


def dump() -> list[CredEntry]:
    _load()
    return list(_entries)


def export_words() -> list[str]:
    _load()
    seen = set()
    words = []
    for e in _entries:
        for w in (e.username, e.password):
            if w and w not in seen:
                seen.add(w)
                words.append(w)
    return words


def vendors() -> list[str]:
    _load()
    return sorted(set(e.vendor for e in _entries))
