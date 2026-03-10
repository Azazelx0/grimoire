"""Interactive REPL shell with prompt_toolkit tab-completion."""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from rich.table import Table

from grimoire import banner
from grimoire.dedup import exact_dedup, fuzzy_dedup
from grimoire.mutator.basic import mutate_all, DEFAULT_OPTS
from grimoire.output import write_file
from grimoire.profiler import generate as profile_generate
from grimoire import alecto as alecto_mod
from grimoire.downloader import list_categories, download
from grimoire.improver import improve
from grimoire.stats import analyze, length_histogram
from grimoire.policy import apply_policy, parse_policy_string

COMMANDS = [
    "help", "stats", "export", "mutate", "profile", "alecto",
    "download", "improve", "dedup", "policy", "analyze",
    "save", "load", "set", "clear", "exit", "quit",
]

completer = WordCompleter(COMMANDS, ignore_case=True)


class ReplState:
    def __init__(self, words=None, emails=None, freq_map=None, config=None):
        self.words = words or []
        self.emails = emails or []
        self.freq_map = freq_map or {}
        self.config = config or {}


def run(state: ReplState):
    session = PromptSession(completer=completer)

    banner.console.print()
    banner.success(f"Session active. {len(state.words)} words loaded. Type 'help' for commands.")
    banner.console.print()

    while True:
        try:
            text = session.prompt(HTML("<ansired><b>grimoire</b></ansired><b>❯</b> "))
        except (EOFError, KeyboardInterrupt):
            banner.info("Exiting GRIMOIRE.")
            break

        text = text.strip()
        if not text:
            continue

        parts = text.split()
        cmd = parts[0].lower()

        if cmd in ("exit", "quit", "q"):
            banner.info("Exiting GRIMOIRE. Stay sharp.")
            break
        elif cmd == "help":
            _cmd_help()
        elif cmd == "stats" or cmd == "analyze":
            _cmd_stats(state)
        elif cmd == "export":
            if len(parts) < 2:
                banner.error("Usage: export <filename>")
                continue
            _cmd_export(state, parts[1])
        elif cmd == "mutate":
            _cmd_mutate(state, parts[1:])
        elif cmd == "profile":
            _cmd_profile(state)
        elif cmd == "alecto":
            _cmd_alecto(parts[1:])
        elif cmd == "download":
            if len(parts) < 2:
                banner.error(f"Usage: download <category>  Available: {', '.join(list_categories())}")
                continue
            _cmd_download(parts[1])
        elif cmd == "improve":
            if len(parts) < 2:
                banner.error("Usage: improve <file>")
                continue
            _cmd_improve(state, parts[1])
        elif cmd == "dedup":
            fuzzy = "--fuzzy" in parts
            _cmd_dedup(state, fuzzy)
        elif cmd == "policy":
            if len(parts) < 2:
                banner.error('Usage: policy min:8 max:16 upper:1 digit:1')
                continue
            _cmd_policy(state, " ".join(parts[1:]))
        elif cmd == "set":
            if len(parts) < 3:
                banner.error("Usage: set <key> <value>")
                continue
            state.config[parts[1]] = " ".join(parts[2:])
            banner.success(f"Set {parts[1]} = {' '.join(parts[2:])}")
        elif cmd == "save":
            if len(parts) < 2:
                banner.error("Usage: save <file>")
                continue
            _cmd_save(state, parts[1])
        elif cmd == "load":
            if len(parts) < 2:
                banner.error("Usage: load <file>")
                continue
            _cmd_load(state, parts[1])
        elif cmd == "clear":
            state.words = []
            state.emails = []
            state.freq_map = {}
            banner.success("Wordlist cleared.")
        else:
            banner.error(f"Unknown command: {cmd}. Type 'help' for available commands.")


def _cmd_help():
    table = Table(title="GRIMOIRE Commands", border_style="red", title_style="bold yellow")
    table.add_column("Command", style="cyan", width=35)
    table.add_column("Description", style="dim")

    cmds = [
        ("help", "Show all commands"),
        ("stats / analyze", "Show wordlist statistics"),
        ("export <file>", "Export wordlist to file"),
        ("mutate [--leet --case --numbers --symbols]", "Apply mutations"),
        ("profile", "Launch target profiling"),
        ("alecto [search <vendor>]", "Browse Alecto DB"),
        ("download <category>", "Download wordlist category"),
        ("improve <file>", "Enhance existing wordlist"),
        ("dedup [--fuzzy]", "Deduplicate wordlist"),
        ("policy min:8 upper:1 ...", "Filter by password policy"),
        ("set <key> <value>", "Change session setting"),
        ("save <file>", "Save wordlist to file"),
        ("load <file>", "Load wordlist from file"),
        ("clear", "Reset wordlist"),
        ("exit", "Quit GRIMOIRE"),
    ]
    for name, desc in cmds:
        table.add_row(name, desc)

    banner.console.print()
    banner.console.print(table)
    banner.console.print()


def _cmd_stats(state: ReplState):
    if not state.words:
        banner.warning("No words loaded.")
        return

    stats = analyze(state.words)
    table = Table(title="Wordlist Statistics", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")

    table.add_row("Total words", str(stats["total"]))
    table.add_row("Unique", str(stats["unique"]))
    table.add_row("Duplicates", str(stats["duplicates"]))
    table.add_row("Min length", str(stats["min_length"]))
    table.add_row("Max length", str(stats["max_length"]))
    table.add_row("Avg length", f"{stats['avg_length']:.1f}")
    table.add_row("Avg entropy", f"{stats['avg_entropy']} bits")

    banner.console.print()
    banner.console.print(table)

    if state.emails:
        banner.info(f"Emails: {len(state.emails)}")

    banner.console.print()
    banner.dim("Length distribution:")
    for line in length_histogram(state.words):
        banner.console.print(line)
    banner.console.print()


def _cmd_export(state: ReplState, filename: str):
    fmt = "txt"
    if filename.endswith(".json"):
        fmt = "json"
    elif filename.endswith(".hc"):
        fmt = "hashcat"

    try:
        write_file(state.words, filename, fmt, state.freq_map)
        banner.success(f"Exported {len(state.words)} words to {filename}")
    except Exception as e:
        banner.error(f"Export failed: {e}")


def _cmd_mutate(state: ReplState, args: list[str]):
    if not args:
        opts = dict(DEFAULT_OPTS)
    else:
        opts = {"num_from": 0, "num_to": 99}
        for arg in args:
            if arg == "--leet":
                opts["leet"] = True
            elif arg == "--case":
                opts["case"] = True
            elif arg == "--numbers":
                opts["numbers"] = True
            elif arg == "--symbols":
                opts["symbols"] = True
            elif arg == "--reverse":
                opts["reverse"] = True
            elif arg == "--years":
                opts["years"] = True

    before = len(state.words)
    state.words = mutate_all(state.words, opts)
    after = len(state.words)
    banner.success(f"Mutation: {before} → {after} words (+{after - before})")


def _cmd_profile(state: ReplState):
    import questionary
    banner.console.print("\n  [bold cyan]── Target Profile ──[/bold cyan]\n")

    p = {
        "first_name": questionary.text("First name:").ask() or "",
        "last_name": questionary.text("Last name:").ask() or "",
        "nickname": questionary.text("Nickname:").ask() or "",
        "birthdate": questionary.text("Birthdate (DD/MM/YYYY):").ask() or "",
        "partner_name": questionary.text("Partner name:").ask() or "",
        "pet_name": questionary.text("Pet name:").ask() or "",
        "company": questionary.text("Company:").ask() or "",
        "leet": True, "special_chars": True,
    }

    words = profile_generate(p)
    state.words.extend(words)
    state.words = exact_dedup(state.words)
    banner.success(f"Profile generated {len(words)} words. Total: {len(state.words)}")


def _cmd_alecto(args: list[str]):
    if len(args) >= 2 and args[0] == "search":
        vendor = " ".join(args[1:])
        results = alecto_mod.search(vendor)
        if not results:
            banner.warning(f"No entries found for: {vendor}")
            return

        table = Table(border_style="cyan")
        table.add_column("Vendor", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Password", style="yellow")
        for e in results:
            table.add_row(e.vendor, e.username, e.password)

        banner.console.print()
        banner.console.print(table)
        banner.info(f"{len(results)} entries found.")
        banner.console.print()
    else:
        entries = alecto_mod.dump()
        vendor_list = alecto_mod.vendors()
        banner.info(f"Alecto DB: {len(entries)} entries, {len(vendor_list)} vendors")
        banner.dim(f"Vendors: {', '.join(vendor_list)}")
        banner.dim("Use 'alecto search <vendor>' to filter.")


def _cmd_download(category: str):
    banner.info(f"Downloading: {category}...")
    try:
        dest = download(category, on_progress=lambda d, t: None)
        banner.success(f"Downloaded to: {dest}")
    except Exception as e:
        banner.error(f"Download failed: {e}")


def _cmd_improve(state: ReplState, file: str):
    try:
        words = improve(file, {"leet": True, "case": True, "numbers": True, "symbols": True})
        state.words.extend(words)
        state.words = exact_dedup(state.words)
        banner.success(f"Improved: {len(words)} words added. Total: {len(state.words)}")
    except Exception as e:
        banner.error(f"Improve failed: {e}")


def _cmd_dedup(state: ReplState, fuzzy: bool):
    before = len(state.words)
    if fuzzy:
        state.words = fuzzy_dedup(state.words, 2)
    else:
        state.words = exact_dedup(state.words)
    after = len(state.words)
    method = "fuzzy" if fuzzy else "exact"
    banner.success(f"Dedup ({method}): {before} → {after} (removed {before - after})")


def _cmd_policy(state: ReplState, policy_str: str):
    policy = parse_policy_string(policy_str)
    before = len(state.words)
    state.words = apply_policy(state.words, policy)
    after = len(state.words)
    banner.success(f"Policy filter: {before} → {after} (removed {before - after})")


def _cmd_save(state: ReplState, filename: str):
    try:
        write_file(state.words, filename, "txt")
        banner.success(f"Saved {len(state.words)} words to {filename}")
    except Exception as e:
        banner.error(f"Save failed: {e}")


def _cmd_load(state: ReplState, filename: str):
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            words = [l.strip() for l in f if l.strip()]
        state.words.extend(words)
        state.words = exact_dedup(state.words)
        banner.success(f"Loaded {len(words)} words from {filename}. Total: {len(state.words)}")
    except Exception as e:
        banner.error(f"Load failed: {e}")
