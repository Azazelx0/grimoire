"""Chain/pipeline mutations — apply mutations in sequence."""

from grimoire.mutator.basic import mutate_all
from grimoire.policy import apply_policy


def run_chain(words: list[str], steps: list[dict]) -> list[str]:
    for step in steps:
        step_type = step.get("type", "")
        if step_type == "leet":
            words = mutate_all(words, {"leet": True})
        elif step_type == "case":
            words = mutate_all(words, {"case": True})
        elif step_type == "numbers":
            frm = step.get("from", 0)
            to = step.get("to", 99)
            words = mutate_all(words, {"numbers": True, "num_from": frm, "num_to": to})
        elif step_type == "symbols":
            words = mutate_all(words, {"symbols": True})
        elif step_type == "years":
            words = mutate_all(words, {"years": True})
        elif step_type == "reverse":
            words = mutate_all(words, {"reverse": True})
        elif step_type == "duplicate":
            words = mutate_all(words, {"duplicate": True})
        elif step_type == "policy":
            policy = step.get("policy", {})
            words = apply_policy(words, policy)
        elif step_type == "dedup":
            from grimoire.dedup import exact_dedup
            words = exact_dedup(words)
    return words


def parse_chain_string(chain_str: str) -> list[dict]:
    steps = []
    for part in chain_str.split("->"):
        part = part.strip()
        if not part:
            continue

        if "(" in part:
            name = part[:part.index("(")].strip()
            args_str = part[part.index("(") + 1:part.rindex(")")]
            step = {"type": name}

            if name in ("numbers",) and "-" in args_str:
                frm, to = args_str.split("-", 1)
                step["from"] = int(frm.strip())
                step["to"] = int(to.strip())
            elif name == "policy":
                step["policy"] = _parse_policy_args(args_str)

            steps.append(step)
        else:
            steps.append({"type": part.lower()})

    return steps


def _parse_policy_args(args_str: str) -> dict:
    policy = {}
    for part in args_str.split(","):
        part = part.strip()
        if ":" in part:
            key, val = part.split(":", 1)
            policy[key.strip()] = int(val.strip())
    return policy
