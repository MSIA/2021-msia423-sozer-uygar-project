import pytest
import pandas as pd

from src.processing.features import ingr_sum, generate_train_df


def test_ingr_sum():
    test_data = [
        [
            0.0,
            0.0,
            0.0,
            2.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            2.0,
            136.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
        ],
        [
            0.0,
            0.0,
            9.0,
            0.0,
            0.0,
            6.0,
            1.0,
            0.0,
            1.0,
            89.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            7.0,
            3.0,
            0.0,
            0.0,
        ],
    ]

    test_columns = [
        "brazilian",
        "british",
        "cajun_creole",
        "chinese",
        "filipino",
        "french",
        "greek",
        "indian",
        "irish",
        "italian",
        "jamaican",
        "japanese",
        "korean",
        "mexican",
        "moroccan",
        "russian",
        "southern_us",
        "spanish",
        "thai",
        "vietnamese",
    ]

    test_index = ["Gochujang base", "Italian bread"]

    test = ingr_sum(
        pd.DataFrame(data=test_data, columns=test_columns, index=test_index)
    )

    true = pd.Series(
        data=[142.0, 118.0], index=["Gochujang base", "Italian bread"]
    )

    pd.testing.assert_series_equal(test, true)


def test_ingr_sum_string_input():
    test_data = [
        [
            "a",
            0.0,
            0.0,
            2.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            2.0,
            "n",
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
        ],
        [
            0.0,
            0.0,
            9.0,
            0.0,
            0.0,
            6.0,
            1.0,
            0.0,
            1.0,
            89.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
            7.0,
            3.0,
            0.0,
            0.0,
        ],
    ]

    test_columns = [
        "brazilian",
        "british",
        "cajun_creole",
        "chinese",
        "filipino",
        "french",
        "greek",
        "indian",
        "irish",
        "italian",
        "jamaican",
        "japanese",
        "korean",
        "mexican",
        "moroccan",
        "russian",
        "southern_us",
        "spanish",
        "thai",
        "vietnamese",
    ]

    test_index = ["Gochujang base", "Italian bread"]

    test = ingr_sum(
        pd.DataFrame(data=test_data, columns=test_columns, index=test_index)
    )

    true = pd.Series(
        data=[6, 118.0], index=["Gochujang base", "Italian bread"]
    )

    pd.testing.assert_series_equal(test, true)


def test_ingr_sum_invalid_type():
    with pytest.raises(AttributeError):
        ingr_sum([])


def test_generate_train_df():

    test_values = [
        ["red pepper", "mexican"],
        ["chopped cilantro fresh", "mexican"],
        ["olive oil", "southern_us"],
        ["white vinegar", "vietnamese"],
        ["green onions", "japanese"],
        ["dried basil", "mexican"],
        ["bell pepper", "chinese"],
        ["currant", "british"],
        ["milk", "brazilian"],
        ["flour tortillas", "mexican"],
        ["garlic cloves", "chinese"],
        ["sunflower oil", "indian"],
        ["Thai red curry paste", "thai"],
        ["honey", "japanese"],
        ["green chilies", "indian"],
        ["chicken bouillon granules", "southern_us"],
        ["eggplant", "moroccan"],
        ["lime wedges", "mexican"],
        ["green olives", "italian"],
        ["hass avocado", "mexican"],
    ]

    test_index = [
        141355,
        314658,
        145595,
        11253,
        394902,
        163446,
        220475,
        184119,
        287494,
        268146,
        30076,
        3157,
        408120,
        345068,
        104764,
        31209,
        262305,
        153529,
        75657,
        58540,
    ]
    test_columns = ["ingredient", "cuisine"]

    test_input = pd.DataFrame(
        data=test_values, columns=test_columns, index=test_index
    )

    test = generate_train_df(
        test_input, min_prevalence=0, sum_column="ingr_sum"
    )

    true_values = [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
    ]

    true_columns_list = [
        "brazilian",
        "british",
        "chinese",
        "indian",
        "italian",
        "japanese",
        "mexican",
        "moroccan",
        "southern_us",
        "thai",
        "vietnamese",
        "ingr_sum",
    ]

    true_columns = pd.Index(true_columns_list, name="cuisine")

    true_index_list = [
        "Thai red curry paste",
        "bell pepper",
        "chicken bouillon granules",
        "chopped cilantro fresh",
        "currant",
        "dried basil",
        "eggplant",
        "flour tortillas",
        "garlic cloves",
        "green chilies",
        "green olives",
        "green onions",
        "hass avocado",
        "honey",
        "lime wedges",
        "milk",
        "olive oil",
        "red pepper",
        "sunflower oil",
        "white vinegar",
    ]

    true_index = pd.Index(true_index_list, name="ingredient")

    true = pd.DataFrame(
        data=true_values, columns=true_columns, index=true_index
    )

    pd.testing.assert_frame_equal(test, true)


def test_generate_train_df_empty():
    with pytest.raises(KeyError):
        generate_train_df(pd.DataFrame([]))
