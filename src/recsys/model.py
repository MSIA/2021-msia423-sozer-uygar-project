import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def mean_center(row):
    avg = row[:-1].mean()
    row[:-1] = row[:-1] - avg

    return row


def normalize(col, scale=1, exclude=None):
    if col.name in exclude:
        return col

    avg = col.mean()
    total = col.sum()

    col = scale * (col - avg) / total
    return col


def softmax(raw):
    return np.e ** raw / np.sum(np.e ** raw)


class RecipeModel:
    def __init__(self, NUM_GUESSES=3, NUM_INGREDIENTS=5):
        self.rec_train = None
        self.pred_train = None

        self.num_guesses = NUM_GUESSES
        self.num_ingredients = NUM_INGREDIENTS

        self.sum_column = None

    def train(self, df, SCALE_CONST, SUM_COLUMN):
        self.sum_column = SUM_COLUMN

        self.pred_train = df.apply(
            normalize, exclude=[self.sum_column], scale=SCALE_CONST, axis=0
        ).apply(mean_center, raw=True, axis=1)

        self.rec_train = df.drop(self.sum_column, axis=1).apply(
            mean_center, raw=True, axis=0
        )

    def predict(self, ingredients):

        df = self.pred_train

        try:
            calc = df.loc[ingredients]
        except KeyError:
            new_ingr = df.index.intersection(ingredients)
            logger.warning(
                "One or more of the keys not found: %s",
                list(pd.Index(ingredients).difference(df.index)),
            )
            calc = df.loc[new_ingr]

        calc = calc.drop(self.sum_column, axis=1).sum(axis=0)

        ordered = softmax(calc).sort_values(ascending=False)

        return ordered[: self.num_guesses]

    def recommend(self, cuisine, selected=None):

        df = self.rec_train

        if selected:
            df = df.drop(labels=selected, axis=0)

        ordered = df.loc[:, cuisine].sort_values(ascending=False)

        return list((ordered[: self.num_ingredients]).index)

    def predict_and_recommend(self, ingredients):

        pred_cuisines = self.predict(ingredients)
        pred_list = list(pred_cuisines.index)

        rec_list = []
        for cuisine in pred_list:
            recommended = self.recommend(
                cuisine,
                selected=ingredients,
            )
            rec_list.append(recommended)

        return dict(zip(pred_list, rec_list))
