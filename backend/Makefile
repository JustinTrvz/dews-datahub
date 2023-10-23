VENV_NAME := venv
PYTHON := $(VENV_NAME)/bin/python
PIP := $(VENV_NAME)/bin/pip

.PHONY: all venv requirements api main clean

# - - - Help text - - -
help:
	@echo "Available targets:"
	@echo "  venv - Create a virtual environment"
	@echo "  requirements - Install project requirements"
	@echo "  api - Run the api.py script"
	@echo "  main - Run the main.py script"
	@echo "  clean - Clean up virtual environment and cached files"

# - - - Backend - - -

venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_NAME)
	$(PIP) install -r requirements.txt

requirements: venv
	@echo "Installing requirements..."
	
setup: venv requirements
	@echo "Created virtual environment and installed requirements..."


api: venv
	@echo "Activating virtual environment and running api.py..."
	@export PYTHONPATH=$$PYTHONPATH:$(PWD)/backend; \
	$(PYTHON) api/api.py

main: venv
	@echo "Running main.py..."
	@export PYTHONPATH=$$PYTHONPATH:$(PWD)/backend; \
	$(PYTHON) main.py

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_NAME) __pycache__


# - - - Firebase - - -
emulators: export FIREBASE_DATABASE_EMULATOR_HOST=localhost:9000
emulators: export STORAGE_EMULATOR_HOST=localhost:9199
emulators:
	@echo "Starting Firebase emulators..."
	echo $$FIREBASE_DATABASE_EMULATOR_HOST
	echo $$STORAGE_EMULATOR_HOST
	firebase emulators:start