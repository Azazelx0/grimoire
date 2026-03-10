"""GRIMOIRE CLI — Click-based command-line interface."""

import click
from grimoire import banner as b
from grimoire.repl import ReplState, run as run_repl


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--url", default="", help="Target URL to crawl")
@click.option("--file", "input_file", default="", help="Local file to extract words from")
@click.option("--mode", default="auto", type=click.Choice(["auto", "static", "headless"]), help="Crawl mode")
@click.option("--depth", default=2, help="Crawl depth")
@click.option("--min-length", default=5, help="Minimum word length")
@click.option("--max-length", default=0, help="Maximum word length (0=unlimited)")
@click.option("--emails/--no-emails", default=False, help="Extract email addresses")
@click.option("--meta/--no-meta", default=False, help="Extract metadata")
@click.option("--js/--no-js", default=False, help="Extract JS strings")
@click.option("--selector", default="", help="CSS selector for extraction")
@click.option("--cookie", default="", help="Cookie string to inject")
@click.option("--header", default="", help="Custom HTTP header")
@click.option("--proxy", default="", help="Proxy URL")
@click.option("--random-ua/--no-random-ua", default=False, help="Rotate User-Agent")
@click.option("--delay", default=0, help="Request delay in ms")
@click.option("--mutate/--no-mutate", default=False, help="Enable mutations")
@click.option("--leet/--no-leet", default=False, help="Leet speak mutations")
@click.option("--case/--no-case", default=False, help="Case variants")
@click.option("--append-numbers/--no-append-numbers", default=False, help="Append numbers")
@click.option("--append-symbols/--no-append-symbols", default=False, help="Append symbols")
@click.option("--rule-file", default="", help="Hashcat .rule file path")
@click.option("--profile", default="", help='Target profile: "name=John dob=1990 pet=Rex"')
@click.option("--alecto", "alecto_search", default=None, help="Search Alecto DB (vendor name)")
@click.option("--improve", "improve_file", default="", help="Improve existing wordlist")
@click.option("--download", "download_cat", default="", help="Download wordlist category")
@click.option("--combo", nargs=2, default=None, help="Combo attack: two wordlist files")
@click.option("--mask", default="", help="Mask pattern: ?u?l?l?d?d?d")
@click.option("--osint", default="", help="OSINT: target username")
@click.option("--wifi-essid", default="", help="Wi-Fi ESSID for wordlist generation")
@click.option("--wifi-vendor", default="", help="Wi-Fi router vendor")
@click.option("--locale", default="", help="Locale codes: en,tr,de")
@click.option("--stats", "stats_file", default="", help="Analyze wordlist file")
@click.option("--chain", default="", help='Chain mutations: "leet -> numbers(0-99)"')
@click.option("--recipe", default="", help="YAML recipe file")
@click.option("--markov-train", default="", help="Train Markov model from wordlist")
@click.option("--markov-count", default=10000, help="Number of Markov-generated words")
@click.option("--policy", default="", help='Password policy: "min:8 upper:1 digit:1"')
@click.option("--output", "-o", default="", help="Output file path")
@click.option("--format", "fmt", default="txt", type=click.Choice(["txt", "json", "hashcat"]), help="Output format")
@click.option("--sort-freq/--no-sort-freq", default=False, help="Sort by frequency")
@click.option("--dedup-fuzzy/--no-dedup-fuzzy", default=False, help="Fuzzy deduplication")
@click.option("--no-banner", is_flag=True, default=False, help="Suppress ASCII banner")
def main(**kwargs):
    """GRIMOIRE — Where words are forged into weapons.

    Advanced wordlist generator combining CeWL web crawling with CUPP target profiling,
    Hashcat mutation engine, OSINT scraping, and more.
    """
    if not kwargs.get("no_banner"):
        b.print_banner()

    # Dispatch to feature handlers based on flags
    if kwargs.get("stats_file"):
        _handle_stats(kwargs["stats_file"])
        return

    if kwargs.get("alecto_search") is not None:
        _handle_alecto(kwargs["alecto_search"])
        return

    if kwargs.get("profile"):
        _handle_profile(kwargs)
        return

    if kwargs.get("improve_file"):
        _handle_improve(kwargs)
        return

    if kwargs.get("download_cat"):
        _handle_download(kwargs["download_cat"])
        return

    if kwargs.get("combo"):
        _handle_combo(kwargs)
        return

    if kwargs.get("mask"):
        _handle_mask(kwargs)
        return

    if kwargs.get("osint"):
        _handle_osint(kwargs)
        return

    if kwargs.get("wifi_essid") or kwargs.get("wifi_vendor"):
        _handle_wifi(kwargs)
        return

    if kwargs.get("locale"):
        _handle_locale(kwargs)
        return

    if kwargs.get("chain"):
        _handle_chain(kwargs)
        return

    if kwargs.get("recipe"):
        _handle_recipe(kwargs["recipe"])
        return

    if kwargs.get("markov_train"):
        _handle_markov(kwargs)
        return

    if kwargs.get("url") or kwargs.get("input_file"):
        _handle_crawl(kwargs)
        return

    # No flags → interactive wizard
    from grimoire.wizard import run as run_wizard
    config, mode = run_wizard()
    if mode == "exit":
        return
    _handle_wizard_result(mode, config)


def _handle_crawl(kw):
    from grimoire.crawler.static import crawl_static
    from grimoire.crawler.headless import crawl_headless, is_available
    from grimoire.dedup import exact_dedup, fuzzy_dedup
    from grimoire.mutator.basic import mutate_all
    from grimoire.mutator.rules import parse_rule_file, apply_rules
    from grimoire.output import write_file, sort_by_frequency

    url = kw["url"]
    b.info(f"Starting crawl: {url}")

    crawl_kwargs = dict(
        url=url, depth=kw["depth"], delay=kw["delay"],
        proxy=kw["proxy"], cookie=kw["cookie"], random_ua=kw["random_ua"],
        min_length=kw["min_length"], max_length=kw["max_length"],
        emails=kw["emails"], meta=kw["meta"], js_strings=kw["js"],
        on_page=lambda u, r: b.success(f"Page: {u} ({len(r.words)} words)"),
    )

    mode = kw["mode"]
    result = None
    if mode == "headless" and is_available():
        result = crawl_headless(**{k: v for k, v in crawl_kwargs.items() if k != "random_ua" and k != "cookie"})
    else:
        result = crawl_static(**crawl_kwargs)

    words = result.word_list()

    if kw["mutate"] or kw["leet"] or kw["case"] or kw["append_numbers"]:
        opts = {
            "leet": kw["leet"], "case": kw["case"],
            "numbers": kw["append_numbers"], "symbols": kw["append_symbols"],
            "num_from": 0, "num_to": 99,
        }
        words = mutate_all(words, opts)

    if kw["rule_file"]:
        rules = parse_rule_file(kw["rule_file"])
        words.extend(apply_rules(words, rules))

    words = fuzzy_dedup(words, 2) if kw["dedup_fuzzy"] else exact_dedup(words)

    if kw["sort_freq"]:
        words = sort_by_frequency(dict(result.words))

    emails = list(result.emails)
    b.success(f"Complete: {len(words)} unique words, {len(emails)} emails")

    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"], dict(result.words))
        b.success(f"Saved to {kw['output']}")

    state = ReplState(words=words, emails=emails, freq_map=dict(result.words))
    run_repl(state)


def _handle_profile(kw):
    from grimoire.profiler import generate
    from grimoire.dedup import exact_dedup
    from grimoire.output import write_file
    import shlex

    pd = {"leet": True, "special_chars": True}
    for pair in kw["profile"].split():
        if "=" in pair:
            k, v = pair.split("=", 1)
            key_map = {
                "name": "first_name", "first": "first_name", "last": "last_name",
                "nick": "nickname", "dob": "birthdate", "partner": "partner_name",
                "pet": "pet_name", "company": "company",
            }
            pd[key_map.get(k.lower(), k.lower())] = v

    words = exact_dedup(generate(pd))
    b.success(f"Profile generated {len(words)} words")

    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")

    run_repl(ReplState(words=words))


def _handle_alecto(vendor):
    from grimoire import alecto as a
    from rich.table import Table

    if vendor:
        results = a.search(vendor)
        if not results:
            b.warning(f"No entries for: {vendor}")
            return
        table = Table(border_style="cyan")
        table.add_column("Vendor", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Password", style="yellow")
        for e in results:
            table.add_row(e.vendor, e.username, e.password)
        b.console.print(table)
        b.info(f"{len(results)} entries found.")
    else:
        entries = a.dump()
        table = Table(border_style="cyan")
        table.add_column("Vendor", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Password", style="yellow")
        for e in entries:
            table.add_row(e.vendor, e.username, e.password)
        b.console.print(table)
        b.info(f"{len(entries)} total entries.")


def _handle_improve(kw):
    from grimoire.improver import improve
    from grimoire.output import write_file

    words = improve(kw["improve_file"], {
        "leet": True, "case": True, "numbers": True, "symbols": True,
        "rule_file": kw["rule_file"], "fuzzy_dedup": kw["dedup_fuzzy"],
    })
    b.success(f"Improved: {len(words)} words")
    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=words))


def _handle_download(category):
    from grimoire.downloader import download
    b.info(f"Downloading: {category}...")
    try:
        dest = download(category)
        b.success(f"Downloaded to: {dest}")
    except Exception as e:
        b.error(f"Failed: {e}")


def _handle_combo(kw):
    from grimoire.mutator.combo import combo_from_files
    from grimoire.output import write_file

    f1, f2 = kw["combo"]
    words = combo_from_files(f1, f2)
    b.success(f"Combo: {len(words)} words generated")
    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=words))


def _handle_mask(kw):
    from grimoire.mask import generate_from_mask, estimate_size
    from grimoire.output import write_file

    mask = kw["mask"]
    est = estimate_size(mask)
    b.info(f"Mask: {mask} → ~{est:,} possible combinations")
    words = generate_from_mask(mask, max_output=100000)
    b.success(f"Generated {len(words)} words")
    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=words))


def _handle_osint(kw):
    from grimoire.osint import gather_osint
    from grimoire.output import write_file

    username = kw["osint"]
    b.info(f"OSINT scraping: {username}...")
    keywords = gather_osint(username)
    b.success(f"Extracted {len(keywords)} keywords")
    if kw["output"]:
        write_file(keywords, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=keywords))


def _handle_wifi(kw):
    from grimoire.wifi import generate_wifi_wordlist
    from grimoire.output import write_file

    words = generate_wifi_wordlist(essid=kw["wifi_essid"], vendor=kw["wifi_vendor"])
    b.success(f"Wi-Fi wordlist: {len(words)} words")
    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=words))


def _handle_locale(kw):
    from grimoire.locale_packs import load_multiple
    from grimoire.output import write_file

    codes = [c.strip() for c in kw["locale"].split(",") if c.strip()]
    words = load_multiple(codes)
    b.success(f"Locale packs: {len(words)} words from {', '.join(codes)}")
    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=words))


def _handle_chain(kw):
    from grimoire.chain import run_chain, parse_chain_string
    from grimoire.output import write_file

    words = []
    if kw.get("input_file"):
        with open(kw["input_file"], "r") as f:
            words = [l.strip() for l in f if l.strip()]

    steps = parse_chain_string(kw["chain"])
    words = run_chain(words, steps)
    b.success(f"Chain: {len(words)} words")
    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=words))


def _handle_recipe(recipe_file):
    from grimoire.recipe import load_recipe, execute_recipe

    recipe = load_recipe(recipe_file)
    b.info(f"Running recipe: {recipe.get('name', recipe_file)}")
    words = execute_recipe(recipe, on_step=lambda i, t, s: b.info(f"Step {i}/{t}: {list(s.keys())[0]}"))
    b.success(f"Recipe complete: {len(words)} words")
    run_repl(ReplState(words=words))


def _handle_markov(kw):
    from grimoire.markov import train_from_file
    from grimoire.output import write_file

    b.info(f"Training Markov model from: {kw['markov_train']}")
    model = train_from_file(kw["markov_train"])
    words = model.generate(count=kw["markov_count"])
    b.success(f"Generated {len(words)} words")
    if kw["output"]:
        write_file(words, kw["output"], kw["fmt"])
        b.success(f"Saved to {kw['output']}")
    run_repl(ReplState(words=words))


def _handle_stats(filepath):
    from grimoire.stats import analyze, length_histogram
    from rich.table import Table

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        words = [l.strip() for l in f if l.strip()]

    stats = analyze(words)
    table = Table(title=f"Analysis: {filepath}", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")

    table.add_row("Total words", f"{stats['total']:,}")
    table.add_row("Unique words", f"{stats['unique']:,}")
    table.add_row("Duplicates", f"{stats['duplicates']:,}")
    table.add_row("Min length", str(stats["min_length"]))
    table.add_row("Max length", str(stats["max_length"]))
    table.add_row("Avg length", f"{stats['avg_length']:.1f}")
    table.add_row("Avg entropy", f"{stats['avg_entropy']} bits")

    b.console.print(table)
    b.console.print()
    b.dim("Length distribution:")
    for line in length_histogram(words):
        b.console.print(line)


def _handle_wizard_result(mode, config):
    from grimoire.output import write_file

    if mode == "crawl":
        _handle_crawl({
            "url": config.get("url", ""), "depth": config.get("depth", 2),
            "delay": config.get("delay", 0), "proxy": config.get("proxy", ""),
            "cookie": "", "random_ua": config.get("random_ua", False),
            "min_length": config.get("min_length", 5), "max_length": config.get("max_length", 0),
            "emails": config.get("emails", False), "meta": config.get("meta", False),
            "js": config.get("js", False), "mode": config.get("mode", "auto"),
            "mutate": config.get("mutate", False), "leet": False, "case": False,
            "append_numbers": False, "append_symbols": False, "rule_file": "",
            "dedup_fuzzy": False, "sort_freq": False,
            "output": config.get("output", ""), "fmt": config.get("format", "txt"),
        })
    elif mode == "profile":
        from grimoire.profiler import generate
        from grimoire.dedup import exact_dedup
        profile_data = {k: v for k, v in config.items() if k not in ("output", "format")}
        profile_data["leet"] = True
        profile_data["special_chars"] = True
        words = exact_dedup(generate(profile_data))
        b.success(f"Profile: {len(words)} words")
        output = config.get("output", "")
        if output:
            write_file(words, output, config.get("format", "txt"))
            b.success(f"Saved to {output}")
        run_repl(ReplState(words=words))
    elif mode == "improve":
        _handle_improve({
            "improve_file": config.get("input_file", ""), "rule_file": "",
            "dedup_fuzzy": config.get("fuzzy_dedup", False),
            "output": config.get("output", ""), "fmt": "txt",
        })
    elif mode == "download":
        _handle_download(config.get("category", ""))
    elif mode == "alecto":
        _handle_alecto("")
    elif mode == "combo":
        from grimoire.mutator.combo import combo_from_files
        words = combo_from_files(config.get("file1", ""), config.get("file2", ""), config.get("separator", ""))
        b.success(f"Combo: {len(words)} words")
        output = config.get("output", "")
        if output:
            write_file(words, output, "txt")
            b.success(f"Saved to {output}")
        run_repl(ReplState(words=words))
    elif mode == "mask":
        from grimoire.mask import generate_from_mask
        words = generate_from_mask(config.get("mask", ""), max_output=config.get("max_output", 100000))
        b.success(f"Mask: {len(words)} words")
        output = config.get("output", "")
        if output:
            write_file(words, output, "txt")
            b.success(f"Saved to {output}")
        run_repl(ReplState(words=words))
    elif mode == "osint":
        from grimoire.osint import gather_osint
        words = gather_osint(config.get("username", ""))
        b.success(f"OSINT: {len(words)} keywords")
        output = config.get("output", "")
        if output:
            write_file(words, output, "txt")
        run_repl(ReplState(words=words))
    elif mode == "wifi":
        from grimoire.wifi import generate_wifi_wordlist
        words = generate_wifi_wordlist(essid=config.get("essid", ""), vendor=config.get("vendor", ""))
        b.success(f"Wi-Fi: {len(words)} words")
        output = config.get("output", "")
        if output:
            write_file(words, output, "txt")
        run_repl(ReplState(words=words))
    elif mode == "locale":
        from grimoire.locale_packs import load_multiple
        words = load_multiple(config.get("locales", []))
        b.success(f"Locale: {len(words)} words")
        output = config.get("output", "")
        if output:
            write_file(words, output, "txt")
        run_repl(ReplState(words=words))
    elif mode == "stats":
        _handle_stats(config.get("input_file", ""))
    elif mode == "chain":
        from grimoire.chain import run_chain, parse_chain_string
        words = []
        input_file = config.get("input_file", "")
        if input_file:
            with open(input_file, "r") as f:
                words = [l.strip() for l in f if l.strip()]
        steps = parse_chain_string(config.get("chain", ""))
        words = run_chain(words, steps)
        b.success(f"Chain: {len(words)} words")
        output = config.get("output", "")
        if output:
            write_file(words, output, "txt")
        run_repl(ReplState(words=words))
    elif mode == "recipe":
        _handle_recipe(config.get("recipe_file", ""))
    elif mode == "markov":
        from grimoire.markov import train_from_file
        model = train_from_file(config.get("train_file", ""))
        words = model.generate(
            count=config.get("count", 10000),
            min_len=config.get("min_len", 6),
            max_len=config.get("max_len", 16),
        )
        b.success(f"Markov: {len(words)} words")
        output = config.get("output", "")
        if output:
            write_file(words, output, "txt")
        run_repl(ReplState(words=words))
