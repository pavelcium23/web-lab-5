from bs4 import BeautifulSoup
from urllib.parse import urlencode, unquote
from src.http_client import fetch
from src.html_parser import to_text


SEARCH_URL = "https://html.duckduckgo.com/html/"


def search(term):
    query = urlencode({"q": term})
    url = f"{SEARCH_URL}?{query}"

    response = fetch(url, extra_headers={"Accept": "text/html"})
    results = _parse_results(response["body"])

    if not results:
        print("No results found.")
        return []

    print(f"\nTop results for: \"{term}\"\n")
    for i, (title, link) in enumerate(results, 1):
        print(f"  {i}. {title}")
        print(f"     {link}\n")

    _prompt_open(results)


def _parse_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for result in soup.select(".result__body"):
        title_tag = result.select_one(".result__title a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        raw_href = title_tag.get("href", "")
        link = _clean_url(raw_href)

        if title and link:
            results.append((title, link))

        if len(results) == 10:
            break

    return results


def _prompt_open(results):
    try:
        choice = input("Open a result? Enter number (or press Enter to skip): ").strip()
        if not choice:
            return
        n = int(choice)
        if not 1 <= n <= len(results):
            print(f"Pick a number between 1 and {len(results)}.")
            return
        title, link = results[n - 1]
        print(f"\nFetching: {link}\n")
        response = fetch(link)
        print(to_text(response))
    except (ValueError, KeyboardInterrupt):
        print()


def _clean_url(href):
    # DuckDuckGo wraps links in a redirect — extract the real URL
    if "uddg=" in href:
        start = href.index("uddg=") + 5
        end = href.find("&", start)
        raw = href[start:] if end == -1 else href[start:end]
        return unquote(raw)
    return href
