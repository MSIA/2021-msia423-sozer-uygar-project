imagename = cuisinehelpr_pipeline
app_imagename = cuisinehelpr_app
upload_imagename = cuisinehelpr_upload
#rds_route = "mysql+pymysql://msia423instructor:usz2807@msia423db.cxnolz9olxpr.us-east-1.rds.amazonaws.com:3306/msia423db"

image_app:
	docker build -t $(app_imagename) -f app/Dockerfile_app .

image_pipeline:
	docker build -t $(imagename) -f Dockerfile .

image_upload:
	docker build -t $(upload_imagename) -f Dockerfile_upload .

upload_data: data/raw.json
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY $(upload_imagename) run.py upload 2021-msia423-sozer-uygar raw.json data/raw.json

create:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI $(upload_imagename) run.py create

data/raw.json:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY $(imagename) run.py download --s3path="s3://2021-msia423-sozer-uygar/raw.json" --path_to="data/raw.json"

raw: data/raw.json

data/clean.csv: data/raw.json config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ $(imagename) run.py pipeline clean --input=data/raw.json --config=config/config.yaml --output=data/clean.csv

cleaned: data/clean.csv

data/full.csv: data/clean.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ $(imagename) run.py pipeline features --input=data/clean.csv --config=config/config.yaml --output=data/full.csv

features: data/full.csv

model: data/raw.json config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ $(imagename) run.py pipeline model --input=data/raw.json --config=config/config.yaml --output=data/

data/kitchen.db: data/full.csv config/config.yaml
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ $(imagename) run.py create 

localdb: data/kitchen.db

test:
	docker run --mount type=bind,source="$(shell pwd)",target=/app/ $(imagename) -m pytest

all: data/raw.json data/clean.csv data/full.csv model

app:
	docker run -p 5000:5000 -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI $(app_imagename)

.PHONY: image_pipeline image_app image_upload raw cleaned features reset test model localdb all upload_data create app