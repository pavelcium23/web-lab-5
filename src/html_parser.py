import json as json_module
from bs4 import BeautifulSoup


def to_text(response):
    content_type = response.get("content_type", "")
    body = response.get("body", "")
    status = response.get("status", 0)

    if status >= 400:
        print(f"[Error {status}: {response.get('status_text', '')}]")

    if "application/json" in content_type:
        return _format_json(body)

    if "text/html" in content_type or body.lstrip().startswith("<!"):
        return _html_to_text(body)

    return body.strip()


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
    chunks = [line for line in lines if line]
    return "\n".join(chunks)
