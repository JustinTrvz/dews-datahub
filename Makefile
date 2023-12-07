VENV_NAME := django-venv
PYTHON := dews/$(VENV_NAME)/bin/python
PIP := dews/$(VENV_NAME)/bin/pip

.PHONY: all venv requirements api main clean

# Help text
help:
	@echo "Available targets:"
	@echo "  venv - Create a virtual environment"
	@echo "  requirements - Install project requirements"
	@echo "  api - Run the api.py script"
	@echo "  main - Run the main.py script"
	@echo "  clean - Clean up virtual environment and cached files"

# Django
venv:
	@echo "Creating virtual environment..."
	cd dews && python3 -m venv $(VENV_NAME)

requirements: venv
	@echo "Installing requirements..."
	$(PIP) install -r dews/requirements.txt

setup: venv requirements
	@echo "Created virtual environment and installed requirements..."

run: venv
	$(PYTHON) dews/manage.py runserver


# Docker

docker-build:
	sudo docker-compose up --build --force-recreate

docker-up:
	sudo docker-compose up

docker-upd:
	sudo docker-compose up -d

docker-down:
	sudo docker-compose down

docker-rm-container:
	sudo docker rm -vf $(docker ps -aq)
	@echo "Removed all Docker container."

docker-rm-images:
	sudo docker rmi -f $(docker images -aq)
	@echo "Removed all Docker images."

docker-rm-all: docker-rm-container docker-rm-images
	@echo "Removed all Docker container and images."


init-db:
	sudo docker-compose exec dews flask init-db

drop-db:
	sudo docker-compose exec dews flask drop-db


# api: venv
# 	@echo "Activating virtual environment and running api.py..."
# 	@export PYTHONPATH=$$PYTHONPATH:$(PWD)/backend; \
# 	$(PYTHON) backend/api/api.py


# clean:
# 	@echo "Cleaning up..."
# 	cd backend && rm -rf $(VENV_NAME) __pycache__


