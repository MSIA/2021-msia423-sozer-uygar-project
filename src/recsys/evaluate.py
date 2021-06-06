import json
from sklearn.model_selection import train_test_split


def generate_splits(filepath, train_size=0.8):
    with open(filepath, "r") as f:
        obj = json.load(f)

    train, test = train_test_split(obj, train_size=train_size, shuffle=True)

    return train, test


def get_accuracy(trained_model, test_list):

    cleantest = [(i["ingredients"], i["cuisine"]) for i in test_list]

    def evaluator(x):
        return x[1] in list(trained_model.predict(x[0]).index)

    return sum(list(map(evaluator, cleantest))) / len(cleantest)
