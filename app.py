import json
import logging.config
import traceback

from flask import Flask
from flask import render_template, request, jsonify
from src.data_model import Ingredient, SessionManager, delete_db, create_db
from src.recsys.model import RecipeModel


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
logger.debug("Web app log")

# Initialize the database session


manager = SessionManager(app)

delete_db(manager.db.engine)
create_db(manager.db.engine)

manager.add_to_db("data/full.csv")

manager.bind_model(
    RecipeModel(NUM_GUESSES=3, NUM_INGREDIENTS=5),
    SCALE_CONST=1000,
    SUM_COLUMN="ingr_sum",
)


@app.route("/")
def index():
    """Main view that lists songs in the database.
    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.
    Returns: rendered html template
    """

    try:

        logger.debug("Index page accessed")

        return render_template("index.html")
    except:
        traceback.print_exc()
        logger.warning("Not able to display tracks, error page returned")
        return render_template("error.html")


@app.route("/dropdown", methods=["GET"])
def dropdown_options():
    ingredients = manager.session.query(Ingredient).all()

    menuitems = [
        {"label": item.name, "value": item.cuisineid} for item in ingredients
    ]

    logger.debug(ingredients)

    return jsonify(menuitems)


# @app.route("/layout")
# def layout_params():
#     return jsonify(cols=NUM_)


@app.route("/predict", methods=["POST"])
def prediction():
    """View that process a POST with new song input
    :return: redirect to index page
    """

    # try:

    # track_manager.add_track(
    #     artist=request.form["artist"],
    #     album=request.form["album"],
    #     title=request.form["title"],
    # )
    # logger.info(
    #     "New song added: %s by %s",
    #     request.form["title"],
    #     request.form["artist"],
    # )
    logger.info(request.form["data"])
    selection = list(map(int, json.loads(request.form["data"])))
    # print(selection)
    # print(selection.split(","))

    # selection = selection.split(",")
    # logger.info(selection)

    ingr_list = (
        manager.session.query(Ingredient)
        .with_entities(Ingredient.name)
        .filter(Ingredient.cuisineid.in_(selection))
        .all()
    )
    logger.info(ingr_list)

    ingr_list = [x[0] for x in ingr_list]

    results = manager.model.predict_and_recommend(ingr_list, request=True)
    logger.info(results)

    logger.info("this is it")
    # logger.info(request.form["ingno"])
    logger.info("that was it")

    return jsonify(results)

    # except:

    #     logger.warning("Not able to display tracks, error page returned")
    #     return render_template("error.html")


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        port=app.config["PORT"],
        host=app.config["HOST"],
    )
