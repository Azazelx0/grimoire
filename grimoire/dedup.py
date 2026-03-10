"""Exact and fuzzy deduplication."""


def exact_dedup(words: list[str]) -> list[str]:
    seen = set()
    result = []
    for w in words:
        if w not in seen:
            seen.add(w)
            result.append(w)
    return result


def fuzzy_dedup(words: list[str], threshold: int = 2) -> list[str]:
    words = sorted(words)
    result = []
    for w in words:
        is_dup = False
        for existing in result[-10:]:
            if _levenshtein(w, existing) <= threshold:
                is_dup = True
                break
        if not is_dup:
            result.append(w)
    return result


def _levenshtein(a: str, b: str) -> int:
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la

    prev = list(range(lb + 1))
    curr = [0] * (lb + 1)

    for i in range(1, la + 1):
        curr[0] = i
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev, curr = curr, prev

    return prev[lb]
