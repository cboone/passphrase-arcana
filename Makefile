PREFIX ?= $(HOME)/.local

.PHONY: all clean fetch extract validate score build install uninstall

all: build

fetch:
	uv run src/fetch_texts.py
	uv run src/fetch_external.py

extract: fetch
	uv run src/extract_words.py

validate: extract
	uv run src/validate_words.py

score: validate
	uv run src/score_typing.py

build: score
	uv run src/build_list.py

install:
	@mkdir -p "$(PREFIX)/bin"
	ln -sf "$(CURDIR)/bin/generate-passphrase" "$(PREFIX)/bin/generate-passphrase"
	@echo "Installed: $(PREFIX)/bin/generate-passphrase -> $(CURDIR)/bin/generate-passphrase"

uninstall:
	rm -f "$(PREFIX)/bin/generate-passphrase"
	@echo "Removed: $(PREFIX)/bin/generate-passphrase"

clean:
	rm -rf data/raw data/words data/validated data/scored

test:
	uv run pytest tests/ -v
