"""Dictionary downloader with configurable categories."""

import os
import requests

DEFAULT_CATEGORIES = {
    "names": [
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/Names/names.txt",
    ],
    "passwords": [
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt",
    ],
    "sports": [
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Leaked-Databases/rockyou-50.txt",
    ],
    "science": [
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt",
    ],
    "random": [
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/darkweb2017-top10000.txt",
    ],
    "religious": [
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/common-passwords-win.txt",
    ],
}


def get_data_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".grimoire")


def get_dict_dir(category: str) -> str:
    return os.path.join(get_data_dir(), "dictionaries", category)


def list_categories() -> list[str]:
    return sorted(DEFAULT_CATEGORIES.keys())


def download(category: str, on_progress=None) -> str:
    urls = DEFAULT_CATEGORIES.get(category)
    if not urls:
        raise ValueError(f"Unknown category: {category}. Available: {', '.join(list_categories())}")

    dest_dir = get_dict_dir(category)
    os.makedirs(dest_dir, exist_ok=True)

    for url in urls:
        filename = url.split("/")[-1]
        dest_path = os.path.join(dest_dir, filename)
        _download_file(url, dest_path, on_progress)

    return dest_dir


def _download_file(url: str, dest_path: str, on_progress=None):
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if on_progress and total > 0:
                on_progress(downloaded, total)
