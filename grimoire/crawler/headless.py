"""Headless browser crawler using Playwright (optional dependency)."""

from grimoire.extractor import extract, ExtractionResult


def is_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        return False


def crawl_headless(url: str, depth: int = 0, proxy: str = "",
                   wait_ms: int = 5000, min_length: int = 5, max_length: int = 0,
                   emails: bool = False, meta: bool = False, js_strings: bool = False,
                   on_page=None, on_error=None) -> ExtractionResult:
    if not is_available():
        raise ImportError(
            "Playwright is not installed. Install with: pip install playwright && playwright install chromium"
        )

    from playwright.sync_api import sync_playwright

    result = ExtractionResult()

    with sync_playwright() as p:
        launch_args = {"headless": True}
        if proxy:
            launch_args["proxy"] = {"server": proxy}

        browser = p.chromium.launch(**launch_args)
        page = browser.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(wait_ms)
            html_content = page.content()

            page_result = extract(
                html_content, min_length=min_length, max_length=max_length,
                emails=emails, meta=meta, js_strings=js_strings,
            )
            result.merge(page_result)

            if on_page:
                on_page(url, page_result)

        except Exception as e:
            if on_error:
                on_error(url, e)
            else:
                raise
        finally:
            browser.close()

    return result
