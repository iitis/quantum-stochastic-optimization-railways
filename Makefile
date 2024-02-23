init:
	@pip3 install -r requirements.txt
test:
	@rm -rf tests/__pycache__/
	@PYTHONPATH=. pytest -q --durations=10 --cov=. --cov-report term --cov-fail-under 60 tests/
lint:
	@pylint --fail-under=8.0 *.py

clean:
	@rm -rf *.jpg

.PHONY: init test clean
