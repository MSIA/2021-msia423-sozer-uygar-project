import logging

import numpy as np

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
    def __init__(self, num_guesses=3, num_ingredients=5):
        self.rec_train = None
        self.pred_train = None

        self.num_guesses = num_guesses
        self.num_ingredients = num_ingredients

        self.sum_column = None

    def train(self, df, scale_const, sum_column):
        self.sum_column = sum_column

        self.pred_train = df.apply(
            normalize, exclude=[sum_column], scale=scale_const, axis=0
        ).apply(mean_center, raw=True, axis=1)

        self.rec_train = df.drop(sum_column, axis=1).apply(
            mean_center, raw=True, axis=0
        )

    def predict(self, ingredients):

        df = self.pred_train

        try:
            calc = df.loc[ingredients]
        except KeyError:
            logger.error("One or more of the keys not found: %s", ingredients)
            return

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
