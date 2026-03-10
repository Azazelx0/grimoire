"""Combo/hybrid attack — merge two wordlists by concatenation."""


def combo_attack(words1: list[str], words2: list[str], separator: str = "") -> list[str]:
    seen = set()
    results = []
    for w1 in words1:
        for w2 in words2:
            combined = f"{w1}{separator}{w2}"
            if combined not in seen:
                seen.add(combined)
                results.append(combined)
    return results


def combo_from_files(path1: str, path2: str, separator: str = "") -> list[str]:
    words1 = _read_wordlist(path1)
    words2 = _read_wordlist(path2)
    return combo_attack(words1, words2, separator)


def _read_wordlist(path: str) -> list[str]:
    words = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)
    return words
