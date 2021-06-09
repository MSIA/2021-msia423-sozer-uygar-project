import pandas as pd
import pytest

from src.recsys.model import mean_center, normalize, softmax


def test_mean_center():
    test_input_values = [
        0.0,
        0.0,
        0.0,
        247.0,
        4.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        5.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        2.0,
        6.0,
        264.0,
    ]

    test_input_index = pd.Index(
        [
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
            "ingr_sum",
        ],
        name="cuisine",
    )

    test_input = pd.Series(test_input_values, index=test_input_index)

    test = mean_center(test_input)

    true_values = [
        -13.2,
        -13.2,
        -13.2,
        233.8,
        -9.2,
        -13.2,
        -13.2,
        -13.2,
        -13.2,
        -13.2,
        -13.2,
        -8.2,
        -13.2,
        -13.2,
        -13.2,
        -13.2,
        -13.2,
        -13.2,
        -11.2,
        -7.2,
        264.0,
    ]

    true_index = pd.Index(
        data=[
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
            "ingr_sum",
        ],
        name="cuisine",
    )

    true = pd.Series(true_values, index=true_index)

    pd.testing.assert_series_equal(test, true)


def test_mean_center_empty():
    test_input = pd.Series([], dtype="object")

    with pytest.raises(ValueError):
        mean_center(test_input)


def test_normalize():
    test_input_values = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0]

    test_input_index = pd.Index(
        [
            "Gochujang base",
            "Italian bread",
            "Italian parsley leaves",
            "Mexican cheese blend",
            "Mexican oregano",
            "Shaoxing wine",
            "Sriracha",
            "Tabasco Pepper Sauce",
            "Thai fish sauce",
            "Thai red curry paste",
        ],
        name="ingredient",
    )

    test_input = pd.Series(test_input_values, index=test_input_index)

    test = normalize(test_input)

    true_values = [-0.1, -0.1, 0.15, -0.1, -0.1, -0.1, -0.1, 0.65, -0.1, -0.1]

    true_index = pd.Index(
        [
            "Gochujang base",
            "Italian bread",
            "Italian parsley leaves",
            "Mexican cheese blend",
            "Mexican oregano",
            "Shaoxing wine",
            "Sriracha",
            "Tabasco Pepper Sauce",
            "Thai fish sauce",
            "Thai red curry paste",
        ],
        name="ingredient",
    )

    true = pd.Series(true_values, index=true_index)

    pd.testing.assert_series_equal(test, true)


def test_normalize_empty():

    test = normalize(pd.Series([], dtype="object"))

    true = pd.Series([], dtype="object")

    pd.testing.assert_series_equal(test, true)


def test_softmax():
    test_input_values = [
        0.0,
        0.0,
        0.0,
        247.0,
        4.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        5.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        2.0,
        6.0,
        264.0,
    ]

    test_input_index = pd.Index(
        [
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
            "ingr_sum",
        ],
        name="cuisine",
    )

    test_input = pd.Series(test_input_values, index=test_input_index)

    test = softmax(test_input).astype("str")

    true_values = [
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "4.1399375473943345e-08",
        "1.2118104329146771e-113",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "3.294042279329056e-113",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "2.2195082290865866e-115",
        "1.6400070816759008e-114",
        "8.954135270075986e-113",
        "0.9999999586006246",
    ]

    true_index = pd.Index(
        [
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
            "ingr_sum",
        ],
        name="cuisine",
    )

    true = pd.Series(true_values, true_index)

    pd.testing.assert_series_equal(test, true)


def test_softmax_empty():

    test = softmax(pd.Series([], dtype="object"))

    true = pd.Series([], dtype="object")

    pd.testing.assert_series_equal(test, true)
