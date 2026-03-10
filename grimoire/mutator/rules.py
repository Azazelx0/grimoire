"""Hashcat-compatible rule file parser and applier."""

from dataclasses import dataclass


@dataclass
class Operation:
    op: str
    char_a: str = ""
    char_b: str = ""
    pos: int = 0


def parse_rule_file(path: str) -> list[list[Operation]]:
    rules = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                ops = parse_rule(line)
                rules.append(ops)
            except ValueError:
                continue
    return rules


def parse_rule(line: str) -> list[Operation]:
    ops = []
    i = 0
    while i < len(line):
        c = line[i]
        if c == ":":
            ops.append(Operation(op="noop"))
            i += 1
        elif c == "l":
            ops.append(Operation(op="lower"))
            i += 1
        elif c == "u":
            ops.append(Operation(op="upper"))
            i += 1
        elif c == "c":
            ops.append(Operation(op="capitalize"))
            i += 1
        elif c == "C":
            ops.append(Operation(op="invcap"))
            i += 1
        elif c == "r":
            ops.append(Operation(op="reverse"))
            i += 1
        elif c == "d":
            ops.append(Operation(op="duplicate"))
            i += 1
        elif c == "$":
            if i + 1 >= len(line):
                raise ValueError(f"$ at pos {i} requires a char")
            ops.append(Operation(op="append", char_a=line[i + 1]))
            i += 2
        elif c == "^":
            if i + 1 >= len(line):
                raise ValueError(f"^ at pos {i} requires a char")
            ops.append(Operation(op="prepend", char_a=line[i + 1]))
            i += 2
        elif c == "s":
            if i + 2 >= len(line):
                raise ValueError(f"s at pos {i} requires two chars")
            ops.append(Operation(op="replace", char_a=line[i + 1], char_b=line[i + 2]))
            i += 3
        elif c == "T":
            if i + 1 >= len(line) or not line[i + 1].isdigit():
                raise ValueError(f"T at pos {i} requires a digit")
            ops.append(Operation(op="toggle", pos=int(line[i + 1])))
            i += 2
        else:
            raise ValueError(f"Unknown op '{c}' at pos {i}")
    return ops


def apply_rule(word: str, ops: list[Operation]) -> str:
    for op in ops:
        word = _apply_op(word, op)
    return word


def _apply_op(word: str, op: Operation) -> str:
    if op.op == "noop":
        return word
    elif op.op == "lower":
        return word.lower()
    elif op.op == "upper":
        return word.upper()
    elif op.op == "capitalize":
        return word.capitalize() if word else word
    elif op.op == "invcap":
        if not word:
            return word
        return word[0].lower() + word[1:].upper()
    elif op.op == "reverse":
        return word[::-1]
    elif op.op == "duplicate":
        return word + word
    elif op.op == "append":
        return word + op.char_a
    elif op.op == "prepend":
        return op.char_a + word
    elif op.op == "replace":
        return word.replace(op.char_a, op.char_b)
    elif op.op == "toggle":
        if 0 <= op.pos < len(word):
            chars = list(word)
            chars[op.pos] = chars[op.pos].swapcase()
            return "".join(chars)
        return word
    return word


def apply_rules(words: list[str], rules: list[list[Operation]]) -> list[str]:
    seen = set()
    results = []
    for w in words:
        for rule in rules:
            mutated = apply_rule(w, rule)
            if mutated not in seen:
                seen.add(mutated)
                results.append(mutated)
    return results
