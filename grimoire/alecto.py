"""Alecto default credentials database — bundled CSV with search/export."""

import csv
import io
from importlib import resources
from dataclasses import dataclass


@dataclass
class AlectoEntry:
    vendor: str
    username: str
    password: str


_entries: list[AlectoEntry] = []


def _load():
    global _entries
    if _entries:
        return
    try:
        data_file = resources.files("grimoire.data").joinpath("alecto.csv")
        text = data_file.read_text(encoding="utf-8")
    except Exception:
        _entries = []
        return

    reader = csv.reader(io.StringIO(text))
    for i, row in enumerate(reader):
        if len(row) < 3:
            continue
        if i == 0 and row[0].strip().lower() == "vendor":
            continue
        _entries.append(AlectoEntry(
            vendor=row[0].strip(),
            username=row[1].strip(),
            password=row[2].strip(),
        ))


def search(vendor: str) -> list[AlectoEntry]:
    _load()
    vendor = vendor.lower()
    return [e for e in _entries if vendor in e.vendor.lower()]


def dump() -> list[AlectoEntry]:
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
