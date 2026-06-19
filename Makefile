# Makefile for QA Automation Framework (Python + Selenium)
# Designed for recruiters and final-year portfolio reference

.PHONY: install test test-headless report docker clean format lint

install:
	pip install -r requirements.txt

test:
	pytest -v --html=reports/report.html --self-contained-html

test-headless:
	pytest -v --headless --html=reports/report.html --self-contained-html

format:
	black pages/ tests/ utils/
	isort pages/ tests/ utils/

lint:
	flake8 pages/ tests/ utils/

docker:
	docker-compose up --build

clean:
	@echo "Cleaning cache, logs, screenshots, and reports..."
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@rm -rf pages/__pycache__
	@rm -rf tests/__pycache__
	@rm -rf utils/__pycache__
	@rm -rf logs/*.log
	@rm -rf screenshots/*.png
	@rm -rf reports/*.html
	@rm -rf reports/execution_summary.md
