default:
	python3 main.py

ve:
	python3 -m venv ve

install:
	pip install -r requirements.txt

prime:
	python3 create_tables.py