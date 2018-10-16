OUTPUTDIR = output
VENVS_PATH = versions

help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make build            build the full site."
	@echo "    make clean            remove the output directory."
	@echo "    make docs             build the documentation."
	@echo "    make format           run the auto-format check."
	@echo "    make lint             run the import sorter check."
	@echo "    make setup:           set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: build
build: clean
	@ccbv install $(VENVS_PATH)

.PHONY: clean
clean:
	@mkdir -p $(OUTPUTDIR)
	@rm -rf $(OUTPUTDIR)/*
	@echo "Cleaned output directory"

.PHONY: docs
docs:
	@sphinx-build -b html docs/source docs/build -n -W

.PHONY: format
format:
	@echo "Running black" && pipenv run black --check ccbv tests || exit 1

.PHONY: lint
lint:
	@echo "Running flake8" && pipenv run flake8 --show-source || exit 1

.PHONY: setup
setup:
	pipenv install --dev
	pip install -e .

.PHONY: sort
sort:
	@echo "Running Isort" && pipenv run isort --check-only --diff || exit 1

.PHONY: test
test:
	pipenv run pytest
