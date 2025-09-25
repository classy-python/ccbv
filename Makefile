help:
	@echo "Usage:"
	@echo "    make help: prints this help."
	@echo "    make test: runs the tests."
	@echo "    make build: install as for a deployed environment."
	@echo "    make run-prod: run webserver as in deployed environment."

test:
	uv run coverage run -m pytest -vvv tests
	uv run coverage report

mypy:
	uv run mypy . | uv run mypy-json-report > mypy-ratchet.json
	git diff --exit-code mypy-ratchet.json

build:
	uv run manage.py collectstatic --no-input
	rm -f ccbv.sqlite
	uv run manage.py migrate
	uv run manage.py load_all_django_versions

build-prod:
	rm -rf staticfiles/*
	uv run --no-dev manage.py collectstatic --no-input

run-prod:
	gunicorn core.wsgi --log-file -
