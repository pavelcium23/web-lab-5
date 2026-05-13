# go2web

A command-line HTTP client built on raw TCP sockets — no built-in or third-party HTTP libraries used.

## Demo

![go2web demo](demo.gif)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x go2web
```

## Usage

```bash
./go2web -h                        # show help
./go2web -u <URL>                  # fetch a URL and print readable output
./go2web -s <search term>          # search DuckDuckGo, print top 10 results
```

## Examples

```bash
./go2web -u https://example.com
./go2web -u https://httpbin.org/get
./go2web -s python socket programming
./go2web -s "what is HTTP"
```

## Features

| Feature | Status |
|---|---|
| `-h`, `-u`, `-s` flags | done |
| Raw TCP sockets (HTTP + HTTPS) | done |
| Human-readable output (no HTML tags) | done |
| HTTP redirects (301/302/303/307/308) | done |
| Interactive search result fetch | done |
| File-based HTTP cache (Cache-Control / Expires) | done |
| Content negotiation (JSON + HTML auto-detection) | done |

## How it works

- Opens a raw `socket.create_connection()` to the host
- Wraps with `ssl` for HTTPS
- Sends a hand-crafted `HTTP/1.1 GET` request
- Parses the response manually (status line, headers, chunked body, gzip)
- Strips HTML tags via BeautifulSoup or pretty-prints JSON
- Caches responses in `.cache/` keyed by SHA-256 of the URL
