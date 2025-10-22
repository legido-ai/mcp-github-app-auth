# mcp_github_app/git_ops.py
import os, subprocess, tempfile
from .auth import get_installation_token

class GitError(RuntimeError):
    pass


def _run(cmd, cwd=None):
    res = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if res.returncode != 0:
        raise GitError(f"git failed: {' '.join(cmd)}\n{res.stdout}\n{res.stderr}")
    return res.stdout


def clone_repo(owner: str, repo: str, dest_dir: str, branch: str | None = None):
    token, _ = get_installation_token()
    url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"
    cmd = ["git", "clone", url, dest_dir]
    if branch:
        cmd.extend(["-b", branch])
    return _run(cmd)


def set_author(cwd: str, name: str, email: str):
    _run(["git", "config", "user.name", name], cwd=cwd)
    _run(["git", "config", "user.email", email], cwd=cwd)


def commit_all(cwd: str, message: str):
    _run(["git", "add", "-A"], cwd=cwd)
    _run(["git", "commit", "-m", message], cwd=cwd)


def push(cwd: str, remote: str = "origin", branch: str = "main"):
    token, _ = get_installation_token()
    # Ensure remote URL includes token for this process
    _run(["git", "remote", "set-url", remote, f"https://x-access-token:{token}@github.com/$(git config --get remote.{remote}.url | sed 's#.*github.com/##')"], cwd=cwd)
    return _run(["git", "push", "-u", remote, branch], cwd=cwd)