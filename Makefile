imagename = cuisinehelpr
datafolder = data/

image:
	docker build -t $(imagename) .

data/raw.json:
	python3 run.py download 2021-msia423-sozer-uygar raw.json data/raw.json

raw: data/raw.json

data/clean.csv: data/raw.json config/config.yaml
	python3 run.py pipeline clean --input=data/raw.json --config=config/config.yaml --output=data/clean.csv

cleaned: data/clean.csv

data/full.csv: data/clean.csv config/config.yaml
	python3 run.py pipeline features --input=data/clean.csv --config=config/config.yaml --output=data/full.csv

features: data/full.csv

reset:
	rm data/*

model: data/raw.json config/config.yaml
	python3 run.py pipeline model --input=data/raw.json --config=config/config.yaml --output=data/

data/kitchen.db: data/full.csv config/config.yaml
	python3 run.py create 

localdb: data/kitchen.db

test:
	python3 -m pytest

app: data/full.csv
	python3 app.py

all: data/raw.json data/clean.csv data/full.csv model

.PHONY: image raw cleaned features reset test model localdb all