"""Interactive wizard — mode selection and sub-wizards using questionary."""

import questionary
from questionary import Style
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
    {"name": "🔐 Alecto DB          — Default credentials database", "value": "alecto"},
    {"name": "🔀 Combo Attack       — Merge two wordlists", "value": "combo"},
    {"name": "🎭 Mask Generator     — Pattern-based generation", "value": "mask"},
    {"name": "🔍 OSINT Scraper      — Social media profiling", "value": "osint"},
    {"name": "📡 Wi-Fi Wordlist     — ESSID/vendor-based passwords", "value": "wifi"},
    {"name": "🌍 Locale Packs       — Language-specific passwords", "value": "locale"},
    {"name": "📊 Analyze Wordlist   — Statistics & analysis", "value": "stats"},
    {"name": "🔗 Chain Pipeline     — Multi-step mutations", "value": "chain"},
    {"name": "📝 Run Recipe         — Execute YAML recipe", "value": "recipe"},
    {"name": "🧬 Markov Generator   — Statistical password generation", "value": "markov"},
]


def run() -> tuple[dict, str]:
    mode = questionary.select(
        "Select mode",
        choices=[questionary.Choice(m["name"], value=m["value"]) for m in MODES],
        style=GRIMOIRE_STYLE,
    ).ask()

    if not mode:
        return {}, "exit"

    config = {}

    if mode == "crawl":
        config = _crawl_wizard()
    elif mode == "profile":
        config = _profile_wizard()
    elif mode == "improve":
        config = _improve_wizard()
    elif mode == "download":
        config = _download_wizard()
    elif mode == "combo":
        config = _combo_wizard()
    elif mode == "mask":
        config = _mask_wizard()
    elif mode == "osint":
        config = _osint_wizard()
    elif mode == "wifi":
        config = _wifi_wizard()
    elif mode == "locale":
        config = _locale_wizard()
    elif mode == "stats":
        config = _stats_wizard()
    elif mode == "chain":
        config = _chain_wizard()
    elif mode == "recipe":
        config = _recipe_wizard()
    elif mode == "markov":
        config = _markov_wizard()

    return config, mode


def _crawl_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Web Crawl Configuration ──[/bold cyan]\n")
    return {
        "url": questionary.text("Target URL:", style=GRIMOIRE_STYLE).ask() or "",
        "mode": questionary.select("Crawl mode:", choices=["auto", "static", "headless"], style=GRIMOIRE_STYLE).ask() or "auto",
        "depth": int(questionary.text("Crawl depth (1-10):", default="2", style=GRIMOIRE_STYLE).ask() or "2"),
        "min_length": int(questionary.text("Min word length:", default="5", style=GRIMOIRE_STYLE).ask() or "5"),
        "max_length": int(questionary.text("Max word length (0=unlimited):", default="0", style=GRIMOIRE_STYLE).ask() or "0"),
        "emails": questionary.confirm("Extract emails?", default=True, style=GRIMOIRE_STYLE).ask(),
        "meta": questionary.confirm("Extract metadata?", default=True, style=GRIMOIRE_STYLE).ask(),
        "js": questionary.confirm("Extract JS strings?", default=False, style=GRIMOIRE_STYLE).ask(),
        "proxy": questionary.text("Proxy URL (empty=none):", default="", style=GRIMOIRE_STYLE).ask() or "",
        "random_ua": questionary.confirm("Rotate User-Agent?", default=False, style=GRIMOIRE_STYLE).ask(),
        "delay": int(questionary.text("Request delay ms (0=none):", default="0", style=GRIMOIRE_STYLE).ask() or "0"),
        "mutate": questionary.confirm("Apply mutations?", default=False, style=GRIMOIRE_STYLE).ask(),
        "output": questionary.text("Output file:", default="wordlist.txt", style=GRIMOIRE_STYLE).ask() or "wordlist.txt",
        "format": questionary.select("Output format:", choices=["txt", "json", "hashcat"], style=GRIMOIRE_STYLE).ask() or "txt",
    }


def _profile_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Target Profile (CUPP-style) ──[/bold cyan]\n")
    return {
        "first_name": questionary.text("Target's first name:", style=GRIMOIRE_STYLE).ask() or "",
        "last_name": questionary.text("Target's last name:", style=GRIMOIRE_STYLE).ask() or "",
        "nickname": questionary.text("Target's nickname:", style=GRIMOIRE_STYLE).ask() or "",
        "birthdate": questionary.text("Birthdate (DD/MM/YYYY or YYYY):", style=GRIMOIRE_STYLE).ask() or "",
        "partner_name": questionary.text("Partner's name (empty=skip):", style=GRIMOIRE_STYLE).ask() or "",
        "partner_nickname": questionary.text("Partner's nickname:", style=GRIMOIRE_STYLE).ask() or "",
        "partner_birthday": questionary.text("Partner's birthdate:", style=GRIMOIRE_STYLE).ask() or "",
        "pet_name": questionary.text("Pet's name:", style=GRIMOIRE_STYLE).ask() or "",
        "company": questionary.text("Company/organization:", style=GRIMOIRE_STYLE).ask() or "",
        "keywords": (questionary.text("Custom keywords (comma-separated):", style=GRIMOIRE_STYLE).ask() or "").split(","),
        "output": questionary.text("Output file:", default="profile-wordlist.txt", style=GRIMOIRE_STYLE).ask() or "profile-wordlist.txt",
        "format": questionary.select("Output format:", choices=["txt", "json", "hashcat"], style=GRIMOIRE_STYLE).ask() or "txt",
    }


def _improve_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Dictionary Improver ──[/bold cyan]\n")
    return {
        "input_file": questionary.text("Input wordlist file:", style=GRIMOIRE_STYLE).ask() or "",
        "leet": questionary.confirm("Apply leet speak?", default=True, style=GRIMOIRE_STYLE).ask(),
        "case": questionary.confirm("Case variants?", default=True, style=GRIMOIRE_STYLE).ask(),
        "numbers": questionary.confirm("Append numbers?", default=True, style=GRIMOIRE_STYLE).ask(),
        "symbols": questionary.confirm("Append symbols?", default=True, style=GRIMOIRE_STYLE).ask(),
        "fuzzy_dedup": questionary.confirm("Fuzzy dedup?", default=False, style=GRIMOIRE_STYLE).ask(),
        "output": questionary.text("Output file:", default="improved.txt", style=GRIMOIRE_STYLE).ask() or "improved.txt",
    }


def _download_wizard() -> dict:
    from grimoire.downloader import list_categories
    cats = list_categories()
    return {
        "category": questionary.select("Select category:", choices=cats, style=GRIMOIRE_STYLE).ask() or cats[0],
    }


def _combo_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Combo Attack ──[/bold cyan]\n")
    return {
        "file1": questionary.text("First wordlist file:", style=GRIMOIRE_STYLE).ask() or "",
        "file2": questionary.text("Second wordlist file:", style=GRIMOIRE_STYLE).ask() or "",
        "separator": questionary.text("Separator between words (empty=none):", default="", style=GRIMOIRE_STYLE).ask() or "",
        "output": questionary.text("Output file:", default="combo.txt", style=GRIMOIRE_STYLE).ask() or "combo.txt",
    }


def _mask_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Mask Generator ──[/bold cyan]\n")
    banner.dim("Charsets: ?l=lower ?u=upper ?d=digit ?s=special ?a=all")
    return {
        "mask": questionary.text("Mask pattern:", default="?u?l?l?l?d?d?d?d", style=GRIMOIRE_STYLE).ask() or "?u?l?l?l?d?d?d?d",
        "max_output": int(questionary.text("Max words to generate:", default="100000", style=GRIMOIRE_STYLE).ask() or "100000"),
        "output": questionary.text("Output file:", default="mask-output.txt", style=GRIMOIRE_STYLE).ask() or "mask-output.txt",
    }


def _osint_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── OSINT Scraper ──[/bold cyan]\n")
    return {
        "username": questionary.text("Target username:", style=GRIMOIRE_STYLE).ask() or "",
        "output": questionary.text("Output file:", default="osint-words.txt", style=GRIMOIRE_STYLE).ask() or "osint-words.txt",
    }


def _wifi_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Wi-Fi Wordlist Generator ──[/bold cyan]\n")
    return {
        "essid": questionary.text("Wi-Fi ESSID (network name):", style=GRIMOIRE_STYLE).ask() or "",
        "vendor": questionary.text("Router vendor (e.g. netgear, tp-link):", style=GRIMOIRE_STYLE).ask() or "",
        "output": questionary.text("Output file:", default="wifi-words.txt", style=GRIMOIRE_STYLE).ask() or "wifi-words.txt",
    }


def _locale_wizard() -> dict:
    from grimoire.locale_packs import list_locales
    locales = list_locales()
    choices = [f"{code} — {name}" for code, name in locales.items()]
    selected = questionary.checkbox("Select locales:", choices=choices, style=GRIMOIRE_STYLE).ask() or []
    codes = [s.split(" — ")[0] for s in selected]
    return {
        "locales": codes,
        "output": questionary.text("Output file:", default="locale-words.txt", style=GRIMOIRE_STYLE).ask() or "locale-words.txt",
    }


def _stats_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Wordlist Analysis ──[/bold cyan]\n")
    return {
        "input_file": questionary.text("Wordlist file to analyze:", style=GRIMOIRE_STYLE).ask() or "",
    }


def _chain_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Chain Pipeline ──[/bold cyan]\n")
    banner.dim("Example: leet -> numbers(0-99) -> policy(min:8)")
    return {
        "input_file": questionary.text("Input wordlist:", style=GRIMOIRE_STYLE).ask() or "",
        "chain": questionary.text("Chain steps:", style=GRIMOIRE_STYLE).ask() or "",
        "output": questionary.text("Output file:", default="chain-output.txt", style=GRIMOIRE_STYLE).ask() or "chain-output.txt",
    }


def _recipe_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Recipe Runner ──[/bold cyan]\n")
    return {
        "recipe_file": questionary.text("Recipe YAML file:", style=GRIMOIRE_STYLE).ask() or "",
    }


def _markov_wizard() -> dict:
    banner.console.print("\n  [bold cyan]── Markov Generator ──[/bold cyan]\n")
    return {
        "train_file": questionary.text("Training wordlist file:", style=GRIMOIRE_STYLE).ask() or "",
        "count": int(questionary.text("Words to generate:", default="10000", style=GRIMOIRE_STYLE).ask() or "10000"),
        "min_len": int(questionary.text("Min word length:", default="6", style=GRIMOIRE_STYLE).ask() or "6"),
        "max_len": int(questionary.text("Max word length:", default="16", style=GRIMOIRE_STYLE).ask() or "16"),
        "output": questionary.text("Output file:", default="markov-output.txt", style=GRIMOIRE_STYLE).ask() or "markov-output.txt",
    }
