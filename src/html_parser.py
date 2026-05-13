import json as json_module
from bs4 import BeautifulSoup

JSON_TYPES = ("application/json", "application/ld+json", "application/vnd.api+json")
HTML_TYPES = ("text/html", "application/xhtml+xml")


def to_text(response):
    content_type = response.get("content_type", "")
    body = response.get("body", "")
    status = response.get("status", 0)

    if status >= 400:
        print(f"[Error {status}: {response.get('status_text', '')}]\n")

    detected = _detect_type(content_type, body)
    print(f"[Content-Type: {detected}]\n")

    if detected == "json":
        return _format_json(body)

    if detected == "html":
        return _html_to_text(body)

    return body.strip()


def _detect_type(content_type, body):
    for t in JSON_TYPES:
        if t in content_type:
            return "json"
    for t in HTML_TYPES:
        if t in content_type:
            return "html"
    # Sniff body as fallback
    stripped = body.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    if stripped.startswith("<!") or stripped.lower().startswith("<html"):
        return "html"
    return "text"


def _format_json(body):
    try:
        data = json_module.loads(body)
        return json_module.dumps(data, indent=2, ensure_ascii=False)
    except json_module.JSONDecodeError:
        return body.strip()


def _html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "meta", "link", "noscript", "head", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)
