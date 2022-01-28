install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python3 -m pytest -vv tests

format:
	black *.py

lint:
	pylint --disable=R,C *.py
	

all: install lint test
