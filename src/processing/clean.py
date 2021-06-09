from json.decoder import JSONDecodeError
import logging
import json
import re

import pandas as pd

logger = logging.getLogger(__name__)


def clean_ingr(items, patterns, verbose=False):
    """For a list of strings, remove segments that match regular expression
    patterns specified

    Args:
        items (array-like): List of strings
        patterns (`list`): List of regex patterns to match and remove
        verbose (bool, optional): When true, prints out warning logs
        for every removal. Defaults to False.

    Returns:
        `list`: List of strings with regex patterns removed
    """
    fixed_items = []

    # Check for every item in the list
    for item in items:
        # Check for every pattern
        for pattern in patterns:
            # if match found, replace with empty str
            if re.match(pattern, item):
                try:
                    fixed = re.sub(pattern, "", item)
                except TypeError:
                    logger.warning(
                        "String type expected in record,\
                        attempting converting to string"
                    )
                    fixed = re.sub(pattern, "", str(item))
                # Print warnings
                if verbose:
                    logger.warning("Exchanged %s to: %s", item, fixed)
                item = fixed

        fixed_items.append(item)

    return fixed_items


def regex_patterns(remove_words):
    """Format remove words such that regex engine matches portion of string
    up until and including the words.

    Args:
        REMOVE_WORDS (list): List of words to be removed

    Returns:
        list: List of formatted regular expression patterns
    """
    try:
        words = ["^.*" + word + " " for word in remove_words]
    except TypeError:
        logger.warning("Expected string")
        return None

    return words


def convert_json(data_path):
    """Convert json to a Python dictionary

    Args:
        data_path (str): Path to JSON file

    Returns:
        dict: Dictionary
    """
    try:
        with open(data_path, "r") as file:
            data = file.read()
            logger.info("Read file from %s", data_path)
    except JSONDecodeError:
        logger.error("Invalid file provided at %s", data_path)

    # Parse file
    obj = json.loads(data)
    logger.info("Obtained %i records", len(obj))

    return obj


def clean(
    data_path,
    patterns,
    remove_words,
    cuisine_attr="cuisine",
    ingredients_attr="ingredients",
    cuisine_col="cuisine",
    ingredient_col="ingredient",
):
    """Main cleaning function that takes a dictionary and formats all
    strings (ingredients) to be formatted so that all patterns listed
    are removed, as well as portions of string up until and including
    any words specified.

    Args:
        data_path (str)): Path to JSON file (raw)
        patterns (array-like): List of regular expression patterns to
        remove from ingredient names
        remove_words (array-like): Any words to be removed (up until and
        including the word) from ingredient names
        cuisine_attr (str, optional): Name of cuisine attribute in JSON.
        Defaults to "cuisine".
        ingredients_attr (str, optional): Name of ingredients attribute in
        JSON. Defaults to "ingredients".
        cuisine_col (str, optional): Name of cuisine column on the output
        dataframe. Defaults to "cuisine".
        ingredient_col (str, optional): Name of ingredient column on the
        output dataframe. Defaults to "ingredient".

    Returns:
        `pandas.DataFrame`: Recipe ingredients dataframe
    """

    # Add any additional patterns to remove from ingr name
    with regex_patterns(remove_words) as rp:
        # function might return None values
        if rp:
            patterns = patterns + rp
        else:
            logger.warning("One or more words have wrong type")

    # Get JSON as dictionary
    data = convert_json(data_path)

    recipe_ings = []

    logger.info("Reformatting %i records", len(data))
    try:
        for recipe in data:
            cuisine = recipe[cuisine_attr]
            ingredients = recipe[ingredients_attr]

            recipe_ings = recipe_ings + [
                (x, cuisine) for x in clean_ingr(ingredients, patterns)
            ]
    except KeyError:
        logger.error(
            "Attributes %s or %s not found in input file at %s",
            cuisine_attr,
            ingredients_attr,
            data_path,
        )
    # Convert to dataframe
    df = pd.DataFrame(data=recipe_ings, columns=[ingredient_col, cuisine_col])
    return df
