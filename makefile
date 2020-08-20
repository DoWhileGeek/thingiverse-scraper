default:
	python3 main.py
purge:
	rm -rf things && rm -rf data.db

prime:
	python3 create_tables.py