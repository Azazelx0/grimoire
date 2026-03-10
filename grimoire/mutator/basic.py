"""Basic word mutations — leet, case, numbers, symbols, years, reverse, duplicate."""

LEET_MAP = str.maketrans("aeiostzg", "43105729")

SYMBOLS = ["!", "@", "#", "$", "%", "&", "*", ".", "-", "_"]

YEARS = [str(y) for y in range(2020, 2031)] + [str(y) for y in range(1990, 2006)]


def leet(word: str) -> str:
    return word.lower().translate(LEET_MAP)


def case_variants(word: str) -> list[str]:
    results = [word.lower(), word.upper()]
    if word:
        results.append(word[0].upper() + word[1:].lower())
        results.append(word[0].lower() + word[1:].upper())
    return results


def append_numbers(word: str, start: int = 0, end: int = 99) -> list[str]:
    return [f"{word}{i}" for i in range(start, end + 1)]


def prepend_numbers(word: str, start: int = 0, end: int = 99) -> list[str]:
    return [f"{i}{word}" for i in range(start, end + 1)]


def append_symbols(word: str, symbols: list[str] | None = None) -> list[str]:
    symbols = symbols or SYMBOLS
    return [word + s for s in symbols]


def prepend_symbols(word: str, symbols: list[str] | None = None) -> list[str]:
    symbols = symbols or SYMBOLS
    return [s + word for s in symbols]


def reverse(word: str) -> str:
    return word[::-1]


def duplicate(word: str) -> str:
    return word + word


def append_years(word: str, years: list[str] | None = None) -> list[str]:
    years = years or YEARS
    return [word + y for y in years]


def mutate_word(word: str, opts: dict) -> list[str]:
    seen = {word}
    results = [word]

    def add(w):
        if w and w not in seen:
            seen.add(w)
            results.append(w)

    if opts.get("leet"):
        add(leet(word))
    if opts.get("case"):
        for v in case_variants(word):
            add(v)
    if opts.get("reverse"):
        add(reverse(word))
    if opts.get("duplicate"):
        add(duplicate(word))
    if opts.get("numbers"):
        for v in append_numbers(word, opts.get("num_from", 0), opts.get("num_to", 99)):
            add(v)
    if opts.get("prepend_numbers"):
        for v in prepend_numbers(word, opts.get("num_from", 0), opts.get("num_to", 99)):
            add(v)
    if opts.get("symbols"):
        for v in append_symbols(word, opts.get("symbol_chars")):
            add(v)
    if opts.get("prepend_symbols"):
        for v in prepend_symbols(word, opts.get("symbol_chars")):
            add(v)
    if opts.get("years"):
        for v in append_years(word, opts.get("year_list")):
            add(v)
    return results


def mutate_all(words: list[str], opts: dict) -> list[str]:
    seen = set()
    results = []
    for w in words:
        for m in mutate_word(w, opts):
            if m not in seen:
                seen.add(m)
                results.append(m)
    return results


DEFAULT_OPTS = {
    "leet": True, "case": True, "numbers": True, "symbols": True,
    "reverse": True, "duplicate": True, "years": True,
    "num_from": 0, "num_to": 99,
}
