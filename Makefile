.PHONY: install-dev test

install-dev:
	uv sync

test:
	uv run pytest -v
