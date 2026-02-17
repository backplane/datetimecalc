OUT_DIR ?= dist

.PHONY: all
all: wheel

.PHONY: test
test:
	@echo "==> $@"
	uv run pytest

.PHONY: clean
clean:
	@echo "==> $@"
	rm -rf dist/ build/ *.egg-info man/datetimecalc.1

.PHONY: wheel
wheel: manpages
	@echo "==> $@"
	uv build --wheel --out-dir $(OUT_DIR)

.PHONY: manpages
manpages: man/datetimecalc.1

man/datetimecalc.1: man/extra-sections.man src/datetimecalc/__main__.py
	@echo "==> $@"
	uv run argparse-manpage \
		--module datetimecalc.__main__ \
		--function get_parser \
		--project-name datetimecalc \
		--description "parse and compute with natural language datetime expressions" \
		--author "Backplane <actualben@users.noreply.github.com>" \
		--url "https://github.com/backplane/datetimecalc" \
		--include "$<" \
		--output "$@"
