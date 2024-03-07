import numpy as np
from enum import Enum, auto
from pathlib import Path
import typing

class Framework(Enum):
    tensorflow = auto()
    sklearn = auto()
    pytorch = auto()

class Model:
    def __init__(self, 
                 model_path: typing.Union[str, Path], 
                 framework: Framework, 
                 version: int,
                 classes: typing.List[str]
                 ):
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


    def predict(self, X: np.ndarray):
        """
        Make a prediction
        """
        predictions = self.model.predict(X)
        predictions = predictions.tolist()
        if self.classes:
            if self.framework == Framework.sklearn:
                predictions = [self.classes[class_idx] for class_idx in predictions]
            elif self.framework == Framework.tensorflow:
                predictions = [self.classes[np.argmax(pred)] for pred in predictions]
        return predictions