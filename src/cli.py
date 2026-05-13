import argparse
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
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-u", metavar="URL", dest="url", help="URL to fetch")
    parser.add_argument("-s", metavar="TERM", dest="search", nargs="+", help="Search term")
    parser.add_argument("-h", action="store_true", dest="help", help="Show help")

    parsed = parser.parse_args(args)

    if parsed.help or not args:
        print(HELP_TEXT)
        sys.exit(0)

    if parsed.url:
        from src.http_client import fetch
        from src.html_parser import to_text

        response = fetch(parsed.url)
        print(to_text(response))

    elif parsed.search:
        from src.search import search

        term = " ".join(parsed.search)
        search(term)

    else:
        print(HELP_TEXT)
        sys.exit(1)
