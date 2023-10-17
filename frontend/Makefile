# Flutter Makefile

# Set the location of your Flutter SDK.
FLUTTER_SDK_PATH := ~/snap/flutter/common/flutter
# Define Flutter commands.
FLUTTER := $(FLUTTER_SDK_PATH)/bin/flutter
# Define default target.
.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  init        : Initialize the Flutter project."
	@echo "  build       : Build the Flutter project."
	@echo "  run         : Run the Flutter project."
	@echo "  clean       : Clean build artifacts."

init:
	@echo "Initializing Flutter project..."
	$(FLUTTER) create .

build:
	@echo "Building Flutter project..."
	$(FLUTTER) build

run:
	@echo "Running Flutter project..."
	$(FLUTTER) run

clean:
	@echo "Cleaning Flutter project..."
	$(FLUTTER) clean

.PHONY: help init build run clean
