help:
	@echo "Usage:"
	@echo "    make help: prints this help."
	@echo "    make test: runs the tests."

test:
	coverage run -m pytest -vvv
	coverage report

mypy:
	mypy . | mypy-json-report > mypy-ratchet.json
	git diff --exit-code mypy-ratchet.json
