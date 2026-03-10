# GRIMOIRE Flag Reference

## Web Crawl Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--url` | string | `""` | Target URL to crawl |
| `--file` | string | `""` | Local file to extract words from |
| `--mode` | choice | `auto` | Crawl mode: `auto`, `static`, `headless` |
| `--depth` | int | `2` | Crawl depth (link levels to follow) |
| `--min-length` | int | `5` | Minimum word length to extract |
| `--max-length` | int | `0` | Maximum word length (`0` = unlimited) |
| `--emails / --no-emails` | bool | `false` | Extract email addresses |
| `--meta / --no-meta` | bool | `false` | Extract HTML metadata |
| `--js / --no-js` | bool | `false` | Extract JavaScript string literals |
| `--selector` | string | `""` | Custom CSS selector for extraction |
| `--cookie` | string | `""` | Cookie string to inject |
| `--header` | string | `""` | Custom HTTP header |
| `--proxy` | string | `""` | Proxy URL (`http://` or `socks5://`) |
| `--random-ua / --no-random-ua` | bool | `false` | Rotate User-Agent per request |
| `--delay` | int | `0` | Request delay in milliseconds |

## Mutation Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--mutate / --no-mutate` | bool | `false` | Enable all mutations |
| `--leet / --no-leet` | bool | `false` | Leet speak substitutions |
| `--case / --no-case` | bool | `false` | Generate case variants |
| `--append-numbers / --no-append-numbers` | bool | `false` | Append `0-99` |
| `--append-symbols / --no-append-symbols` | bool | `false` | Append common symbols |
| `--rule-file` | string | `""` | Path to Hashcat `.rule` file |

## Feature Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--profile` | string | `""` | Target profile: `"name=John dob=1990 pet=Rex"` |
| `--alecto` | string | `None` | Search Alecto DB (empty = dump all) |
| `--improve` | string | `""` | Improve existing wordlist file |
| `--download` | string | `""` | Download wordlist by category |
| `--combo` | 2 strings | `None` | Combo attack: two wordlist files |
| `--mask` | string | `""` | Mask pattern: `?u?l?l?d?d?d` |
| `--osint` | string | `""` | OSINT: target username |
| `--wifi-essid` | string | `""` | Wi-Fi ESSID for wordlist generation |
| `--wifi-vendor` | string | `""` | Wi-Fi router vendor |
| `--locale` | string | `""` | Locale codes: `en,tr,de` |
| `--stats` | string | `""` | Analyze wordlist file |
| `--chain` | string | `""` | Chain mutations: `"leet -> numbers(0-99)"` |
| `--recipe` | string | `""` | YAML recipe file |
| `--markov-train` | string | `""` | Train Markov model from wordlist |
| `--markov-count` | int | `10000` | Number of Markov-generated words |
| `--policy` | string | `""` | Password policy: `"min:8 upper:1 digit:1"` |

## Output Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-o, --output` | string | `""` | Output file path |
| `--format` | choice | `txt` | Output format: `txt`, `json`, `hashcat` |
| `--sort-freq / --no-sort-freq` | bool | `false` | Sort output by word frequency |
| `--dedup-fuzzy / --no-dedup-fuzzy` | bool | `false` | Enable fuzzy deduplication |
| `--no-banner` | bool | `false` | Suppress ASCII banner |
