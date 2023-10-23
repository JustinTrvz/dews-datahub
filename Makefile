VENV_NAME := venv
PYTHON := backend/$(VENV_NAME)/bin/python
PIP := backend/$(VENV_NAME)/bin/pip

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
	cd backend && python3 -m venv $(VENV_NAME)

requirements: venv
	@echo "Installing requirements..."
	$(PIP) install -r backend/requirements.txt

setup: venv requirements
	@echo "Created virtual environment and installed requirements..."


api: venv
	@echo "Activating virtual environment and running api.py..."
	@export PYTHONPATH=$$PYTHONPATH:$(PWD)/backend; \
	$(PYTHON) backend/api/api.py

# main: export FIRESTORE_EMULATOR_HOST=localhost:8080
# main: export FIREBASE_DATABASE_EMULATOR_HOST=localhost:9000
# main: export FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199
# main: export STORAGE_EMULATOR_HOST=localhost:9199
main: venv
	@echo "Running main.py..."
	@export PYTHONPATH=$$PYTHONPATH:$(PWD)/backend; \
	$(PYTHON) backend/main.py

clean:
	@echo "Cleaning up..."
	cd backend && rm -rf $(VENV_NAME) __pycache__


# - - - Firebase - - -
emulators: export FIRESTORE_EMULATOR_HOST=localhost:8080
emulators: export FIREBASE_DATABASE_EMULATOR_HOST=localhost:9000
emulators: export FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199
emulators: export STORAGE_EMULATOR_HOST=localhost:9199
emulators:
	@echo "Starting Firebase emulators..."
	echo $$FIREBASE_DATABASE_EMULATOR_HOST
	echo $$STORAGE_EMULATOR_HOST
	cd backend && firebase emulators:start

# - - - Frontend - - -
# Set the location of your Flutter SDK.
FLUTTER_SDK_PATH := ~/snap/flutter/common/flutter
# Define Flutter commands.
FLUTTER := $(FLUTTER_SDK_PATH)/bin/flutter

build-linux:
	@echo "Building Flutter project..."
	cd frontend && $(FLUTTER) build linux

build-web:
	@echo "Building Flutter project..."
	cd frontend && $(FLUTTER) build web

flutter:
	@echo "Running Flutter project..."
	cd frontend && $(FLUTTER) run -d chrome --web-browser-flag "--disable-web-security"
