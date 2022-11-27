help:
	@echo "Usage:"
	@echo "    make help: prints this help."
	@echo "    make test: runs the tests."
	@echo "    make build: install as for a deployed environment."

test:
	coverage run -m pytest -vvv
	coverage report

mypy:
	mypy . | mypy-json-report > mypy-ratchet.json
	git diff --exit-code mypy-ratchet.json

build:
	pip install -r requirements.txt
	python manage.py collectstatic --no-input
