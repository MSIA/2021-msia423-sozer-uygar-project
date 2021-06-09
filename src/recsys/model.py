import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def mean_center(row):
    """Subtract mean from each element in a row

    Args:
        row (`pandas.Series`): row item representing
        1 unique ingredient

    Returns:
        `pandas.Series`: mean centered vector
    """
    try:
        avg = row[:-1].mean()
        row[:-1] = row[:-1] - avg
    except IndexError:
        logger.error("Supplied empty Series %s", row.name)
        return row

    return row


def normalize(col, scale=1, exclude=None):
    """Mean center and scale a column.

    Args:
        col (`pandas.Series`): df column
        scale (int, optional): Constant to multiply every cell.
        Helpful for model robustness if there are tons of rows.
        Defaults to 1.
        exclude (`list` of Strings, optional): Name of columns to
        avoid editing. Defaults to None.

    Returns:
        `pandas.Series`: Normalized column
    """
    # If name matches exclude list, return column as is
    if col.name in exclude:
        return col

    try:
        avg = col.mean()
        total = col.sum()
    except ValueError:
        logger.warning(
            "Invalid value detected in column %s, returning as is", col.name
        )
        return col
    except TypeError:
        logger.warning(
            "Invalid value detected in column %s, returning as is", col.name
        )
        return col

    col = scale * (col - avg) / total
    return col


def softmax(raw):
    """Get relative percentages of a probability vector of
    mutually exclusive classes

    Args:
        raw (`pandas.Series`): Vector of probabilities

    Returns:
        `pandas.Series`: raw probabilites transformed to
        add up to 1.0
    """
    try:
        softmax = np.e ** raw / np.sum(np.e ** raw)
    except TypeError:
        logger.error("Invalid vector type, contains non-numeric")

    return softmax


class RecipeModel:
    """Combined predictive and recommender model for detecting cuisine
    type from lists of ingredients, as well as recommendations for
    extending the lists with cuisine-specific items.

    Class methods:
    - train()
    - predict()
    - recommend()
    - predict_and_recommend()

    Training dataframes:
    - RecipeModel.rec_train (`pandas.DataFrame`)
    - RecipeModel.pred_train (`pandas.DataFrame`)
    """

    def __init__(self, num_guesses=3, num_ingredients=5):
        # Initialize train sets for predictions and recommendations
        self.rec_train = None
        self.pred_train = None

        # Response config
        self.num_guesses = num_guesses
        self.num_ingredients = num_ingredients

        self.sum_column = None

    def train(self, df, scale_const, sum_column):
        """Train RecipeModel. Computes and binds separate train sets for
        recommendations and predictions.

        Args:
            df (`pandas.DataFrame`): DataFrame containing ingredient data. Df
            must be keyed by String repr of the ingredient, and must contain a
            column for each cuisine.
            SCALE_CONST (`float`): Scale each cell by a constant if relative
            importance measures are too small
            SUM_COLUMN (String): Name of column representing sum of each row
        """
        self.sum_column = sum_column

        # Assign train set
        self.pred_train = df.apply(
            normalize, exclude=[self.sum_column], scale=scale_const, axis=0
        ).apply(mean_center, raw=True, axis=1)
        logger.info(
            "Trained for predictions, df length %i", len(self.pred_train)
        )

        self.rec_train = df.drop(self.sum_column, axis=1).apply(
            mean_center, raw=True, axis=0
        )
        logger.info(
            "Trained for recommendations, df length %i", len(self.rec_train)
        )

        logger.info("Training complete")

    def predict(self, ingredients, verbose=False):
        """Return predictions from the trained dataframe.
         Model makes no decisions influenced by
        ingredients that do not exist in the trained df.

        Args:
            ingredients (array-like): List of selected ingredients that
            the prediction is requested for.
            verbose (bool, optional): If True, prints out warning message
            indicating when ingredients are not found. Defaults to False.

        Returns:
            [type]: [description]
        """
        df = self.pred_train

        try:
            # Get relevant rows
            calc = df.loc[ingredients]
        except KeyError:
            # If one or more ingredients not found, subset the
            # ingredients to whatever is available in the train set
            new_ingr = df.index.intersection(ingredients)

            if verbose:
                logger.warning(
                    "One or more of the keys not found: %s",
                    list(pd.Index(ingredients).difference(df.index)),
                )
            calc = df.loc[new_ingr]

        calc = calc.drop(self.sum_column, axis=1).sum(axis=0)

        ordered = softmax(calc).sort_values(ascending=False)

        return ordered[: self.num_guesses]

    def recommend(self, cuisine, selected=None):
        """Get predictions from a list of ingredients as a list.
        Number of preds configured in init."""
        df = self.rec_train

        try:
            if selected:
                # attempt dropping selected rows
                df = df.drop(labels=selected, axis=0)
                logger.info(
                    "Dropped a total of %i rows named: %s",
                    len(self.rec_train) - len(df),
                    selected,
                )
        except KeyError:
            logger.error(
                "One or more of selected ingredients \
            %s not found in database.",
                selected,
            )

        # Reorder list to return top n rows
        ordered = df.loc[:, cuisine].sort_values(ascending=False)
        logger.debug("Returning %i recommendations", self.num_ingredients)

        return list((ordered[: self.num_ingredients]).index)

    def predict_and_recommend(self, ingredients, request=False, verbose=False):
        """Predict cuisines from a list of ingredients, and provide recommended
        items for each cuisine. Ingredients not found in the training set of
        the model instance is excluded from predictions.

        This is the public API for RecipeModel. Do not use other methods
        outside of class definition.

        Args:
            ingredients (`list`): Input ingredients as a list
            request (bool, optional): Print out predictions and recommendations
            in a REST API friendly mode. Defaults to False.
            verbose (bool, optional): If True, print out warning messages from
            pred and rec methods. Defaults to False.

        Returns:
            `dict`: Dictionary of values
        """
        logger.info(
            "Making %i predictions and %i recommendations",
            self.num_guesses,
            self.num_ingredients,
        )
        # Get preds
        pred_cuisines = self.predict(ingredients, verbose)
        pred_list = list(pred_cuisines.index)

        # Get recs
        rec_list = []
        for cuisine in pred_list:
            recommended = self.recommend(
                cuisine,
                selected=ingredients,
            )
            rec_list.append(recommended)

        if request:
            logger.debug("Returning Request type results")
            # Request mode displays each cuisine as cuisine1, cuisine2...
            # and each recommended ingredient as cuisine11, cuisine12,
            # option21 etc.
            recs = {}
            for i in range(len(pred_list)):
                recs["cuisine" + str(i + 1)] = pred_list[i]
                for j in range(len(rec_list[i])):
                    recs["option" + str(i + 1) + str(j + 1)] = rec_list[i][j]
            return recs
        else:
            # Non request mode displays
            # {"cuisine":[ingredients], "cuisine":[ingredients]...}
            logger.debug("Returning standard type results")
            return dict(zip(pred_list, rec_list))
