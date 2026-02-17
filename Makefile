.PHONY: all build clean manpage test

OUT_DIR ?= dist

all: build

build: manpage
	uv build --wheel --out-dir $(OUT_DIR)

manpage: man/datetimecalc.1

man/datetimecalc.1: src/datetimecalc/__main__.py man/extra-sections.man
	uv run argparse-manpage \
		--module datetimecalc.__main__ \
		--function get_parser \
		--project-name datetimecalc \
		--description "parse and compute with natural language datetime expressions" \
		--author "Backplane <actualben@users.noreply.github.com>" \
		--url "https://github.com/backplane/datetimecalc" \
		--include man/extra-sections.man \
		--output man/datetimecalc.1

test:
	uv run pytest

clean:
	rm -rf dist/ build/ *.egg-info
