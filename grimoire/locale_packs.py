"""Language/locale-specific common password packs."""

from importlib import resources

BUILTIN_LOCALES = {
    "en": "English",
    "tr": "Turkish",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "ar": "Arabic (transliterated)",
}


def list_locales() -> dict[str, str]:
    return dict(BUILTIN_LOCALES)


def load_locale(locale_code: str) -> list[str]:
    try:
        data_file = resources.files("grimoire.data.locales").joinpath(f"{locale_code}.txt")
        text = data_file.read_text(encoding="utf-8")
        return [w.strip() for w in text.splitlines() if w.strip()]
    except Exception:
        return []


def load_multiple(locale_codes: list[str]) -> list[str]:
    seen = set()
    results = []
    for code in locale_codes:
        for word in load_locale(code):
            if word not in seen:
                seen.add(word)
                results.append(word)
    return results
