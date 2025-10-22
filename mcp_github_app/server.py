# mcp_github_app/server.py
from mcp.server import Server
from mcp.types import Tool, ToolArgument
from pydantic import BaseModel
from . import git_ops, gh_api

server = Server("github-app")

# ---- Models ----
class CloneArgs(BaseModel):
    owner: str
    repo: str
    dest_dir: str
    branch: str | None = None

class BranchArgs(BaseModel):
    owner: str
    repo: str
    new_branch: str
    from_ref: str = "heads/main"

class PushArgs(BaseModel):
    cwd: str
    remote: str = "origin"
    branch: str = "main"

class PRCreateArgs(BaseModel):
    owner: str
    repo: str
    title: str
    head: str
    base: str = "main"
    body: str | None = None

class PRMergeArgs(BaseModel):
    owner: str
    repo: str
    number: int
    merge_method: str = "squash"
    commit_title: str | None = None
    commit_message: str | None = None

# ---- Tools ----
@server.tool()
def clone_repo(args: CloneArgs):
    return git_ops.clone_repo(args.owner, args.repo, args.dest_dir, args.branch)

@server.tool()
def create_branch(args: BranchArgs):
    return gh_api.create_branch(args.owner, args.repo, args.new_branch, args.from_ref)

@server.tool()
def push(args: PushArgs):
    return git_ops.push(args.cwd, args.remote, args.branch)

@server.tool()
def create_pull_request(args: PRCreateArgs):
    return gh_api.create_pull_request(args.owner, args.repo, args.title, args.head, args.base, args.body)

@server.tool()
def merge_pull_request(args: PRMergeArgs):
    return gh_api.merge_pull_request(args.owner, args.repo, args.number, args.merge_method, args.commit_title, args.commit_message)

if __name__ == "__main__":
    server.run_stdio()