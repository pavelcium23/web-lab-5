import socket
import ssl
import zlib
import certifi
from urllib.parse import urlparse

MAX_REDIRECTS = 10


def _parse_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    parsed = urlparse(url)
    scheme = parsed.scheme
    host = parsed.hostname
    port = parsed.port or (443 if scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    return scheme, host, port, path


def _send_request(scheme, host, port, path, extra_headers=None):
    sock = socket.create_connection((host, port), timeout=15)
    if scheme == "https":
        ctx = ssl.create_default_context(cafile=certifi.where())
        sock = ctx.wrap_socket(sock, server_hostname=host)

    headers = {
        "Host": host,
        "User-Agent": "go2web/1.0",
        "Accept": "text/html,application/json,*/*;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
    }
    if extra_headers:
        headers.update(extra_headers)

    header_lines = "\r\n".join(f"{k}: {v}" for k, v in headers.items())
    request = f"GET {path} HTTP/1.1\r\n{header_lines}\r\n\r\n"
    sock.sendall(request.encode())

    raw = b""
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        raw += chunk
    sock.close()
    return raw


def _decode_chunked(data):
    result = b""
    while data:
        crlf = data.find(b"\r\n")
        if crlf == -1:
            break
        try:
            size = int(data[:crlf].split(b";")[0].strip(), 16)
        except ValueError:
            break
        if size == 0:
            break
        result += data[crlf + 2: crlf + 2 + size]
        data = data[crlf + 2 + size + 2:]
    return result


def _parse_response(raw):
    sep = raw.find(b"\r\n\r\n")
    if sep == -1:
        raise ValueError("Invalid HTTP response: no header/body separator")

    header_bytes = raw[:sep]
    body_bytes = raw[sep + 4:]

    header_text = header_bytes.decode("utf-8", errors="replace")
    lines = header_text.split("\r\n")

    parts = lines[0].split(" ", 2)
    status_code = int(parts[1])
    status_text = parts[2] if len(parts) > 2 else ""

    headers = {}
    for line in lines[1:]:
        if ": " in line:
            key, _, value = line.partition(": ")
            headers[key.lower()] = value.strip()

    if headers.get("transfer-encoding", "").lower() == "chunked":
        body_bytes = _decode_chunked(body_bytes)

    encoding = headers.get("content-encoding", "")
    if encoding == "gzip":
        body_bytes = zlib.decompress(body_bytes, 16 + zlib.MAX_WBITS)
    elif encoding == "deflate":
        try:
            body_bytes = zlib.decompress(body_bytes)
        except zlib.error:
            body_bytes = zlib.decompress(body_bytes, -zlib.MAX_WBITS)

    content_type = headers.get("content-type", "")
    charset = "utf-8"
    if "charset=" in content_type:
        charset = content_type.split("charset=")[-1].strip().split(";")[0]

    body = body_bytes.decode(charset, errors="replace")

    return {
        "status": status_code,
        "status_text": status_text,
        "headers": headers,
        "body": body,
        "content_type": content_type,
    }


def fetch(url, _redirects=0, extra_headers=None):
    if _redirects > MAX_REDIRECTS:
        raise RuntimeError("Too many redirects")

    scheme, host, port, path = _parse_url(url)
    raw = _send_request(scheme, host, port, path, extra_headers)
    response = _parse_response(raw)

    if response["status"] in (301, 302, 303, 307, 308):
        location = response["headers"].get("location", "")
        if location:
            if not location.startswith("http"):
                location = f"{scheme}://{host}{location}"
            print(f"  → Redirect {response['status']}: {location}")
            return fetch(location, _redirects + 1, extra_headers)

    return response
