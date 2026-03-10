"""Mask/pattern-based password generator (like Hashcat masks)."""

import itertools
import string

CHARSETS = {
    "?l": string.ascii_lowercase,
    "?u": string.ascii_uppercase,
    "?d": string.digits,
    "?s": "!@#$%^&*()-_=+[]{}|;:',.<>?/`~",
    "?a": string.ascii_letters + string.digits + "!@#$%^&*()-_=+",
}


def parse_mask(mask: str, custom_charsets: dict | None = None) -> list[str]:
    charsets = {**CHARSETS}
    if custom_charsets:
        charsets.update(custom_charsets)

    groups = []
    i = 0
    while i < len(mask):
        if i + 1 < len(mask) and mask[i] == "?":
            token = mask[i:i + 2]
            if token in charsets:
                groups.append(charsets[token])
                i += 2
                continue
        groups.append(mask[i])
        i += 1

    return groups


def generate_from_mask(mask: str, custom_charsets: dict | None = None,
                       max_output: int = 100000) -> list[str]:
    groups = parse_mask(mask, custom_charsets)

    total = 1
    for g in groups:
        total *= len(g)
        if total > max_output:
            break

    results = []
    count = 0
    for combo in itertools.product(*groups):
        if count >= max_output:
            break
        results.append("".join(combo))
        count += 1

    return results


def estimate_size(mask: str, custom_charsets: dict | None = None) -> int:
    groups = parse_mask(mask, custom_charsets)
    total = 1
    for g in groups:
        total *= len(g)
    return total
