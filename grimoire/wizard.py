"""Interactive wizard — mode selection, sub-wizards, and post-processing using questionary."""

import questionary
from questionary import Style, Choice
from grimoire import banner

GRIMOIRE_STYLE = Style([
    ("qmark", "fg:ansired bold"),
    ("question", "fg:ansiyellow bold"),
    ("answer", "fg:ansigreen bold"),
    ("pointer", "fg:ansired bold"),
    ("highlighted", "fg:ansired bold"),
    ("selected", "fg:ansigreen"),
    ("separator", "fg:ansiyellow"),
    ("instruction", "fg:ansicyan"),
])

MODES = [
    {"name": "🕷  Web Crawl         — Extract words from a URL", "value": "crawl"},
    {"name": "🎯 Profile Target     — CUPP-style personal profiling", "value": "profile"},
    {"name": "📈 Improve Dict       — Mutate an existing wordlist", "value": "improve"},
    {"name": "📥 Download Lists     — Fetch curated wordlists", "value": "download"},
    {"name": "🔐 Default Creds      — Dynamic Default credentials database", "value": "defcreds"},
    {"name": "🔀 Combo Attack       — Merge two wordlists", "value": "combo"},
    {"name": "🎭 Mask Generator     — Pattern-based generation", "value": "mask"},
    {"name": "🔍 OSINT Scraper      — Social media profiling", "value": "osint"},
    {"name": "📡 Wi-Fi Wordlist     — ESSID/vendor-based passwords", "value": "wifi"},
    {"name": "🌍 Locale Packs       — Language-specific passwords", "value": "locale"},
    {"name": "📊 Analyze Wordlist   — Statistics & analysis", "value": "stats"},
    {"name": "🔗 Chain Pipeline     — Multi-step mutations", "value": "chain"},
    {"name": "📝 Run Recipe         — Execute YAML recipe", "value": "recipe"},
    {"name": "🧬 Markov Generator   — Statistical password generation", "value": "markov"},
    questionary.Separator("─────────────────────────────────────────────"),
    {"name": "🔄 Update GRIMOIRE    — Pull latest from GitHub", "value": "update"},
    {"name": "🚪 Exit", "value": "exit"},
]


def run() -> tuple[dict, str]:
    mode = questionary.select(
        "Select mode",
        choices=[
            Choice(m["name"], value=m["value"]) if isinstance(m, dict) else m
            for m in MODES
        ],
        style=GRIMOIRE_STYLE,
    ).ask()

    if not mode or mode == "exit":
        return {}, "exit"

    if mode == "update":
        return {}, "update"

    config = {}
    wizards = {
        "crawl": _crawl_wizard, "profile": _profile_wizard,
        "improve": _improve_wizard, "download": _download_wizard,
        "combo": _combo_wizard, "mask": _mask_wizard,
        "osint": _osint_wizard, "wifi": _wifi_wizard,
        "locale": _locale_wizard, "stats": _stats_wizard,
        "chain": _chain_wizard, "recipe": _recipe_wizard,
        "markov": _markov_wizard, "defcreds": _default_creds_wizard,
    }

    wizard_fn = wizards.get(mode)
    if wizard_fn:
        config = wizard_fn()

    return config, mode


# ──────────────────────────────────────────────────────────────
# SHARED HELPERS — reusable across wizards
# ──────────────────────────────────────────────────────────────


def _mutation_wizard() -> dict:
    """Granular mutation selection with checkboxes."""
    banner.console.print("\n  [bold cyan]── Mutation Options ──[/bold cyan]")
    mutations = questionary.checkbox(
        "Select mutations to apply:",
        choices=[
            Choice("Leet speak (a→@, e→3, ...)", value="leet", checked=True),
            Choice("Case variants (upper, lower, capitalize)", value="case", checked=True),
            Choice("Append numbers (0–99)", value="numbers", checked=True),
            Choice("Append symbols (!@#$%)", value="symbols", checked=False),
            Choice("Append years (2020–2026)", value="years", checked=False),
            Choice("Reverse words", value="reverse", checked=False),
        ],
        style=GRIMOIRE_STYLE,
    ).ask() or []
    return {m: True for m in mutations}


def _policy_wizard() -> dict:
    """Interactive password policy configuration."""
    banner.console.print("\n  [bold cyan]── Password Policy Filter ──[/bold cyan]")
    return {
        "min_length": int(questionary.text("Min password length:", default="8", style=GRIMOIRE_STYLE).ask() or "8"),
        "max_length": int(questionary.text("Max password length (0=unlimited):", default="0", style=GRIMOIRE_STYLE).ask() or "0"),
        "min_upper": int(questionary.text("Required uppercase letters:", default="0", style=GRIMOIRE_STYLE).ask() or "0"),
        "min_lower": int(questionary.text("Required lowercase letters:", default="0", style=GRIMOIRE_STYLE).ask() or "0"),
        "min_digit": int(questionary.text("Required digits:", default="0", style=GRIMOIRE_STYLE).ask() or "0"),
        "min_special": int(questionary.text("Required special characters:", default="0", style=GRIMOIRE_STYLE).ask() or "0"),
    }


def _output_wizard(default_name: str = "output.txt") -> dict:
    """Output file + format selector."""
    return {
        "output": questionary.text("Output file:", default=default_name, style=GRIMOIRE_STYLE).ask() or default_name,
        "format": questionary.select("Output format:", choices=["txt", "json", "hashcat"], style=GRIMOIRE_STYLE).ask() or "txt",
    }


def post_process_menu(words: list[str]) -> list[str]:
    """Post-processing loop — apply mutations, filter, dedup, analyze, export.
    Returns the final wordlist. Loops until user exits or goes back."""
    from grimoire.dedup import exact_dedup, fuzzy_dedup
    from grimoire.mutator.basic import mutate_all
    from grimoire.policy import apply_policy
    from grimoire.stats import analyze, length_histogram
    from grimoire.output import write_file, sort_by_frequency

    while True:
        banner.console.print()
        banner.info(f"Current wordlist: {len(words)} words")

        action = questionary.select(
            "What next?",
            choices=[
                Choice("🧬 Apply Mutations        — leet, case, numbers, symbols", value="mutate"),
                Choice("🛡  Apply Policy Filter    — length, upper, digit, special", value="policy"),
                Choice("🔄 Deduplicate            — exact or fuzzy", value="dedup"),
                Choice("🔀 Sort by Frequency", value="sort"),
                Choice("📊 Show Statistics         — length histogram, entropy", value="stats"),
                Choice("💾 Export to File          — txt, json, hashcat", value="export"),
                Choice("🔁 REPL Shell              — advanced tab-complete shell", value="repl"),
                questionary.Separator("───────────────────────────────────────────"),
                Choice("↩  Back to Main Menu", value="back"),
                Choice("🚪 Exit GRIMOIRE", value="exit"),
            ],
            style=GRIMOIRE_STYLE,
        ).ask()

        if not action or action == "exit":
            banner.info("Exiting GRIMOIRE. Stay sharp.")
            return words

        if action == "back":
            return words

        if action == "repl":
            from grimoire.repl import ReplState, run as run_repl
            run_repl(ReplState(words=words))
            return words

        if action == "mutate":
            opts = _mutation_wizard()
            opts["num_from"] = 0
            opts["num_to"] = 99
            before = len(words)
            words = mutate_all(words, opts)
            words = exact_dedup(words)
            banner.success(f"Mutation: {before} → {len(words)} words")

        elif action == "policy":
            p = _policy_wizard()
            before = len(words)
            words = apply_policy(words, p)
            banner.success(f"Policy: {before} → {len(words)} words (removed {before - len(words)})")

        elif action == "dedup":
            method = questionary.select(
                "Dedup method:",
                choices=["Exact (fast)", "Fuzzy (Levenshtein-based)"],
                style=GRIMOIRE_STYLE,
            ).ask()
            before = len(words)
            if method and "Fuzzy" in method:
                words = fuzzy_dedup(words, 2)
            else:
                words = exact_dedup(words)
            banner.success(f"Dedup: {before} → {len(words)} (removed {before - len(words)})")

        elif action == "sort":
            freq = {}
            for w in words:
                freq[w] = freq.get(w, 0) + 1
            words = sort_by_frequency(freq)
            banner.success(f"Sorted {len(words)} words by frequency")

        elif action == "stats":
            if not words:
                banner.warning("No words to analyze.")
                continue
            from rich.table import Table
            stats = analyze(words)
            table = Table(title="Wordlist Statistics", border_style="cyan")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="bold white")
            table.add_row("Total words", f"{stats['total']:,}")
            table.add_row("Unique", f"{stats['unique']:,}")
            table.add_row("Duplicates", f"{stats['duplicates']:,}")
            table.add_row("Min length", str(stats["min_length"]))
            table.add_row("Max length", str(stats["max_length"]))
            table.add_row("Avg length", f"{stats['avg_length']:.1f}")
            table.add_row("Avg entropy", f"{stats['avg_entropy']} bits")
            banner.console.print()
            banner.console.print(table)
            banner.console.print()
            banner.dim("Length distribution:")
            for line in length_histogram(words):
                banner.console.print(line)

        elif action == "export":
            out = _output_wizard()
            try:
                freq = {}
                for w in words:
                    freq[w] = freq.get(w, 0) + 1
                write_file(words, out["output"], out["format"], freq)
                banner.success(f"Exported {len(words)} words to {out['output']}")
            except Exception as e:
                banner.error(f"Export failed: {e}")

    return words


# ──────────────────────────────────────────────────────────────
# SUB-WIZARDS — one per mode
# ──────────────────────────────────────────────────────────────


def _crawl_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Web Crawl Configuration ──[/bold cyan]\n")
    url = questionary.text("Target URL:", style=GRIMOIRE_STYLE).ask() or ""
    mode = questionary.select("Crawl mode:", choices=["auto", "static", "headless"], style=GRIMOIRE_STYLE).ask() or "auto"
    depth = int(questionary.text("Crawl depth (1-10):", default="2", style=GRIMOIRE_STYLE).ask() or "2")
    min_length = int(questionary.text("Min word length:", default="5", style=GRIMOIRE_STYLE).ask() or "5")
    max_length = int(questionary.text("Max word length (0=unlimited):", default="0", style=GRIMOIRE_STYLE).ask() or "0")

    extract_opts = questionary.checkbox(
        "What to extract:",
        choices=[
            Choice("Email addresses", value="emails", checked=True),
            Choice("HTML metadata (title, meta, alt)", value="meta", checked=True),
            Choice("JavaScript string literals", value="js", checked=False),
        ],
        style=GRIMOIRE_STYLE,
    ).ask() or []

    advanced = questionary.confirm("Configure advanced options? (proxy, cookies, auth)", default=False, style=GRIMOIRE_STYLE).ask()
    proxy, cookie, header, selector = "", "", "", ""
    random_ua, delay = False, 0
    if advanced:
        proxy = questionary.text("Proxy URL (empty=none):", default="", style=GRIMOIRE_STYLE).ask() or ""
        cookie = questionary.text("Cookie string (empty=none):", default="", style=GRIMOIRE_STYLE).ask() or ""
        header = questionary.text("Custom header 'Key: Value' (empty=none):", default="", style=GRIMOIRE_STYLE).ask() or ""
        selector = questionary.text("CSS selector to target (empty=all):", default="", style=GRIMOIRE_STYLE).ask() or ""
        random_ua = questionary.confirm("Rotate User-Agent?", default=True, style=GRIMOIRE_STYLE).ask()
        delay = int(questionary.text("Request delay ms:", default="200", style=GRIMOIRE_STYLE).ask() or "0")

    do_mutate = questionary.confirm("Apply mutations after crawl?", default=False, style=GRIMOIRE_STYLE).ask()
    mutations = {}
    rule_file = ""
    if do_mutate:
        mutations = _mutation_wizard()
        use_rules = questionary.confirm("Use a Hashcat .rule file?", default=False, style=GRIMOIRE_STYLE).ask()
        if use_rules:
            rule_file = questionary.text("Rule file path:", style=GRIMOIRE_STYLE).ask() or ""

    out = _output_wizard("crawl-output.txt")
    return {
        "url": url, "mode": mode, "depth": depth,
        "min_length": min_length, "max_length": max_length,
        "emails": "emails" in extract_opts,
        "meta": "meta" in extract_opts,
        "js": "js" in extract_opts,
        "proxy": proxy, "cookie": cookie, "header": header,
        "selector": selector, "random_ua": random_ua, "delay": delay,
        "mutate": do_mutate, "mutations": mutations,
        "rule_file": rule_file,
        **out,
    }


def _profile_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Target Profile (CUPP-style) ──[/bold cyan]\n")
    first = questionary.text("Target's first name:", style=GRIMOIRE_STYLE).ask() or ""
    last = questionary.text("Target's last name:", style=GRIMOIRE_STYLE).ask() or ""
    nick = questionary.text("Target's nickname:", style=GRIMOIRE_STYLE).ask() or ""
    dob = questionary.text("Birthdate (DD/MM/YYYY or YYYY):", style=GRIMOIRE_STYLE).ask() or ""
    partner = questionary.text("Partner's name (empty=skip):", style=GRIMOIRE_STYLE).ask() or ""
    partner_nick = questionary.text("Partner's nickname:", style=GRIMOIRE_STYLE).ask() or ""
    partner_dob = questionary.text("Partner's birthdate:", style=GRIMOIRE_STYLE).ask() or ""
    pet = questionary.text("Pet's name:", style=GRIMOIRE_STYLE).ask() or ""
    company = questionary.text("Company/organization:", style=GRIMOIRE_STYLE).ask() or ""
    kws = questionary.text("Custom keywords (comma-separated):", style=GRIMOIRE_STYLE).ask() or ""

    out = _output_wizard("profile-wordlist.txt")
    return {
        "first_name": first, "last_name": last, "nickname": nick,
        "birthdate": dob, "partner_name": partner,
        "partner_nickname": partner_nick, "partner_birthday": partner_dob,
        "pet_name": pet, "company": company,
        "keywords": [k.strip() for k in kws.split(",") if k.strip()],
        **out,
    }


def _improve_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Dictionary Improver ──[/bold cyan]\n")
    input_file = questionary.text("Input wordlist file:", style=GRIMOIRE_STYLE).ask() or ""
    mutations = _mutation_wizard()
    use_rules = questionary.confirm("Apply a Hashcat .rule file?", default=False, style=GRIMOIRE_STYLE).ask()
    rule_file = ""
    if use_rules:
        rule_file = questionary.text("Rule file path:", style=GRIMOIRE_STYLE).ask() or ""
    fuzzy = questionary.confirm("Use fuzzy dedup?", default=False, style=GRIMOIRE_STYLE).ask()
    out = _output_wizard("improved.txt")
    return {
        "input_file": input_file,
        "rule_file": rule_file,
        "fuzzy_dedup": fuzzy,
        **mutations, **out,
    }


def _download_wizard() -> dict:
    from grimoire.downloader import list_categories
    cats = list_categories()
    return {
        "category": questionary.select("Select category:", choices=cats, style=GRIMOIRE_STYLE).ask() or cats[0],
    }


def _default_creds_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Default Credentials ──[/bold cyan]\n")
    action = questionary.select(
        "What to do?",
        choices=[
            Choice("🔍 Search by vendor", value="search"),
            Choice("📋 List all vendors", value="list"),
            Choice("📦 Dump all entries", value="dump"),
            Choice("💾 Export to file", value="export"),
        ],
        style=GRIMOIRE_STYLE,
    ).ask() or "dump"

    config = {"action": action}
    if action == "search":
        config["vendor"] = questionary.text("Vendor name to search:", style=GRIMOIRE_STYLE).ask() or ""
    elif action == "list":
        from grimoire import default_creds as dc
        vendors = dc.vendors()
        vendor = questionary.select(
            "Select a vendor to view:",
            choices=vendors,
            style=GRIMOIRE_STYLE,
            use_indicator=True
        ).ask()
        if vendor:
            config["action"] = "search"
            config["vendor"] = vendor
        else:
            config["action"] = "none" # user aborted
    elif action == "export":
        config["export_type"] = questionary.select(
            "Export what?",
            choices=["Usernames only", "Passwords only", "Both (CSV format)"],
            style=GRIMOIRE_STYLE,
        ).ask() or "Both (CSV format)"
        config["output"] = questionary.text("Output file:", default="defcreds-export.txt", style=GRIMOIRE_STYLE).ask() or "defcreds-export.txt"
    return config


def _combo_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Combo Attack ──[/bold cyan]\n")
    f1 = questionary.text("First wordlist file:", style=GRIMOIRE_STYLE).ask() or ""
    f2 = questionary.text("Second wordlist file:", style=GRIMOIRE_STYLE).ask() or ""
    sep = questionary.text("Separator between words (empty=none):", default="", style=GRIMOIRE_STYLE).ask() or ""
    out = _output_wizard("combo.txt")
    return {"file1": f1, "file2": f2, "separator": sep, **out}


def _mask_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Mask Generator ──[/bold cyan]\n")
    banner.dim("Charsets: ?l=lower ?u=upper ?d=digit ?s=special ?a=all")
    mask = questionary.text("Mask pattern:", default="?u?l?l?l?d?d?d?d", style=GRIMOIRE_STYLE).ask() or "?u?l?l?l?d?d?d?d"

    from grimoire.mask import estimate_size
    est = estimate_size(mask)
    banner.info(f"Estimated combinations: {est:,}")

    max_out = int(questionary.text("Max words to generate:", default="100000", style=GRIMOIRE_STYLE).ask() or "100000")
    out = _output_wizard("mask-output.txt")
    return {"mask": mask, "max_output": max_out, **out}


def _osint_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── OSINT Scraper ──[/bold cyan]\n")
    platform_choices = [
        Choice("GitHub", value="github", checked=True),
        Choice("Instagram", value="instagram", checked=True),
        Choice("X (Twitter)", value="x", checked=True),
        Choice("LinkedIn", value="linkedin", checked=True),
    ]
    selected = questionary.checkbox(
        "Select platforms to scrape:",
        choices=platform_choices,
        style=GRIMOIRE_STYLE,
    ).ask() or ["github", "instagram", "x", "linkedin"]
    username = questionary.text("Target username:", style=GRIMOIRE_STYLE).ask() or ""
    out = _output_wizard("osint-words.txt")
    return {"username": username, "platforms": selected, **out}


def _wifi_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Wi-Fi Wordlist Generator ──[/bold cyan]\n")
    essid = questionary.text("Wi-Fi ESSID (network name):", style=GRIMOIRE_STYLE).ask() or ""
    vendor = questionary.text("Router vendor (e.g. netgear, tp-link):", style=GRIMOIRE_STYLE).ask() or ""
    out = _output_wizard("wifi-words.txt")
    return {"essid": essid, "vendor": vendor, **out}


def _locale_wizard() -> dict:
    from grimoire.locale_packs import list_locales
    locales = list_locales()
    choices = [f"{code} — {name}" for code, name in locales.items()]
    selected = questionary.checkbox("Select locales:", choices=choices, style=GRIMOIRE_STYLE).ask() or []
    codes = [s.split(" — ")[0] for s in selected]
    out = _output_wizard("locale-words.txt")
    return {"locales": codes, **out}


def _stats_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Wordlist Analysis ──[/bold cyan]\n")
    return {
        "input_file": questionary.text("Wordlist file to analyze:", style=GRIMOIRE_STYLE).ask() or "",
    }


def _chain_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Chain Pipeline ──[/bold cyan]\n")
    banner.dim("Example: leet -> numbers(0-99) -> policy(min:8)")

    build_mode = questionary.select(
        "How to define chain?",
        choices=[
            Choice("Type chain string manually", value="manual"),
            Choice("Build step-by-step (interactive)", value="interactive"),
        ],
        style=GRIMOIRE_STYLE,
    ).ask() or "manual"

    chain_str = ""
    if build_mode == "manual":
        chain_str = questionary.text("Chain steps:", style=GRIMOIRE_STYLE).ask() or ""
    else:
        steps = []
        available = ["leet", "case", "numbers", "symbols", "years", "reverse", "dedup", "policy"]
        while True:
            step = questionary.select(
                f"Add step ({len(steps)} so far):",
                choices=[Choice(s, value=s) for s in available] + [Choice("✅ Done building", value="done")],
                style=GRIMOIRE_STYLE,
            ).ask()
            if step == "done" or not step:
                break
            if step == "numbers":
                rng = questionary.text("Range (e.g. 0-99):", default="0-99", style=GRIMOIRE_STYLE).ask() or "0-99"
                steps.append(f"numbers({rng})")
            elif step == "policy":
                p = questionary.text("Policy (e.g. min:8 upper:1):", default="min:8", style=GRIMOIRE_STYLE).ask() or "min:8"
                steps.append(f"policy({p})")
            else:
                steps.append(step)
        chain_str = " -> ".join(steps)
        if chain_str:
            banner.info(f"Chain: {chain_str}")

    input_file = questionary.text("Input wordlist:", style=GRIMOIRE_STYLE).ask() or ""
    out = _output_wizard("chain-output.txt")
    return {"input_file": input_file, "chain": chain_str, **out}


def _recipe_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Recipe Runner ──[/bold cyan]\n")
    return {
        "recipe_file": questionary.text("Recipe YAML file:", style=GRIMOIRE_STYLE).ask() or "",
    }


def _markov_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Markov Generator ──[/bold cyan]\n")
    train_file = questionary.text("Training wordlist file:", style=GRIMOIRE_STYLE).ask() or ""
    count = int(questionary.text("Words to generate:", default="10000", style=GRIMOIRE_STYLE).ask() or "10000")
    min_len = int(questionary.text("Min word length:", default="6", style=GRIMOIRE_STYLE).ask() or "6")
    max_len = int(questionary.text("Max word length:", default="16", style=GRIMOIRE_STYLE).ask() or "16")
    out = _output_wizard("markov-output.txt")
    return {
        "train_file": train_file, "count": count,
        "min_len": min_len, "max_len": max_len,
        **out,
    }
