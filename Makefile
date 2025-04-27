help:
	@echo "Usage:"
	@echo "    make help: prints this help."
	@echo "    make test: runs the tests."
	@echo "    make build: install as for a deployed environment."
	@echo "    make run-prod: run webserver as in deployed environment."
	@echo "    make compile: compile the requirements specs."

_uv:
	# ensure uv is installed
	pip install uv

test:
	coverage run -m pytest -vvv
	coverage report

mypy:
	mypy . | mypy-json-report > mypy-ratchet.json
	git diff --exit-code mypy-ratchet.json

build: _uv
	uv pip install -r requirements.prod.txt -r requirements.dev.txt
	python manage.py collectstatic --no-input
	rm -f ccbv.sqlite
	python manage.py migrate
	python manage.py load_all_django_versions

run-prod:
	gunicorn core.wsgi --log-file -

compile: _uv
	uv pip compile --quiet requirements.prod.in --output-file=requirements.prod.txt
	uv pip compile --quiet requirements.dev.in --output-file=requirements.dev.txt
