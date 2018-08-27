OUTPUTDIR = output

help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make clean            remove the output directory."
	@echo "    make build            build the full site."
	@echo "    make deploy           deploy the built site."
	@echo "    make docs             build the documentation."
	@echo "    make install          install the dependencies."
	@echo "    make lint             run the linters."
	@echo "    make test             run the tests."

.PHONY: clean
clean:
	rm -rf $(OUTPUTDIR)

.PHONY: build
build: clean
	python -m ccbv config.ini $(OUTPUTDIR)

.PHONY: deploy
deploy: clean build
	echo "TODO: build, save to GitHub Pages branch, commit, push"

.PHONY: docs
docs:
	@sphinx-build -b html docs/source docs/build -n -W

.PHONY: install
install:
	pipenv install --dev

.PHONY: lint
lint:
	@echo "Running Isort" && pipenv run isort --check-only --diff || exit 1
	@echo "Running black" && pipenv run black --check --quiet ccbv tests || exit 1
	@echo "Running flake8" && pipenv run flake8 --show-source || exit 1

.PHONY: test
test:
	pytest
