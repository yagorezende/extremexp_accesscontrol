.PHONY: setup
setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt

.PHONY: install
install:
	bash install.sh

.PHONY: run
run:
	bash run.sh

.PHONY: run-docker
run-docker:
	docker-compose up --build

.PHONY: bootstrap
bootstrap:
	bash bootstrap.sh

.PHONY: generate-docs
generate-docs:
	@echo "Generating documentation..."
	@bash generate_docs.sh

.PHONY: update-swagger
update-swagger:
	@echo "Updating Swagger documentation..."
	@cp docs/swagger.json docs/swagger/swagger.json

.PHONY: destroy
destroy:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm .env

