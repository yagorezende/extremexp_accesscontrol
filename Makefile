.PHONY: install run destroy

install:
	bash install.sh

run:
	bash run.sh

destroy:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm .env

