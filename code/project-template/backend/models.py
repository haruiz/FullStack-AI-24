import numpy as np
from enum import Enum, auto
from pathlib import Path
import typing
from abc import ABC
import typing

class Framework(Enum):
    tensorflow = auto()
    sklearn = auto()
    pytorch = auto()

class Model(ABC):
    def __init__(self, 
                 model_name: str,
                 model_path: typing.Union[str, Path], 
                 framework: Framework, 
                 version: int,
                 classes: typing.List[str]
                 ):
        self.model_name = model_name
        self.model_path = model_path
        self.framework = framework
        self.version = version
        self.classes = classes
        self.model = None
        
        self.load()

    def load(self):
        """
        Load the model from the model_path
        """
        if self.framework == Framework.sklearn:
            self.__load_sklearn_model()
        elif self.framework == Framework.tensorflow:
            self.__load_tensorflow_model()
        else:
            raise ValueError(f"Framework {self.framework} not supported")

    def __load_sklearn_model(self):
        """
        Load a sklearn model
        """
        from joblib import load
        self.model = load(self.model_path)

    def __load_tensorflow_model(self):
        """
        Load a tensorflow model
        """
        import tensorflow as tf
        self.model = tf.keras.models.load_model(self.model_path)

    def __call__(self, X: typing.Any) -> typing.Any:
        return self.predict(X)

    def predict(self, X: typing.Any) -> typing.Any:
        """
        Make a prediction
        """
        raise NotImplementedError("Subclasses must implement this method")
    


class IrisModel(Model):
    def __init__(self, framework: Framework = Framework.tensorflow):
        
        if framework == Framework.tensorflow:
            model_path = "models/iris-model/tf/model"
            version = 1
        elif framework == Framework.sklearn:
            model_path = "models/iris-model/sklearn/model.pk"
            version = 1
        else:
            raise ValueError(f"Framework {framework} not supported")
        classes = ["setosa", "versicolor", "virginica"]
        name = "iris-model"
        super().__init__(name, model_path, framework, version, classes)
    
    def predict(self, X):
        """
        Make a prediction
        """
        outputs = []
        if self.framework == Framework.sklearn:
            predictions =  self.model.predict_proba(X)
            for i, xi_probs in enumerate(predictions):
                outputs.append({self.classes[j]: round(float(xi_probs[j]), 3) for j in range(len(xi_probs))})
        elif self.framework == Framework.tensorflow:
            outputs = []
            predictions =  self.model.predict(X)
            for i, xi_softmax in enumerate(predictions):
                outputs.append({self.classes[j]: round(float(xi_softmax[j]), 3) for j in range(len(xi_softmax))})
        return outputs
            


class FlowersModel(Model):
    def __init__(self):
        model_path = "models/flowers-model/tf/model"
        framework = Framework.tensorflow
        version = 1
        classes = ["daisy", "dandelion", "roses", "sunflowers", "tulips"]
        name = "flowers-model"
        super().__init__(name, model_path, framework, version, classes)

        self.target_size = (180, 180)
    
    def processing_input(self, image_bytes:  bytes):
        """
        Preprocess the input image
        """
        import tensorflow as tf
        from PIL import Image as PILImage
        from io import BytesIO
        
        image_stream = BytesIO(image_bytes)
        resized_image = tf.keras.preprocessing.image.load_img(image_stream, target_size=self.target_size)
        image_arr = tf.keras.preprocessing.image.img_to_array(resized_image)
        img_tensor = tf.convert_to_tensor(image_arr)
        img_tensor = tf.expand_dims(img_tensor, 0)
        img_tensor = tf.divide(img_tensor, 255.0)
        return img_tensor
    
    def predict(self, image_bytes: bytes):
        """
        Make a prediction
        """
        import tensorflow as tf
        img_tensor = self.processing_input(image_bytes)
        scores = self.model.predict(img_tensor)
        predictions = tf.nn.softmax(scores)
        outputs = []
        for i, xi_softmax in enumerate(predictions):
            outputs.append({self.classes[j]: round(float(xi_softmax[j]), 3) for j in range(len(xi_softmax))})
        return outputs