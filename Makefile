.PHONY: install run destroy run-docker

install:
	bash install.sh

run:
	bash run.sh

run-docker:
	docker-compose up --build

bootstrap:
	bash bootstrap.sh

destroy:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm .env

