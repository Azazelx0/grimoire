# Hashcat Rule Syntax

GRIMOIRE supports a subset of Hashcat-compatible rule operations. Rules are loaded from `.rule` files where each line is a sequence of operations applied to each input word.

## Supported Operations

| Operation | Description | Example Input → Output |
|-----------|-------------|------------------------|
| `:` | Do nothing (passthrough) | `password` → `password` |
| `l` | Lowercase all characters | `PassWord` → `password` |
| `u` | Uppercase all characters | `password` → `PASSWORD` |
| `c` | Capitalize first letter, lowercase rest | `password` → `Password` |
| `C` | Lowercase first, uppercase rest | `password` → `pASSWORD` |
| `r` | Reverse the word | `password` → `drowssap` |
| `d` | Duplicate the word | `pass` → `passpass` |
| `$X` | Append character X | `pass$!` → `pass!` |
| `^X` | Prepend character X | `pass^@` → `@pass` |
| `sXY` | Replace all X with Y | `passso0` → `passw0rd` (with `sa0`) |
| `TN` | Toggle case at position N | `passT0` → `Password` |

## Composite Rules

Multiple operations can be chained on a single line:

```
# Capitalize + append !
c$!
# Input: password → Output: Password!

# Uppercase + reverse
ur
# Input: password → Output: DROWSSAP

# Leet speak simulation
sa@se3si1so0
# Input: password → Output: p@55w0rd (approximate)

# Capitalize + append 2024
c$2$0$2$4
# Input: admin → Output: Admin2024
```

## Rule File Format

- One rule per line
- Lines starting with `#` are comments
- Empty lines are ignored

### Example: `mutation-example.rule`

```
# Basic transforms
:
l
u
c
C

# Append common chars
$!
$@
$#
$$
$1
$2$3

# Prepend
^!
^@

# Reverse
r

# Leet speak
sa4
se3
si1
so0
ss5

# Composite
c$!
c$1
c$1$2$3
u$!
r$!
sa4se3si1so0
c$2$0$2$5
```

## Usage

### CLI

```bash
grimoire --url https://target.com --rule-file custom.rule --format hashcat --output rules.hc
```

### REPL (not directly, but via improve)

```
grimoire> improve source.txt
# (rules are applied automatically if configured in session)
```

## Writing Your Own Rules

1. Create a `.rule` file with one rule per line
2. Test with a small wordlist first
3. Complex rules (many appends) can create very large output — use dedup

### Tips

- Start with simple transforms (`:`, `l`, `u`, `c`)
- Add character appends for the most common password patterns (`$!`, `$1`)
- Use `sXY` for targeted substitutions
- Chain operations for complex transforms
- Keep your rule file under 50 rules to avoid massive output
