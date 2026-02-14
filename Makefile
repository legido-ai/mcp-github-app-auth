.PHONY: help test test-mcp-validation build docker clean

# Default target
.DEFAULT_GOAL := help

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show help
	@echo "$(BLUE)MCP GitHub App Auth - Make Commands$(NC)"
	@echo ""
	@echo "  $(GREEN)test$(NC)                 Run all tests"
	@echo "  $(GREEN)test-mcp-validation$(NC)  Validate Github MCP server with init handshake"
	@echo "  $(GREEN)build$(NC)                Build the project"
	@echo "  $(GREEN)docker$(NC)               Build Docker image"
	@echo "  $(GREEN)clean$(NC)                Clean artifacts"
	@echo ""

# Run all tests
test: test-mcp-validation

# Test Github MCP validation with initialization handshake
test-mcp-validation: ## Validate Github MCP server
	@echo "Testing Github MCP validation..."
	@if [ -z "$$GITHUB_APP_ID" ] || [ -z "$$GITHUB_PRIVATE_KEY" ] || [ -z "$$GITHUB_INSTALLATION_ID" ]; then \
		echo "$(RED)ERROR: Missing required environment variables$(NC)"; \
		echo "Please set: GITHUB_APP_ID, GITHUB_PRIVATE_KEY, GITHUB_INSTALLATION_ID"; \
		exit 1; \
	fi
	@arch=$$(uname -m); \
	if [ "$$arch" = "aarch64" ]; then \
		tag="arm"; \
		echo "Detected ARM architecture, using tag: $$tag"; \
	else \
		tag="latest"; \
		echo "Detected non-ARM architecture, using tag: $$tag"; \
	fi; \
	echo "Running MCP Github App Auth server test..."; \
	output=$$(printf '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "manual-test", "version": "1.0"}}}\n{"jsonrpc": "2.0", "method": "notifications/initialized"}\n{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | \
	docker run -i --rm \
		-e GITHUB_APP_ID="$$GITHUB_APP_ID" \
		-e GITHUB_PRIVATE_KEY="$$GITHUB_PRIVATE_KEY" \
		-e GITHUB_INSTALLATION_ID="$$GITHUB_INSTALLATION_ID" \
		ghcr.io/legido-ai/mcp-github-app-auth:$$tag 2>&1); \
	result=$$?; \
	echo "$$output"; \
	if [ $$result -ne 0 ]; then \
		echo "$(RED)TEST FAILED: Docker command failed with exit code $$result$(NC)"; \
		exit 1; \
	fi; \
	if echo "$$output" | grep -q '"jsonrpc":"2.0"'; then \
		if echo "$$output" | grep -q '"result"'; then \
			echo "$(GREEN)✓ TEST PASSED: Valid JSON-RPC response received$(NC)"; \
			exit 0; \
		else \
			echo "$(RED)TEST FAILED: No result field in response$(NC)"; \
			exit 1; \
		fi; \
	elif echo "$$output" | grep -q '"error"'; then \
		echo "$(RED)TEST FAILED: Error in response$(NC)"; \
		exit 1; \
	else \
		echo "$(RED)TEST FAILED: Invalid JSON-RPC response$(NC)"; \
		exit 1; \
	fi

build: ## Build placeholder
	@echo "Building project..."
	@python3 -m pip install -e . >/dev/null 2>&1 && echo "$(GREEN)✓ Build successful$(NC)" || echo "$(RED)✗ Build failed$(NC)"

docker: ## Docker build
	@echo "Building Docker image..."
	@docker build . -t mcp-github-app-auth:latest
	@echo "$(GREEN)✓ Docker build successful$(NC)"

clean: ## Clean artifacts
	@echo "Cleaning artifacts..."
	@rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__ || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"
