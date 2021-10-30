SHELL=/bin/bash

.PHONY = setup init run clean

# Defines the default target that `make` will try to make, or in the case of a phony target, execute the specified commands
# This target is executed whenever we just type `make`
.DEFAULT_GOAL = run

# This will install the package manager Poetry
setup:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | ${PYTHON} -
	@echo "Done."

init:
	poetry install

run:
	time poetry run python main.py

clean:
	rm -r .venv 