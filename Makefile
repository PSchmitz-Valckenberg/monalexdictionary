PYTHON ?= python3
PORT ?= 5000

.PHONY: install run test check clean

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	flask --app app run --port $(PORT)

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover

check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile app.py tests/test_app.py
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
