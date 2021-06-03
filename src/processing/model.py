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


def predict(df, ingredients, num_guesses=3, exclude=["ingr_sum"]):

    try:
        calc = df.loc[ingredients]
    except KeyError:
        print("key not found")
        return

    calc = calc.drop(exclude, axis=1).sum(axis=0)

    ordered = softmax(calc).sort_values(ascending=False)

    return ordered[:num_guesses]


def recommend(df, cuisine, num_ingredients=5, selected=None):

    if selected:
        df = df.drop(labels=selected, axis=0)

    ordered = df.loc[:, cuisine].sort_values(ascending=False)

    return list((ordered[:num_ingredients]).index)


def predict_and_recommend(
    df, ingredients, scale_const=1000, num_cuisines=3, num_ingredients=5
):

    predict_train = df.apply(
        normalize, exclude=["ingr_sum"], scale=scale_const, axis=0
    ).apply(mean_center, raw=True, axis=1)
    pred_cuisines = predict(
        predict_train, ingredients, num_guesses=num_cuisines
    )
    pred_list = list(pred_cuisines.index)

    rec_train = df.drop("ingr_sum", axis=1).apply(mean_center, raw=True, axis=0)
    rec_list = []
    for cuisine in pred_list:
        recommended = recommend(
            rec_train,
            cuisine,
            num_ingredients=num_ingredients,
            selected=ingredients,
        )
        rec_list.append(recommended)

    return dict(zip(pred_list, rec_list))
