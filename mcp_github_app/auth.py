# mcp_github_app/auth.py
import time, os, json, requests, jwt
from typing import Tuple
import datetime

_GHS_CACHE = {"token": None, "exp": 0}

class AppAuthError(RuntimeError):
    pass

def _now() -> int:
    return int(time.time())

def get_installation_token() -> Tuple[str, int]:
    """Return a valid installation token and its expiry epoch seconds.
    Creates a fresh one if absent/expired.
    """
    global _GHS_CACHE
    if _GHS_CACHE["token"] and _GHS_CACHE["exp"] - 120 > _now():
        return _GHS_CACHE["token"], _GHS_CACHE["exp"]

    app_id = os.environ.get("GITHUB_APP_ID")
    installation_id = os.environ.get("GITHUB_INSTALLATION_ID")
    private_key = os.environ.get("GITHUB_PRIVATE_KEY")
    if not (app_id and installation_id and private_key):
        raise AppAuthError("Missing GITHUB_APP_ID / GITHUB_INSTALLATION_ID / GITHUB_PRIVATE_KEY")

    # 1) Sign JWT (10 min)
    now = _now()
    payload = {"iat": now, "exp": now + 10 * 60, "iss": app_id}
    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

    # 2) Exchange for installation token
    api_host = os.environ.get("GITHUB_API_HOST", "https://api.github.com")
    url = f"{api_host}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "mcp-github-app-python"
    }
    resp = requests.post(url, headers=headers, json={})
    if resp.status_code // 100 != 2:
        raise AppAuthError(f"Failed to get installation token: {resp.status_code} {resp.text}")

    data = resp.json()
    token = data["token"]
    # expires_at ISO8601 → epoch
    exp = int(datetime.datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00")).timestamp())
    _GHS_CACHE = {"token": token, "exp": exp}
    return token, exp


def auth_header() -> dict:
    token, _ = get_installation_token()
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}