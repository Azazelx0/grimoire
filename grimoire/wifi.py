"""Wi-Fi ESSID-based wordlist generator."""

from grimoire.mutator.basic import leet, case_variants, append_numbers

VENDOR_DEFAULTS = {
    "netgear": ["password", "admin", "1234", "netgear"],
    "linksys": ["admin", "linksys", ""],
    "tp-link": ["admin", "tplink", ""],
    "asus": ["admin", "asus", "password"],
    "dlink": ["admin", "dlink", ""],
    "belkin": ["belkin", ""],
    "arris": ["password", "admin", "1234"],
    "motorola": ["motorola", "admin"],
    "ubiquiti": ["ubnt", "admin"],
    "mikrotik": ["admin", ""],
    "zyxel": ["1234", "admin"],
    "huawei": ["admin", "huawei"],
}

COMMON_WIFI_PATTERNS = [
    "{essid}123", "{essid}1234", "{essid}12345",
    "{essid}!", "{essid}@", "{essid}#",
    "{essid}2024", "{essid}2025", "{essid}2026",
    "{essid}wifi", "{essid}net", "{essid}home",
    "wifi{essid}", "my{essid}", "the{essid}",
]


def generate_wifi_wordlist(essid: str = "", vendor: str = "") -> list[str]:
    seen = set()
    results = []

    def add(w):
        w = w.strip()
        if w and w not in seen:
            seen.add(w)
            results.append(w)

    if essid:
        essid_lower = essid.lower()
        essid_clean = "".join(c for c in essid_lower if c.isalnum())

        add(essid)
        add(essid_lower)
        add(essid_clean)
        add(essid.upper())

        for variant in case_variants(essid_clean):
            add(variant)

        add(leet(essid_clean))

        for pattern in COMMON_WIFI_PATTERNS:
            add(pattern.format(essid=essid_clean))
            add(pattern.format(essid=essid_clean[0].upper() + essid_clean[1:] if essid_clean else ""))

        for n in append_numbers(essid_clean, 0, 99):
            add(n)

    if vendor:
        vendor_lower = vendor.lower()
        defaults = VENDOR_DEFAULTS.get(vendor_lower, [])
        for d in defaults:
            add(d)

        if essid:
            for d in defaults:
                if d:
                    add(essid.lower() + d)
                    add(d + essid.lower())

    return results
