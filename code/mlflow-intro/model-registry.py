import mlflow
from mlflow.tracking import MlflowClient


def get_best_run_id(experiment_name: str) -> str:
    """
    Get the best run
    :param experiment_name:
    :return:
    """
    # Get the best run
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise Exception(f"Experiment '{experiment_name}' does not exist.")
    experiment_id = experiment.experiment_id
    runs = mlflow.search_runs(experiment_id)
    best_run = runs.sort_values(by=['metrics.accuracy'], ascending=False).iloc[0]
    return best_run["run_id"]


def delete_all_models(experiment_name):
    """
    Delete all models
    :param experiment_name:
    :return:
    """
    client = MlflowClient()
    model_versions = client.search_model_versions(f"name='{experiment_name}-model'")
    for model in model_versions:
        client.delete_model_version(
            name=model.name,
            version=model.version
        )
    registered_models = client.search_registered_models(f"name='{experiment_name}-model'")
    for model in registered_models:
        client.delete_registered_model(model.name)


def register_model(run_id, model_name):
    """
    Register the model
    :param experiment_name:
    :param model_name:
    :param run_id:
    :return:
    """
    client = MlflowClient()
    try:
        model = client.get_registered_model(model_name)
    except:
        model = client.create_registered_model(model_name)
    return model


def create_model_version(run_id: str, model_name: str, model_prefix: str = "/model"):
    """
    Create a model version
    :param run_id:
    :param model_name:
    :param model_prefix:
    :return:
    """
    client = MlflowClient()
    run = client.get_run(run_id)
    model_url = run.info.artifact_uri + model_prefix
    model_version = client.create_model_version(
        name=model_name,
        source=model_url,
        run_id=run_id
    )
    return model_version


def set_model_version_alias(model_name, alias, version=None):
    """
    Set the model alias
    :param version: version of the model to be aliased
    :param model_name: name of the model
    :param alias: alias name
    """
    client = MlflowClient()
    if version is None:
        versions = client.search_model_versions(f"name='{model_name}'")
        if len(versions) == 0:
            raise Exception(f"No versions found for model '{model_name}'")
        version = versions[0].version

    client.set_registered_model_alias(
        name=model_name,
        alias=alias,
        version=version
    )


def get_model_signature_by_version(model_name, version=None):
    """
    Deploy the model
    :param model_name:
    :param alias:
    :param version:
    :return:
    """
    # Get the best run
    client = MlflowClient()
    model_version = client.get_model_version(model_name, version)
    loaded_model = mlflow.pyfunc.load_model(model_version.source)
    print(loaded_model._model_meta._signature)


def get_model_signature_by_alias(model_name, alias):
    """
    Deploy the model
    :param model_name:
    :param alias:
    :return:
    """
    # Get the best run
    client = MlflowClient()
    model_version = client.get_model_version_by_alias(model_name, alias)
    loaded_model = mlflow.pyfunc.load_model(model_version.source)
    print(loaded_model._model_meta._signature)


def register_iris_model():
    """
    Register the iris model
    """
    experiment_name = "iris-classification"
    model_name = "iris-classification-model"
    # delete_all_models(experiment_name)
    best_run_id = get_best_run_id(experiment_name)
    register_model(best_run_id, model_name)
    create_model_version(best_run_id, model_name)
    set_model_version_alias(model_name, "test")
    get_model_signature_by_alias(model_name, "test")


def register_flowers_model():
    """
    Register the iris model
    """
    experiment_name = "flowers-classification"
    model_name = "flowers-classification-model"
    delete_all_models(experiment_name)
    best_run_id = get_best_run_id(experiment_name)
    register_model(best_run_id, model_name)
    create_model_version(best_run_id, model_name)
    set_model_version_alias(model_name, "production")
    get_model_signature_by_alias(model_name, "production")


if __name__ == '__main__':
    mlflow.set_tracking_uri("http://0.0.0.0:4001")

    # register_iris_model()
    register_flowers_model()
