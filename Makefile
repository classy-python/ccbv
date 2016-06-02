help:
	@echo "Usage:"
	@echo "    make help:           prints this help."
	@echo "    make all-versions:   install all Django versions and generate docs"
	@echo "    make run:            run local dev server"
	@echo "    make setup:          set up local env for dev"

1.3:
	versions/1.3/bin/ccbv --location=versions generate 1.3 django.views.generic

1.4:
	versions/1.4/bin/ccbv --location=versions generate 1.4 django.views.generic django.contrib.formtools.wizard.views

1.5:
	versions/1.5/bin/ccbv --location=versions generate 1.5 django.views.generic django.contrib.formtools.wizard.views

1.6:
	versions/1.6/bin/ccbv --location=versions generate 1.6 django.views.generic django.contrib.formtools.wizard.views

1.7:
	versions/1.7/bin/ccbv --location=versions generate 1.7 django.views.generic django.contrib.formtools.wizard.views

1.8:
	versions/1.8/bin/ccbv --location=versions generate 1.8 django.views.generic

1.9:
	versions/1.9/bin/ccbv --location=versions generate 1.9 django.views.generic django.contrib.auth.mixins


all-versions:
	ccbv --location=versions install-versions 1.{3..9}
	make 1.{3..9}

run:
	@(cd output; python3 -m http.server)

setup:
	pip install -e .

static:
	@cat \
		ccbv/static/bootstrap-2.0.4.css \
		ccbv/static/bootstrap-responsive-2.0.3.css \
		ccbv/static/ccbv.css \
		ccbv/static/manni.css \
		> output/style.css && \
		echo 'Built Styles'
	@cat \
		ccbv/static/jquery-1.7.1.min.js \
		ccbv/static/bootstrap-collapse-2.0.1.js \
		ccbv/static/modernizr-2.5.3.min.js \
		ccbv/static/bootstrap-dropdowns-2.0.3.js \
		ccbv/static/ccbv.js \
		ccbv/static/bootstrap-tooltip-2.0.4.js \
		> output/script.js && \
		echo 'Built Scripts'
