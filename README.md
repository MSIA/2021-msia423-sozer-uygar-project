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

<!-- toc -->

* [MSiA 423 Project - CuisineHelpr](#msia-423-project---cuisinehelpr)
   * [Vision](#vision)
   * [Mission](#mission)
   * [Success criteria](#success-criteria)
* [Repository](#repository)
   * [Directory structure](#directory-structure)
   * [Running the app](#running-the-app)
      * [1. Initialize Docker](#1-initialize-docker)
      * [2. Configure database](#2-configure-database)
         * [Obtain raw data](#obtain-raw-data)
         * [Upload raw data on AWS S3](#upload-raw-data-on-aws-s3)
         * [Create the database](#create-the-database)
<!-- tocstop -->

## Directory structure 

```
├── config                          <- Folder for configuration files
│   ├── logging                     <- Logging configurations
│   └── dbconfig.py                 <- Configurations for database management
├── data                            <- Data files for the project
│   ├── external
│   ├── sample
│   └── train.json                  <- Project dataset, obtained from Kaggle (see below)
├── docs
├── notebooks                       <- Jupyter notebooks
│   ├── archive                     <- Develop notebooks no longer being used
│   ├── deliver                     <- Notebooks shared with others / in final state
│   └── develop                     <- Current notebooks being used in development.
├── src                             <- Project source code
│   ├── __init__.py
│   ├── data_model.py               <- Defines data model for the relational DB used
│   └── upload_data.py              <- Lands raw data on AWS S3
├── README.md                       <- You are here
├── test                            <- Unit tests for source modules
├── Dockerfile
├── Pipfile                         <- pipenv dependencies
├── Pipfile.lock                    <- pipenv dependency resolution file
├── requirements.txt                <- Required packages for project
└── run.py                          <- Orchestration script
```


## Running the app
### 1. Initialize Docker

This project uses Docker containers to ensure OS compatibility. At the root of the repository, run:

```bash
docker build -t <IMAGE-NAME> .
```

replacing `<IMAGE-NAME>` with desired alias.


### 2. Configure database

#### Obtain raw data

The raw data used in this project is available on [Kaggle](https://www.kaggle.com/kaggle/recipe-ingredients-dataset) as a `JSON` file. In order to comply with Kaggle policies, I encourage you to log-in to Kaggle with your own credentials and place `train.json` in the `data/` folder.

I provided a copy of this file in this repository.

#### Upload raw data on AWS S3

In order to interact with Amazon Web Services through the console, run the following two lines:

```bash
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
```

filling in with your pre-approved credentials. Then run:

```bash
docker run \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    <IMAGE-NAME> upload <name-of-bucket> <filename>
```

filling in your S3 bucket name (without `S3://`) and the name you want your file to appear as on S3.

This command has an optional argument

```bash
    -d <data-path>
```

where you can configure another location for the raw data file. By default, it is `data/train.json`.

#### Create the database 

To create the database in the location configured in `config/dbconfig.py`, run: 

```bash
docker run <IMAGE-NAME> create
```

By default, this command creates a database locally at `sqlite:///data/kitchen.db`.

Alternatively, you might want to specify a MySQL server to create the database on. For this, set MySQL configurations as environment variables:

```bash
export MYSQL_HOST=<host-name>
export MYSQL_PORT=<port-no>
export MYSQL_USER=<db-user>
export MYSQL_PASSWORD=<db-password>
export MYSQL_DATABASE=<database-name>
```

and run:

```bash
docker run \
    -e MYSQL_HOST \
    -e MYSQL_PORT \
    -e MYSQL_USER \
    -e MYSQL_PASSWORD \
    -e MYSQL_DATABASE \
    <IMAGE-NAME> create
```

`create` command has an optional argument:

```bash
    -s <engine-string>
```

where you can enter your own formatted engine string. Otherwise, the program will try to format the engine string using the environment variables shown above.
