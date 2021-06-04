import json
import os
from sklearn.model_selection import train_test_split


def generate_splits(filepath, output_folder, train_size=0.8):
    with open(filepath, "r") as f:
        obj = json.load(f)

    train, test = train_test_split(obj, train_size=train_size, shuffle=True)

    output_path = output_folder + "/evaluate/"

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    with open(output_path + "train.json", "w") as f:
        f.write(json.dumps(train))

    with open(output_path + "test.json", "w") as f:
        f.write(json.dumps(test))


def get_accuracy(trained_model, test_list):

    cleantest = [(i["ingredients"], i["cuisine"]) for i in test_list]

    def evaluator(x):
        return x[1] in list(trained_model.predict(x[0]).index)

    return sum(list(map(evaluator, cleantest))) / len(cleantest)
