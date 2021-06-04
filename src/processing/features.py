import logging

logger = logging.getLogger(__name__)


def ingr_sum(df):
    return df.iloc[:, 1:].sum(axis=1, skipna=True)


def generate_train_df(df, DROP_ROWS=None, MIN_PREVALENCE=100):
    cuisine_series = df.groupby("ingredient").cuisine.value_counts()

    cuisinedf = cuisine_series.unstack().fillna(0)
    if DROP_ROWS:
        cuisinedf = cuisinedf.drop(DROP_ROWS, axis=0)

    cuisinedf["ingr_sum"] = ingr_sum(cuisinedf)

    cuisinedf[cuisinedf.ingr_sum >= MIN_PREVALENCE]

    return cuisinedf
