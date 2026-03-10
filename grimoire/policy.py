"""Password policy filter — filter words by password requirements."""


def apply_policy(words: list[str], policy: dict) -> list[str]:
    return [w for w in words if matches_policy(w, policy)]


def matches_policy(word: str, policy: dict) -> bool:
    min_len = policy.get("min", 0)
    max_len = policy.get("max", 0)
    min_upper = policy.get("upper", 0)
    min_lower = policy.get("lower", 0)
    min_digit = policy.get("digit", 0)
    min_special = policy.get("special", 0)

    if min_len > 0 and len(word) < min_len:
        return False
    if max_len > 0 and len(word) > max_len:
        return False

    upper_count = sum(1 for c in word if c.isupper())
    lower_count = sum(1 for c in word if c.islower())
    digit_count = sum(1 for c in word if c.isdigit())
    special_count = sum(1 for c in word if not c.isalnum())

    if upper_count < min_upper:
        return False
    if lower_count < min_lower:
        return False
    if digit_count < min_digit:
        return False
    if special_count < min_special:
        return False

    return True


def parse_policy_string(policy_str: str) -> dict:
    policy = {}
    for part in policy_str.split():
        if ":" in part:
            key, val = part.split(":", 1)
            try:
                policy[key.strip()] = int(val.strip())
            except ValueError:
                pass
    return policy


def describe_policy(policy: dict) -> str:
    parts = []
    if policy.get("min"):
        parts.append(f"min length: {policy['min']}")
    if policy.get("max"):
        parts.append(f"max length: {policy['max']}")
    if policy.get("upper"):
        parts.append(f"uppercase: ≥{policy['upper']}")
    if policy.get("lower"):
        parts.append(f"lowercase: ≥{policy['lower']}")
    if policy.get("digit"):
        parts.append(f"digits: ≥{policy['digit']}")
    if policy.get("special"):
        parts.append(f"special: ≥{policy['special']}")
    return ", ".join(parts) if parts else "No policy"
