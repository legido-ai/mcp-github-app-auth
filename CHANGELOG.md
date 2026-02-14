# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.0] - 2026-02-14

### Added
- Makefile with `test-mcp-validation` target to validate Github MCP server with proper initialization handshake.
- Architecture detection in tests to use ARM tag for aarch64 systems.
- Integration with docker-openclaw `full-test` suite via `test-github-app-auth-mcp-validation` target.

### Changed
- CI publishes Docker images for both `linux/amd64` and `linux/arm64`.
- CI now also publishes an explicit `ghcr.io/legido-ai/mcp-github-app-auth:arm` tag for ARM deployments.
