import json
import logging.config
import traceback

from flask import Flask
from flask import render_template, request, jsonify
from sqlalchemy.exc import OperationalError
from src.data_model import Ingredient, SessionManager, delete_db, create_db
from src.recsys.model import RecipeModel
from sqlalchemy.sql import text as sa_text

# Initialize the Flask application
app = Flask(
    __name__, template_folder="app/templates", static_folder="app/static"
)

# Configure flask app from flask_config.py
app.config.from_pyfile("config/flaskconfig.py")

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug("Initializing web app log")

# Initialize the database session

manager = SessionManager(app)
logger.info("Connected to db %s", manager.db.engine)

# If app is configured to re-do, delete and re-create
# database schema
if app.config["REDO"]:
    delete_db(manager.db.engine)
    logger.info("Deleted db schema %s", manager.db.engine)
    create_db(manager.db.engine)
    logger.info("Created db schema %s", manager.db.engine)
    manager.session.execute(
        sa_text("""TRUNCATE TABLE ingredients""").execution_options(
            autocommit=True
        )
    )
    logger.info("Deleted table content at %s", manager.db.engine)
    manager.add_to_db("data/full.csv")
    logger.info("Repopulated table at %s", manager.db.engine)

# Create new model object for the current session,
# will be trained on what is on the db
manager.bind_model(
    RecipeModel(num_guesses=3, num_ingredients=5),
    scale_const=1000,
    sum_column="ingr_sum",
)


@app.route("/")
def index():
    """Main page that returns a dropdown menu with options
    preloaded, when an option is selected from the menu, website
    dynamically changes via JQuery

    Returns:
        HTML document: index page
    """

    try:
        logger.debug("Index page accessed")
        return render_template("index.html")
    except Exception as e:
        traceback.print_exc()
        logger.warning("Not able to load index page, error page returned")
        logger.warning("Exception occurred: %s", e)
        return render_template("error.html")


@app.route("/dropdown", methods=["GET"])
def dropdown_options():
    """Get list of dropdown options from the connected database

    Returns:
        JSON formatted dictionary as key (cuisineid): value (name string)
    """
    ingredients = manager.session.query(Ingredient).all()
    logger.info(
        "Loaded %i records to populate dropdown menu", len(ingredients)
    )

    menuitems = [
        {"label": item.name, "value": item.cuisineid} for item in ingredients
    ]

    return jsonify(menuitems)


@app.route("/predict", methods=["POST"])
def prediction():
    """Process a post request sending in lists of ingredients as an array
    of cuisineid's (integer)

    Returns:
        JSON formatted dictionary as key (HTML element id): value (string)
    """
    try:
        logger.info(
            "POST request received at server, %s", request.form["data"]
        )

        # Map integer cuisineids to the ingredients' name (String)
        selection = list(map(int, json.loads(request.form["data"])))
        logger.info("Current selection: %s", selection)

        # Subset list by names
        ingr_list = (
            manager.session.query(Ingredient)
            .with_entities(Ingredient.name)
            .filter(Ingredient.cuisineid.in_(selection))
            .all()
        )
        logger.info(
            "Successfully processed request, attempting to return results"
        )

        # Returns tuples with second value empty
        # Only keep the first value
        ingr_list = [x[0] for x in ingr_list]

        results = manager.model.predict_and_recommend(ingr_list, request=True)
        logger.info("Predict + recommend complete: %s", results)

        return jsonify(results)

    except TypeError:
        logger.warning(
            "Supplied forbidden input, do not interact with private app API"
        )
    except Exception as e:
        logger.warning("Unusual exception %s", e)
        return -1


@app.route("/convert", methods=["POST"])
def conversion():
    """Process incoming post requests with ingredient name, return
    the cuisineid

    For a future implementation on the app

    Returns:
        int: Cuisine ID of the ingredient
    """

    logger.info("The client returned %s", "".join(request.form))

    item = "".join(request.form)

    try:
        response = (
            manager.session.query(Ingredient)
            .with_entities(Ingredient.cuisineid)
            .filter(Ingredient.name == item)
            .all()
        )
        logger.info("Response created: %s", response[0][0])

        return str(response[0][0])
    except OperationalError:
        logger.warning("Connection to db timed out, please check connection")
    except TypeError:
        logger.warning("Bad request, input could not be parsed")
    except Exception as e:
        logger.warning("Unusual exception %s", e)


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        port=app.config["PORT"],
        host=app.config["HOST"],
    )
