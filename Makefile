PREFIX ?= $(HOME)/.local

.PHONY: all clean fetch extract filter-proper-nouns validate score build install uninstall test lint fmt format format-check lint-md help

all: build

fetch:
	uv run src/fetch_texts.py
	uv run src/fetch_external.py

extract: fetch
	uv run src/extract_words.py

filter-proper-nouns: extract
	uv run src/filter_proper_nouns.py

validate: filter-proper-nouns
	uv run src/validate_words.py

score: validate
	uv run src/score_typing.py

build: score
	uv run src/build_list.py

install:
	@mkdir -p "$(PREFIX)/bin"
	ln -sf "$(CURDIR)/bin/arcana" "$(PREFIX)/bin/arcana"
	@echo "Installed: $(PREFIX)/bin/arcana -> $(CURDIR)/bin/arcana"

uninstall:
	rm -f "$(PREFIX)/bin/arcana"
	@echo "Removed: $(PREFIX)/bin/arcana"

clean:
	rm -rf data/raw data/words data/validated data/scored

test:
	uv run pytest tests/ -v

lint:
	uvx ruff check .

fmt:
	uvx ruff format --check .

format:
	npx prettier --write .

format-check:
	npx prettier --check .

lint-md:
	npx markdownlint-cli2 "**/*.md"

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'
