"""Wordlist statistics and analysis."""

import math
import string
from collections import Counter


def analyze(words: list[str]) -> dict:
    if not words:
        return {"total": 0}

    lengths = [len(w) for w in words]
    charset_counts = {"alpha_only": 0, "numeric_only": 0, "alnum": 0, "has_special": 0, "mixed": 0}

    for w in words:
        has_alpha = any(c.isalpha() for c in w)
        has_digit = any(c.isdigit() for c in w)
        has_special = any(not c.isalnum() for c in w)

        if has_special:
            charset_counts["has_special"] += 1
        if has_alpha and not has_digit and not has_special:
            charset_counts["alpha_only"] += 1
        elif has_digit and not has_alpha and not has_special:
            charset_counts["numeric_only"] += 1
        elif has_alpha and has_digit and not has_special:
            charset_counts["alnum"] += 1
        if has_alpha and has_digit and has_special:
            charset_counts["mixed"] += 1

    length_dist = Counter(lengths)
    patterns = _detect_patterns(words)
    unique = len(set(words))
    duplicates = len(words) - unique

    avg_entropy = sum(_word_entropy(w) for w in words[:1000]) / min(len(words), 1000)

    return {
        "total": len(words),
        "unique": unique,
        "duplicates": duplicates,
        "min_length": min(lengths),
        "max_length": max(lengths),
        "avg_length": sum(lengths) / len(lengths),
        "length_distribution": dict(sorted(length_dist.items())),
        "charset": charset_counts,
        "patterns": patterns,
        "avg_entropy": round(avg_entropy, 2),
    }


def _word_entropy(word: str) -> float:
    if not word:
        return 0.0
    charset_size = 0
    if any(c in string.ascii_lowercase for c in word):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in word):
        charset_size += 26
    if any(c in string.digits for c in word):
        charset_size += 10
    if any(not c.isalnum() for c in word):
        charset_size += 32
    if charset_size == 0:
        return 0.0
    return len(word) * math.log2(charset_size)


def _detect_patterns(words: list[str]) -> dict[str, int]:
    patterns = {"word_number": 0, "capitalized_digits": 0, "all_lower": 0, "all_upper": 0, "leet_speak": 0}
    leet_chars = set("4310572")

    for w in words[:5000]:
        if w.islower():
            patterns["all_lower"] += 1
        elif w.isupper():
            patterns["all_upper"] += 1

        if len(w) > 2 and w[:-1].isalpha() and w[-1].isdigit():
            patterns["word_number"] += 1
        elif len(w) > 2 and w[0].isupper() and any(c.isdigit() for c in w):
            patterns["capitalized_digits"] += 1

        if any(c in leet_chars for c in w) and any(c.isalpha() for c in w):
            patterns["leet_speak"] += 1

    return patterns


def length_histogram(words: list[str], max_bar: int = 40) -> list[str]:
    if not words:
        return ["No words to analyze."]

    lengths = Counter(len(w) for w in words)
    max_count = max(lengths.values())
    lines = []

    for length in sorted(lengths.keys()):
        count = lengths[length]
        bar_len = int(count / max_count * max_bar)
        lines.append(f"  {length:3d} │{'█' * bar_len} {count}")

    return lines
