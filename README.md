# MCP GitHub App Server

A lightweight MCP (Model Context Protocol) server that provides GitHub operations using GitHub App authentication instead of personal access tokens.

## Primary Function

The main purpose of this server is to obtain temporary GitHub tokens for accessing private repositories using GitHub App authentication. The primary tool is:

- **`clone_repo`**: Obtain a GitHub token for accessing a repository
  - Parameters: `owner` (string), `repo` (string)
  - Returns a GitHub token that can be used for authentication

Note: Despite the name, this tool does not actually clone the repository. It only returns a GitHub token that can be used to clone the repository directly using git.

## Additional Tools

The server also provides tools for performing common Git operations:

- **`create_branch`**: Create a new branch in a GitHub repository
  - Parameters: `owner` (string), `repo` (string), `new_branch` (string), `from_ref` (string, optional, default: "heads/main")

- **`push`**: Push changes to a GitHub repository
  - Parameters: `cwd` (string), `remote` (string, optional, default: "origin"), `branch` (string, optional, default: "main")

- **`create_pull_request`**: Create a pull request in a GitHub repository
  - Parameters: `owner` (string), `repo` (string), `title` (string), `head` (string), `base` (string, optional, default: "main"), `body` (string, optional)

- **`merge_pull_request`**: Merge a pull request in a GitHub repository
  - Parameters: `owner` (string), `repo` (string), `number` (integer), `merge_method` (string, optional, default: "squash"), `commit_title` (string, optional), `commit_message` (string, optional)

## Prerequisites

- A GitHub App installed with repository permissions for Contents (Read & write) and Pull requests (Read & write)
- Environment variables: `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`, `GITHUB_INSTALLATION_ID`

## Installation

```bash
pip install .
```

## Usage

### Docker Usage (Recommended)

Build the Docker image:
```bash
docker build . -t localhost/test
```

### Get GitHub Token

Execute the `clone_repo` command to get a GitHub token:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "clone_repo", "params": {"owner": "fictional-org", "repo": "private-repo"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

This returns a JSON response with the GitHub token:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"github_token": "ghs_tokenhere"}}
```

You can then use this token to clone the repository directly:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

## End-to-End Example

1. Build the server:
```bash
docker build . -t localhost/test
```

2. Get a GitHub token by running the clone_repo command:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "clone_repo", "params": {"owner": "fictional-org", "repo": "private-repo"}}' | docker run -i --rm -e GITHUB_APP_ID="$GITHUB_APP_ID" -e GITHUB_PRIVATE_KEY="$GITHUB_PRIVATE_KEY" -e GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" localhost/test
```

This will return a JSON response like:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"github_token": "ghs_tokenhere"}}
```

3. Use the returned token to clone the repository:
```bash
git clone https://x-access-token:ghs_tokenhere@github.com/fictional-org/private-repo.git
```

## Testing

Run tests with:
```bash
python3 -m pytest tests/ -v
```

## Security Notes

- Installation tokens expire after approximately 1 hour
- The server caches and refreshes tokens automatically
