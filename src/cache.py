import os
import json
import hashlib
import time

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")


def _key(url):
    return hashlib.sha256(url.encode()).hexdigest()


def _path(url):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, _key(url) + ".json")


def get(url):
    path = _path(url)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        if time.time() < entry["expires_at"]:
            print(f"  [cache hit] {url}")
            return entry["response"]
        os.remove(path)
    except (json.JSONDecodeError, KeyError, OSError):
        pass
    return None


def store(url, response):
    max_age = _max_age(response["headers"])
    if max_age <= 0:
        return
    entry = {
        "expires_at": time.time() + max_age,
        "response": response,
    }
    try:
        with open(_path(url), "w", encoding="utf-8") as f:
            json.dump(entry, f)
    except OSError:
        pass


DEFAULT_TTL = 3600  # 1 hour for responses with no cache directives


def _max_age(headers):
    cc = headers.get("cache-control", "")
    for part in cc.split(","):
        part = part.strip()
        if part.startswith("no-store") or part.startswith("no-cache"):
            return 0
        if part.startswith("max-age="):
            try:
                return int(part.split("=")[1])
            except ValueError:
                pass
    # Fall back to Expires header
    expires = headers.get("expires", "")
    if expires:
        try:
            from email.utils import parsedate_to_datetime
            exp_time = parsedate_to_datetime(expires).timestamp()
            return max(0, int(exp_time - time.time()))
        except Exception:
            pass
    return DEFAULT_TTL
