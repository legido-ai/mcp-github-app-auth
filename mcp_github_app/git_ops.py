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


import os

def clone_repo(owner: str, repo: str, dest_dir: str, branch: str | None = None):
    """
    Clone a GitHub repository and return the GitHub token.

    The returned token can be used for various Git operations including:
    - git clone, git push, git pull, git fetch

    Token format: https://x-access-token:<TOKEN>@github.com/<OWNER>/<REPO>.git

    Args:
        owner: GitHub repository owner/organization
        repo: GitHub repository name
        dest_dir: Destination directory for the clone
        branch: Optional specific branch to clone

    Returns:
        Dict with 'clone_output' and 'github_token' keys
    """
    token, _ = get_installation_token()
    url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"

    # Ensure the destination directory exists with proper permissions
    os.makedirs(dest_dir, mode=0o777, exist_ok=True)

    cmd = ["git", "clone", url, dest_dir]
    if branch:
        cmd.extend(["-b", branch])
    result = _run(cmd)
    return {"clone_output": result, "github_token": token}


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