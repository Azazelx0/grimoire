"""CUPP-style target profiler — generates personalized wordlists from personal data."""

from grimoire.mutator.basic import leet


def generate(profile: dict) -> list[str]:
    base_words = []

    def add_if(val):
        if isinstance(val, str) and val.strip():
            base_words.append(val.strip().lower())
        elif isinstance(val, list):
            for v in val:
                if v and v.strip():
                    base_words.append(v.strip().lower())

    add_if(profile.get("first_name"))
    add_if(profile.get("last_name"))
    add_if(profile.get("nickname"))
    add_if(profile.get("partner_name"))
    add_if(profile.get("partner_nickname"))
    add_if(profile.get("pet_name"))
    add_if(profile.get("company"))
    add_if(profile.get("keywords"))

    date_parts = _extract_date_parts(profile.get("birthdate", ""))
    partner_date_parts = _extract_date_parts(profile.get("partner_birthday", ""))

    seen = set()
    results = []

    def add(w):
        w = w.strip()
        if w and w not in seen:
            seen.add(w)
            results.append(w)

    for w in base_words:
        add(w)
        if w:
            add(w[0].upper() + w[1:])

    for w in base_words:
        for dp in date_parts + partner_date_parts:
            add(w + dp)
            add(dp + w)
            if w:
                add((w[0].upper() + w[1:]) + dp)

    for i, w1 in enumerate(base_words):
        for j, w2 in enumerate(base_words):
            if i != j:
                add(w1 + w2)
                add(w2 + w1)
                add(w1 + "_" + w2)
                add(w1 + "." + w2)

    for w in base_words:
        for i in range(100):
            add(f"{w}{i}")
            add(f"{w}{i:02d}")
        for i in (111, 222, 333, 444, 555, 666, 777, 888, 999):
            add(f"{w}{i}")
        add(w + "123")
        add(w + "1234")
        add(w + "12345")

    if profile.get("leet", True):
        snapshot = list(results)
        for w in snapshot:
            add(leet(w))

    if profile.get("special_chars", True):
        snapshot = list(results)
        for w in snapshot:
            for sym in ("!", "@", "#", "$", "*", ".", "?"):
                add(w + sym)

    return results


def _extract_date_parts(date_str: str) -> list[str]:
    date_str = date_str.strip()
    if not date_str:
        return []

    parts = []
    segments = []
    for sep in ("/", "-", "."):
        if sep in date_str:
            segments = date_str.split(sep)
            break

    if len(segments) == 3:
        day, month, year = segments[0], segments[1], segments[2]
        parts.extend([year, day + month, month + year, day + month + year])
        if len(year) == 4:
            parts.extend([year[2:], day + month + year[2:]])
    elif len(date_str) == 4:
        parts.extend([date_str, date_str[2:]])
    else:
        parts.append(date_str)

    return parts
