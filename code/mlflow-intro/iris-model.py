# third party libraries
import typing
import warnings
from datetime import datetime
import pandas
import seaborn as sns
from sklearn.datasets import load_iris

import matplotlib.pyplot as plt
# MLflow libraries
import mlflow
from mlflow.models.signature import infer_signature

# ML libraries  for the analysis
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")


# Function to load the dataset
def fetch_data() -> pandas.DataFrame:
    """
    Load the data
    :return:  pandas.DataFrame
    """
    # Load the iris dataset
    iris = load_iris()
    # Create a pandas dataframe
    df = pandas.DataFrame(data=iris.data, columns=iris.feature_names)
    # Add the target column
    df['target'] = iris.target
    return df


def split_dataset(data: pandas.DataFrame, test_size=0.2, random_state=7) -> typing.Tuple:
    """
    Split the dataset into train and validation
    :param data:
    :param test_size:
    :param random_state:
    :return:
    """
    X = data.iloc[:, 0:4]
    y = data.iloc[:, 4]
    X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=test_size,
                                                                    random_state=random_state)
    return X_train, X_validation, Y_train, Y_validation


def run_experiment(experiment_name):
    """
    Run the experiment
    :param experiment_name:
    :return:
    """
    # 1. Load the data
    data = fetch_data()
    # 2. Split the dataset
    X_train, X_validation, Y_train, Y_validation = split_dataset(data)
    # 3. make a dictionary with the algorithms to be evaluated
    models = {
        'LR': LogisticRegression(solver='liblinear', multi_class='ovr'),
        'LDA': LinearDiscriminantAnalysis(),
        'KNN': KNeighborsClassifier(),
        'CART': DecisionTreeClassifier(),
        'NB': GaussianNB(),
        'SVM': SVC(gamma='auto')
    }

    # create mlfow experiment if it does not exist
    # otherwise, get the experiment id
    experiment = mlflow.get_experiment_by_name(experiment_name)

    # create the experiment
    if experiment:
        print("Experiment already exists.")
        experiment_id = experiment.experiment_id
    else:
        print("Creating a new experiment")
        experiment_id = mlflow.create_experiment(experiment_name)

    # Run each model in a separate run
    for model_name, model in models.items():
        print(f"Running {model_name}...")

        # create unique id for the run
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_id = f"{model_name}-{run_id}"

        # start the run and log the parameters
        with mlflow.start_run(experiment_id=experiment_id, run_name=run_id) as run:
            # train the model
            model.fit(X_train, Y_train)
            mlflow.log_param("model_name", model_name)

            # make predictions
            predictions = model.predict(X_validation)
            accuracy = accuracy_score(Y_validation, predictions)
            mlflow.log_metric("accuracy", accuracy)

            # log the confusion matrix
            cm = confusion_matrix(Y_validation, predictions)
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_title(f"Confusion Matrix for {model_name}")
            sns.heatmap(cm, annot=True, ax=ax, fmt='g')
            plt.xlabel('Predicted')
            plt.ylabel('True')
            mlflow.log_figure(fig, f"confusion_matrix_{model_name}.png")

            # log the model
            signature = infer_signature(X_train, model.predict(X_train))
            mlflow.sklearn.log_model(model, "model", signature=signature)
            print(f"{model_name} accuracy: {accuracy}, run_id: {run.info.run_id}")


if __name__ == '__main__':
    mlflow.set_tracking_uri("http://0.0.0.0:4001")
    experiment_name = "iris-classification"
    run_experiment(experiment_name)
