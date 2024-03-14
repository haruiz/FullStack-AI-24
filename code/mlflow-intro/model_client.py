import numpy as np
import requests
import json
from PIL import Image


def test_iris_model():
    """
      Test the iris model
    :return:
    """
    url = "http://127.0.0.1:8081/invocations"
    labels = ["setosa", "versicolor", "virginica"]

    payload = json.dumps({
        "instances": [{
            "sepal length (cm)": 5,
            "sepal width (cm)": 3.2,
            "petal length (cm)": 1.2,
            "petal width (cm)": 0.2
        }]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    predictions = response_json["predictions"]
    class_index = predictions[0]
    print(labels[class_index])


def test_flowers_model():
    """
    Test the flowers model
    :return:
    """
    image_path = "sunflowers.jpg"
    image = Image.open(image_path)
    image = image.resize((180, 180))
    image_arr = np.array(image) / 255.0
    labels = ["daisy", "dandelion", "roses", "sunflowers", "tulips"]

    url = "http://127.0.0.1:8081/invocations"
    payload = json.dumps({
        "instances": [image_arr.tolist()]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    predictions = response_json["predictions"]
    softmax = np.exp(predictions) / np.sum(np.exp(predictions), axis=1)
    argmax = np.argmax(softmax, axis=1)
    class_index = argmax[0]
    print(labels[class_index])


if __name__ == '__main__':
    # test_iris_model()
    test_flowers_model()
