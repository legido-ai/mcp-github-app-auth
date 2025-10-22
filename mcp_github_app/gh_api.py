# mcp_github_app/gh_api.py
import requests
from .auth import auth_header

API = "https://api.github.com"

class GhApiError(RuntimeError):
    pass


def _req(method: str, path: str, **kwargs):
    h = auth_header()
    h.update({"X-GitHub-Api-Version": "2022-11-28", "User-Agent": "mcp-github-app-python"})
    resp = requests.request(method, f"{API}{path}", headers=h, **kwargs)
    if resp.status_code // 100 != 2:
        raise GhApiError(f"GitHub API {method} {path} failed: {resp.status_code} {resp.text}")
    return resp.json() if resp.text else {}


# --- Branches ---

def create_branch(owner: str, repo: str, new_branch: str, from_ref: str = "heads/main"):
    # 1) Get sha of base ref
    ref = _req("GET", f"/repos/{owner}/{repo}/git/ref/{from_ref}")
    sha = ref["object"]["sha"]
    # 2) Create new ref
    return _req("POST", f"/repos/{owner}/{repo}/git/refs", json={"ref": f"refs/heads/{new_branch}", "sha": sha})


# --- Pull Requests ---

def create_pull_request(owner: str, repo: str, title: str, head: str, base: str = "main", body: str | None = None):
    return _req("POST", f"/repos/{owner}/{repo}/pulls", json={"title": title, "head": head, "base": base, "body": body})


def merge_pull_request(owner: str, repo: str, pr_number: int, merge_method: str = "squash", commit_title: str | None = None, commit_message: str | None = None):
    payload = {"merge_method": merge_method}
    if commit_title: payload["commit_title"] = commit_title
    if commit_message: payload["commit_message"] = commit_message
    return _req("PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", json=payload)


# --- Files ---

def create_or_update_file(owner: str, repo: str, path: str, content_b64: str, message: str, branch: str = "main", sha: str | None = None):
    body = {"message": message, "content": content_b64, "branch": branch}
    if sha: body["sha"] = sha
    return _req("PUT", f"/repos/{owner}/{repo}/contents/{path}", json=body)