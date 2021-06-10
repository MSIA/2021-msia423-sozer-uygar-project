# MSiA 423 Project - CuisineHelpr

Author: Uygar Sozer

QA Partner: Isaac Choi

## Vision

Home chefs at all levels, from beginner to pro, know that it is difficult to get inspiration to break out of the comfort zone of a few basic dishes and cuisines. Discovering new cuisines could
be surprisingly challenging if you can't dedicate time to go recipe surfing, especially when you
come home tired and hungry!

In reality, even if you never cooked Thai or Indian food yourself, a lot of world cuisines start
with mostly the same ingredients. You would only need to pick up a few other ingredients on
your next grocery store visit to make a delicious Indian curry. Maybe beginner cooks wouldn't be
so intimidated to explore more if there was a robust source they could pick up inspiration from.
CuisineHelper aims to solve some of these issues by simplifying the planning process of cooking,
as well as making recommendations for new styles of cooking we think the user is interested in.

## Mission

The app will ask the user to enter a few ingredients on a search bar. After 3 ingredients, the
app will display a few different cuisines underneath that would make use of those ingredients,
and tries to complete a basic *shopping list* for you for each of those cuisines. The user can
continue adding more ingredients on their search bar, which might start going in another direction,
and the app will adjust the predictions and the shopping lists accordingly.

In developing this app, I will create a predictive model that assigns a cuisine label to a list
of ingredients. As the user inputs the ingredients they are interested in, the model will 
generate predictions. I will remove
basic ingredients such as salt, cooking oil, flour etc. that show up in practically any cuisine
to improve precision. Then, for the grocery lists, the app will use a separate model to compute
item associations for each cuisine and display the most highly associated items to the input list
underneath each of the 3 cuisines predicted.

Data sources:
* [Yummly dataset](https://www.kaggle.com/kaggle/recipe-ingredients-dataset) - 
contains 40,000 ingredient lists, each labeled with 1 of 20 different cuisines
* [Dataset by Dominik Schmidt](https://dominikschmidt.xyz/simplified-recipes-1M/) -
over 1M unlabeled recipes for market basket analysis

## Success criteria

**Model performance**:
* Prior to deployment, the predictive model should have a **cross-validation accuracy** (predicting the
right cuisine within the top 3 most likely cuisines) **of more than 70%**.

**Business metrics**:

* Monthly unique user count, and user retention
(the user returned to the app within 2 weeks)
* Positive explicit feedback randomly solicited from the user 
(the user clicked upvote on one or more of the predictions)
* In the future, when we add recipe links to cuisines, promising clickstream data (the user followed
the link to the recipe provided)

---

# Repository

* [MSiA 423 Project - CuisineHelpr](#msia-423-project---cuisinehelpr)
   * [Vision](#vision)
   * [Mission](#mission)
   * [Success criteria](#success-criteria)
* [Repository](#repository)
   * [Directory structure](#directory-structure)
* [Running the app](#running-the-app)
   * [Initialize Docker](#initialize-docker)
   * [Obtain raw data](#obtain-raw-data)
   * [Upload raw data on AWS S3](#upload-raw-data-on-aws-s3)
   * [Model pipeline](#model-pipeline)
   * [Create the database](#create-the-database)
   * [Web app](#web-app)

## Directory structure 

```
├── app                             <- Files for the web application
│   ├── static                      <- CSS, Javascript, images
│   ├── templates                   <- HTML templates operated on by Flask
│   ├── Dockerfile_app              <- Docker container creation for web app
│   └── boot.sh                     <- Shell script on Docker boot up 
│
├── config                          
│   ├── logging                     <- Logger configuration
│   ├── config.yaml                 <- Reproducible model documentation
│   └── flaskconfig.py              <- Configurations for database management
│
├── copilot                         <- AWS ECS deployment configurations
├── deliverables                    <- Final presentation & demo
├── notebooks                       <- Jupyter notebooks used during development (archived - see develop branch)
├── src
│   ├── processing                  <- Module for data processing
│   │   ├── __init__.py                   
│   │   ├── clean.py                <- Data cleaning
│   │   └── features.py             <- Feature/training dataframe generation
│   │
│   ├── recsys                      <- Module for predictive model & recommender system
│   │   ├── __init__.py             
│   │   ├── evaluate.py             <- Model evaluation
│   │   └── model.py                <- Defines machine learning model class
│   │
│   ├── data_model.py               <- Defines data model for the relational DB used
│   └── dataio.py                   <- Functions for data I/O through AWS S3
│
├── test                            <- Unit tests
│
├── Dockerfile                      <- Dockerfile for container to run ML model pipeline
├── Dockerfile_upload               <- Dockerfile for container to interact with S3
├── Makefile                        <- Make directives
├── Makefile_app                    <- Make directives for web app container (DO NOT USE)
├── Pipfile                         <- pipenv dependencies
├── Pipfile.lock                    <- pipenv dependencies - absolute 
├── README.md                       <- You are here
├── app.py                          <- Wrapper for Flask app
├── requirements.txt                <- Required packages for project
└── run.py                          <- Orchestration script
```

# Running the app
## Initialize Docker

This project uses Docker containers to ensure OS compatibility. There are 3 separate Dockerfiles for:

* Data acquisition and upload
* Model pipeline
* Web application

At the root of the repository, run:

```bash
make image_upload
make image_pipeline
make image_app
```

for each of the Docker functionalities respectively.

Note: Windows users may need to add `winpty` before running Docker commands.


## Obtain raw data

The raw data used in this project is available on [Kaggle](https://www.kaggle.com/kaggle/recipe-ingredients-dataset) as a `JSON` file. In order to comply with Kaggle policies, I encourage you to log-in to Kaggle with your own credentials and place `train.json` in the `data/` folder.

I provided a copy of this file in this repository.

## Upload raw data on AWS S3

In order to interact with Amazon Web Services through the console, run the following two lines:

```bash
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
```

filling in with your pre-approved credentials. Then run:

```bash
make upload_data
```


For any changes in S3 bucket name, file key name on S3 or local filepath, see `Makefile`.

By default, the raw data lives in `data/train.json`.

## Model pipeline

To run the entirety of the model pipeline, run:

```bash
make model
```

By default, this will invoke the special Dockerfile for the model pipeline, mount the root of the repository to the Docker image and copy all files to the `data/` folder, including evaluation results.

For each individual step, you can run:

```bash
make cleaned
make features
```

Please note that `features` command has file dependencies on `cleaned`, which has dependencies on the raw data file downloaded from S3.


## Create the database 

To create the database in the location configured in `config/dbconfig.py`, run: 

```bash
make localdb
```

By default, this command creates a database locally at `sqlite:///data/kitchen.db`.

Alternatively, you might want to specify a MySQL server to create the database on. For this, please set MySQL URI as an environment variable:

```bash
export SQLALCHEMY_DATABASE_URI="{dialect}://{username}:{password}@{hostname}/{database_name}"
```

and run:

```bash
make create
```

## Web app

Web app will run on Docker image created by the `make image_app`. Once that image is created, simply run:

```bash
make app
```

which will automatically boot up app image with all data cleaning and featurizing artifacts, fill in any missing files and start web server at port `5000`.

You can access the website at:
```bash
http://localhost:5000
```

To kill the web app, open up another terminal instance and run:
```bash
docker stop webapp
```

Note: If you would like to make sure app image starts by downloading the raw data from S3, please delete all files in the `data/` folder before re-making the image with the command:
```bash
make image_app
```