"""YAML recipe system — execute multi-step wordlist generation pipelines."""

import yaml


def load_recipe(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def execute_recipe(recipe: dict, on_step=None) -> list[str]:
    from grimoire.profiler import generate as profile_generate
    from grimoire.mutator.basic import mutate_all
    from grimoire.dedup import exact_dedup
    from grimoire.policy import apply_policy
    from grimoire.crawler.static import crawl_static
    from grimoire.output import write_file

    words = []
    steps = recipe.get("steps", [])

    for i, step in enumerate(steps):
        if on_step:
            on_step(i + 1, len(steps), step)

        if "crawl" in step:
            cfg = step["crawl"]
            result = crawl_static(
                url=cfg.get("url", ""),
                depth=cfg.get("depth", 2),
                min_length=cfg.get("min_length", 5),
                emails=cfg.get("emails", False),
                meta=cfg.get("meta", True),
            )
            words.extend(result.word_list())

        elif "profile" in step:
            cfg = step["profile"]
            profile_data = {
                "first_name": cfg.get("name", ""),
                "last_name": cfg.get("last", ""),
                "nickname": cfg.get("nick", ""),
                "birthdate": cfg.get("dob", ""),
                "partner_name": cfg.get("partner", ""),
                "pet_name": cfg.get("pet", ""),
                "company": cfg.get("company", ""),
                "keywords": cfg.get("keywords", []),
                "leet": True, "special_chars": True,
            }
            words.extend(profile_generate(profile_data))

        elif "mutate" in step:
            mutations = step["mutate"]
            if isinstance(mutations, list):
                opts = {m: True for m in mutations}
                opts.setdefault("num_from", 0)
                opts.setdefault("num_to", 99)
                words = mutate_all(words, opts)

        elif "policy" in step:
            cfg = step["policy"]
            words = apply_policy(words, cfg)

        elif "dedup" in step:
            words = exact_dedup(words)

        elif "export" in step:
            path = step["export"]
            fmt = "txt"
            if path.endswith(".json"):
                fmt = "json"
            elif path.endswith(".hc"):
                fmt = "hashcat"
            write_file(words, path, fmt)

    words = exact_dedup(words)
    return words
