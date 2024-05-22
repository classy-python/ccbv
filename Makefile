help:
	@echo "Usage:"
	@echo "    make help: prints this help."
	@echo "    make test: runs the tests."
	@echo "    make build: install as for a deployed environment."
	@echo "    make run-prod: run webserver as in deployed environment."
	@echo "    make compile: compile the requirements specs."

test:
	coverage run -m pytest -vvv
	coverage report

mypy:
	mypy . | mypy-json-report > mypy-ratchet.json
	git diff --exit-code mypy-ratchet.json

build:
	pip install -r requirements.prod.txt -r requirements.dev.txt
	python manage.py collectstatic --no-input
	rm --force ccbv.sqlite
	DATABASE_URL=sqlite:///ccbv.sqlite python manage.py migrate
	DATABASE_URL=sqlite:///ccbv.sqlite python manage.py load_all_django_versions

run-prod:
	DATABASE_URL=sqlite:///ccbv.sqlite gunicorn core.wsgi --log-file -

compile:
	pip-compile requirements.prod.in --output-file=requirements.prod.txt
	pip-compile requirements.dev.in --output-file=requirements.dev.txt
