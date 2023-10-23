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

run:
	@echo "Running Flutter project..."
	cd frontend && $(FLUTTER) run