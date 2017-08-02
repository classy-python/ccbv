help:
	@echo "Usage:"
	@echo "    make help:           prints this help."
	@echo "    make run:            run local dev server"
	@echo "    make setup:          set up local env for dev"

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
