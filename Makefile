help:
	@echo "Usage:"
	@echo "    make help: prints this help."
	@echo "    make test: runs the tests."

test:
	coverage run -m pytest -vvv
	coverage report
