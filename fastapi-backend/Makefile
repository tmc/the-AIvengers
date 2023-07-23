# Hackathon Templates Fastapi Backend Makefile

# Variables
APP_NAME=myapp
IMG_NAME=mycontainer

generate:

# Commands
install:
	# Python dependencies
	pip install -r requirements.txt

.PHONY: ngrok-tunnel
ngrok-tunnel:
	command -v ngrok >/dev/null 2>&1 || (brew install ngrok)
	ngrok http 8000

clean:
	# Delete Python artifacts
	find . -name '*.pyc' -exec rm '{}' ';'
	find . -name '*.pyo' -exec rm '{}' ';'
	find . -name '*~' -exec rm '{}' ';'
	find . -name '__pycache__' -exec rm -r '{}' ';'
	rm -f .coverage
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf .mypy_cache

run: .venv
	# Run the app
	.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

.venv: requirements.txt
	# Create virtual environment
	python3 -m venv .venv
	.venv/bin/pip install wheel
	.venv/bin/pip install -r requirements.txt

docker-build:
	# Build the Docker image
	docker build -t $(IMG_NAME) .

docker-run:
	# Run the Docker container
	docker run --name $(APP_NAME) -p 8000:8000 $(IMG_NAME)

docker-stop:
	# Stop the Docker container
	docker stop $(APP_NAME)
	docker rm $(APP_NAME)
