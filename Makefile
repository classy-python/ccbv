help:
	@echo "Usage:"
	@echo "    make help: prints this help."
	@echo "    make test: runs the tests."

test:
	python manage.py test cbv

1.3:
	python ccbv/run.py django/django 1.3

1.4:
	python ccbv/run.py django/django 1.4

1.5:
	python ccbv/run.py django/django 1.5

1.6:
	python ccbv/run.py django/django 1.6

all: 1.3 1.4 1.5 1.6
