import logging
import numpy as np

logger = logging.getLogger(__name__)


def ingr_sum(df):
    """Get the sum of all values in a row

    Input df should be cleaned by regular
    expression matching.
    Args:
        df (`pandas.DataFrame`): Cleaned dataframe

    Returns:
        `int`: Sum of all columns
    """
    try:
        # Skip ingredient name column
        return df.iloc[:, 1:].sum(axis=1, skipna=True)
    except TypeError:
        logger.error("One or more columns containing strings")
        return np.nan


def generate_train_df(df, drop_rows=None, min_prevalence=100, sum_column=None):
    """Reshapes cleaned dataframe to appropriate format for model training.

    The resulting dataframe has a row for each ingredient, a column
    representing each cuisine and a column at the end that sums all
    values in a row.

    Args:
        df (`pandas.DataFrame`): Cleaned dataframe. Each row represents a
        recipe ingredient. Two columns: ingredient name, cuisine label
        drop_rows (`list`, optional): Any particular ingredients to not
        include in training set. Defaults to None.
        min_prevalence (int, optional): If row sum of an ingredient
        falls under this threshold, remove row from training column.
        Defaults to 100.
        sum_column (str, optional): Name given to row sum column.
        Defaults to None.

    Returns:
        `pandas.DataFrame`: Return reshaped training dataframe
    """

    # Group by ingredient and count each cuisine
    cuisine_series = df.groupby("ingredient").cuisine.value_counts()

    # Pivot the dataframe, if cuisine doesn't include ingredient,
    # fill with 0
    cuisinedf = cuisine_series.unstack().fillna(0)

    # Drop ingredients listed in function from the training set
    if drop_rows:
        prev_length = len(cuisinedf)
        cuisinedf = cuisinedf.drop(drop_rows, axis=0)
        logger.info(
            "Dropped %i rows containing: %s",
            prev_length - len(cuisinedf),
            drop_rows,
        )

    # Set sum column
    try:
        cuisinedf[sum_column] = ingr_sum(cuisinedf)
    except KeyError:
        logger.error("Sum column not set")

    # Subset by a threshold total sum, drop ingredients
    # that fall below it
    cuisinedf = cuisinedf[cuisinedf.ingr_sum >= min_prevalence]

    return cuisinedf
