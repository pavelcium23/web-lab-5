import sys


HELP_TEXT = """go2web - HTTP client over raw TCP sockets

Usage:
  go2web -u <URL>          Make an HTTP request to the URL and print response
  go2web -s <search-term>  Search using DuckDuckGo and print top 10 results
  go2web -h                Show this help message

Examples:
  go2web -u https://example.com
  go2web -s python socket programming
  go2web -s "what is HTTP"
"""


def run(args):
    if not args or args[0] in ("-h", "--help"):
        print(HELP_TEXT)
        sys.exit(0)

    flag = args[0]
    rest = args[1:]

    if flag == "-u":
        if not rest:
            print("Error: -u requires a URL.\n")
            print(HELP_TEXT)
            sys.exit(1)
        _cmd_url(rest[0])

    elif flag == "-s":
        if not rest:
            print("Error: -s requires a search term.\n")
            print(HELP_TEXT)
            sys.exit(1)
        _cmd_search(" ".join(rest))

    else:
        print(f"Unknown option: {flag}\n")
        print(HELP_TEXT)
        sys.exit(1)


def _cmd_url(url):
    from src.http_client import fetch
    from src.html_parser import to_text
    try:
        response = fetch(url)
        print(to_text(response))
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Connection error: {e}")
        sys.exit(1)


def _cmd_search(term):
    from src.search import search
    try:
        search(term)
    except OSError as e:
        print(f"Connection error: {e}")
        sys.exit(1)
