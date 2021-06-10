import pytest
import pandas as pd

from src.processing.clean import regex_patterns, clean, clean_ingr


def test_clean_ingr():
    test_list = ["andouille sausage, cooked", "butter,", ",garlic cloves"]

    test = clean_ingr(test_list, [",.*$", "^.*fresh "])

    true = ["andouille sausage", "butter", ""]

    assert test == true


def test_clean_ingr_empty():
    test_list = []

    test = clean_ingr(test_list, [",.*$", "^.*fresh "])

    true = []

    assert test == true


def test_clean_ingr_invalid():
    with pytest.raises(TypeError):
        test_list = [sum, type]
        clean_ingr(test_list, [",.*$", "^.*fresh "])


def test_regex_patterns():
    test_list = ["fresh", "low-fat"]
    test = regex_patterns(test_list)
    true = ["^.*fresh ", "^.*low-fat "]

    assert test == true


def test_regex_pattern_invalid_input():
    test_list = ["fresh", 3]
    test = regex_patterns(test_list)

    assert test is None


def test_clean():
    test_dict = [
        {
            "id": 3037,
            "cuisine": "mexican",
            "ingredients": [
                "eggs",
                "grating cheese",
                "jalapeno chilies",
                "freshly ground pepper",
                "finely chopped onion",
                "salt",
                "tomatoes",
                "vegetable oil",
                "corn tortillas",
            ],
        },
        {
            "id": 19712,
            "cuisine": "cajun_creole",
            "ingredients": [
                "andouille sausage",
                "butter",
                "garlic cloves",
                "dried oregano",
                "chicken broth",
                "bay leaves",
                "creole seasoning",
                "ground cayenne pepper",
                "tomato paste",
                "chili",
                "purple onion",
                "ham",
                "green bell pepper",
                "green onions",
                "long-grain rice",
                "plum tomatoes",
            ],
        },
    ]

    test_df = clean(test_dict, ["^[(].*?[)] ", ",.*$"], ["fresh"])

    true_df_values = [
        ["eggs", "mexican"],
        ["grating cheese", "mexican"],
        ["jalapeno chilies", "mexican"],
        ["freshly ground pepper", "mexican"],
        ["finely chopped onion", "mexican"],
        ["salt", "mexican"],
        ["tomatoes", "mexican"],
        ["vegetable oil", "mexican"],
        ["corn tortillas", "mexican"],
        ["andouille sausage", "cajun_creole"],
        ["butter", "cajun_creole"],
        ["garlic cloves", "cajun_creole"],
        ["dried oregano", "cajun_creole"],
        ["chicken broth", "cajun_creole"],
        ["bay leaves", "cajun_creole"],
        ["creole seasoning", "cajun_creole"],
        ["ground cayenne pepper", "cajun_creole"],
        ["tomato paste", "cajun_creole"],
        ["chili", "cajun_creole"],
        ["purple onion", "cajun_creole"],
        ["ham", "cajun_creole"],
        ["green bell pepper", "cajun_creole"],
        ["green onions", "cajun_creole"],
        ["long-grain rice", "cajun_creole"],
        ["plum tomatoes", "cajun_creole"],
    ]

    true_df_columns = ["ingredient", "cuisine"]

    true_df = pd.DataFrame(data=true_df_values, columns=true_df_columns)

    pd.testing.assert_frame_equal(true_df, test_df)


def test_clean_empty_dict():
    test_dict = []

    test_df = clean(test_dict, ["^[(].*?[)] ", ",.*$"], ["fresh"])

    true_df_values = []

    true_df_columns = ["ingredient", "cuisine"]

    true_df = pd.DataFrame(data=true_df_values, columns=true_df_columns)

    pd.testing.assert_frame_equal(true_df, test_df)


def test_clean_wrong_attrs():
    # Input "cuisines" instead of "cuisine"
    # Input "ingredient" instead of "ingredients"
    test_dict = [
        {
            "id": 3037,
            "cuisines": "mexican",
            "ingredient": [
                "eggs",
                "grating cheese",
                "jalapeno chilies",
                "freshly ground pepper",
                "finely chopped onion",
                "salt",
                "tomatoes",
                "vegetable oil",
                "corn tortillas",
            ],
        },
        {
            "id": 19712,
            "cuisines": "cajun_creole",
            "ingredient": [
                "andouille sausage",
                "butter",
                "garlic cloves",
                "dried oregano",
                "chicken broth",
                "bay leaves",
                "creole seasoning",
                "ground cayenne pepper",
                "tomato paste",
                "chili",
                "purple onion",
                "ham",
                "green bell pepper",
                "green onions",
                "long-grain rice",
                "plum tomatoes",
            ],
        },
    ]

    test_df = clean(test_dict, ["^[(].*?[)] ", ",.*$"], ["fresh"])

    true_df_columns = ["ingredient", "cuisine"]

    true_df = pd.DataFrame(data=[], columns=true_df_columns)

    pd.testing.assert_frame_equal(true_df, test_df)
