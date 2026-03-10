"""Output writers — plaintext, JSON, hashcat formats."""

import json
import os


def write_file(words: list[str], path: str, fmt: str = "txt", freq_map: dict | None = None):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    if fmt == "json":
        write_json(words, path, freq_map)
    elif fmt == "hashcat":
        write_hashcat(words, path)
    else:
        write_plaintext(words, path)


def write_plaintext(words: list[str], path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(words) + "\n")


def write_json(words: list[str], path: str, freq_map: dict | None = None):
    freq_map = freq_map or {}
    entries = [{"word": w, "frequency": freq_map.get(w, 0)} for w in words]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def write_hashcat(words: list[str], path: str):
    with open(path, "w", encoding="utf-8") as f:
        for w in words:
            f.write(f":${w}\n")


def sort_by_frequency(freq_map: dict) -> list[str]:
    return sorted(freq_map, key=lambda w: freq_map[w], reverse=True)
