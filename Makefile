help:
	@echo "Usage:"
	@echo "    make help:           prints this help."
	@echo "    make all-versions:   install all Django versions and generate docs"
	@echo "    make run:            run local dev server"
	@echo "    make setup:          set up local env for dev"

all-versions:
	ccbv --location=versions install-versions 1.{3..9}
	ccbv --location=versions generate 1.3 django.views.generic
	ccbv --location=versions generate 1.4 django.views.generic
	ccbv --location=versions generate 1.5 django.views.generic
	ccbv --location=versions generate 1.6 django.views.generic
	ccbv --location=versions generate 1.7 django.views.generic
	ccbv --location=versions generate 1.8 django.views.generic
	ccbv --location=versions generate 1.9 django.views.generic

run:
	@(cd output; python3 -m http.server)

setup:
	pip install -e .
