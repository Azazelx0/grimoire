"""Dictionary improver — enhance existing wordlists with mutations."""

from grimoire.mutator.basic import mutate_all
from grimoire.mutator.rules import parse_rule_file, apply_rules
from grimoire.dedup import exact_dedup, fuzzy_dedup


def improve(input_path: str, opts: dict) -> list[str]:
    words = []
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)

    mut_opts = {
        "leet": opts.get("leet", True),
        "case": opts.get("case", True),
        "numbers": opts.get("numbers", True),
        "symbols": opts.get("symbols", True),
        "reverse": opts.get("reverse", False),
        "duplicate": opts.get("duplicate", False),
        "years": opts.get("years", True),
        "num_from": 0,
        "num_to": 99,
    }

    enhanced = mutate_all(words, mut_opts)

    rule_file = opts.get("rule_file", "")
    if rule_file:
        try:
            rules = parse_rule_file(rule_file)
            if rules:
                rule_results = apply_rules(words, rules)
                enhanced.extend(rule_results)
        except Exception:
            pass

    if opts.get("fuzzy_dedup"):
        enhanced = fuzzy_dedup(enhanced, 2)
    else:
        enhanced = exact_dedup(enhanced)

    return enhanced
