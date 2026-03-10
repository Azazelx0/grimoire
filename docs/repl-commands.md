# REPL Command Reference

After any operation, GRIMOIRE drops into an interactive REPL session with tab-completion. You can refine, mutate, export, and analyze without restarting.

## Commands

### `help`
Show all available commands with descriptions.

```
grimoire❯ help
```

### `stats` / `analyze`
Show wordlist statistics — total words, unique, duplicates, length distribution histogram, charset breakdown, entropy score.

```
grimoire❯ stats
```

### `export <file>`
Export the current wordlist to a file. Format is auto-detected from extension (`.json` → JSON, `.hc` → Hashcat, default → plaintext).

```
grimoire❯ export wordlist.txt
grimoire❯ export results.json
```

### `mutate [flags]`
Apply mutations to the current wordlist. Without flags, applies all default mutations.

```
grimoire❯ mutate
grimoire❯ mutate --leet --case
grimoire❯ mutate --numbers --symbols
```

### `profile`
Launch interactive target profiling wizard (CUPP-style). Generated words are added to the current wordlist.

```
grimoire❯ profile
```

### `alecto [search <vendor>]`
Browse or search the Alecto default credentials database.

```
grimoire❯ alecto                  # show all vendors
grimoire❯ alecto search cisco     # search by vendor
```

### `download <category>`
Download a wordlist by category. Available: `names`, `passwords`, `sports`, `science`, `random`, `religious`.

```
grimoire❯ download passwords
```

### `improve <file>`
Load an existing wordlist and enhance it with mutations.

```
grimoire❯ improve oldlist.txt
```

### `dedup [--fuzzy]`
Deduplicate the current wordlist. Use `--fuzzy` for Levenshtein-based fuzzy dedup.

```
grimoire❯ dedup
grimoire❯ dedup --fuzzy
```

### `policy <rules>`
Filter the current wordlist by password policy requirements.

```
grimoire❯ policy min:8 max:16 upper:1 digit:1
```

### `load <file>`
Load words from a file and add them to the current wordlist.

```
grimoire❯ load another-list.txt
```

### `save <file>`
Save the current wordlist to a plaintext file.

```
grimoire❯ save output.txt
```

### `set <key> <value>`
Set a session configuration value.

```
grimoire❯ set output results.txt
```

### `clear`
Clear the current wordlist and reset the session.

```
grimoire❯ clear
```

### `exit` / `quit` / `q`
Exit GRIMOIRE.

```
grimoire❯ exit
```
