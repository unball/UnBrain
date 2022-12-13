

help:
	@echo "beautifier: Runs black, flake8 and mypy"

beautifier: 
	black src -l 80 && flake8 src && mypy . --no-strict-optional
