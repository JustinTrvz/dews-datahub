VENV_NAME := venv
PYTHON := backend/$(VENV_NAME)/bin/python
PIP := backend/$(VENV_NAME)/bin/pip

.PHONY: all venv requirements flask firebase-emulators firebase

# TODO: finish help text
help:
	@echo "Available targets:"
	@echo "  all        		: Executes all commands from the list."
	@echo "  TODO..." 

all: venv requirements run

venv:
	@echo "Creating virtual environment..."
	python3 -m venv backend/$(VENV_NAME)

requirements: venv
	@echo "Installing requirements..."
	$(PIP) install -r requirements.txt

api: venv
	@echo "Activating virtual environment and running api.py..."
	$(PYTHON) backend/api/api.py

main: venv
	@echo "Running main.py"
	$(PYTHON) backend/main.py

firebase-emulators:
	@echo "Starting Firebase emulators..."
	cd backend && firebase emulators:start

clean:
	@echo "Cleaning up..."
	rm -rf backend/$(VENV_NAME) __pycache__

# If you want to force the recreation of the virtual environment and reinstall requirements, you can use 'make clean' followed by 'make all'.