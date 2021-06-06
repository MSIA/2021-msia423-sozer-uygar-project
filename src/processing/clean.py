import logging
import json
import re

import pandas as pd

logger = logging.getLogger(__name__)


def clean_ingr(items, patterns, verbose=False):
    fixed_items = []
    for item in items:
        for pattern in patterns:
            if re.match(pattern, item):
                fixed = re.sub(pattern, "", item)
                if verbose:
                    logger.debug("Exchanged %s to: %s", item, fixed)
                item = fixed
        fixed_items.append(item)

    return fixed_items


def regex_patterns(PATTERNS, REMOVE_WORDS):
    words = ["^.*" + word + " " for word in REMOVE_WORDS]

    PATTERNS += words
    return PATTERNS


def clean(DATA_PATH, PATTERNS, REMOVE_WORDS):
    with open(DATA_PATH, "r") as file:
        data = file.read()
        logger.info("Read file from %s", DATA_PATH)

    # parse file
    obj = json.loads(data)
    logger.info("Obtained %i records", len(obj))

    recipe_ings = []

    patterns = regex_patterns(PATTERNS, REMOVE_WORDS)

    for recipe in obj:
        cuisine = recipe["cuisine"]
        ingredients = recipe["ingredients"]

        recipe_ings += [(x, cuisine) for x in clean_ingr(ingredients, patterns)]

    df = pd.DataFrame(data=recipe_ings, columns=["ingredient", "cuisine"])
    return df
