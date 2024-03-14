import mlflow
import tensorflow as tf
import numpy as np
import matplotlib.pylab as plt
import tensorflow_datasets as tfds
import keras
from keras.models import Sequential
import keras.layers as layers
from mlflow.models import infer_signature
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt

IMG_SIZE = 180


def fetch_data():
    """
    Fetch the data from the web
    :return:
    """
    # Fetch data from the web
    (ds_train, ds_validation, ds_test), metadata = tfds.load(
        "tf_flowers",
        split=['train[:80%]', 'train[80%:90%]', 'train[90%:]'],
        as_supervised=True,
        with_info=True
    )
    return ds_train, ds_validation, ds_test, metadata


def preprocess_data(ds_subset, batch_size=32, shuffle=False, augment=False):
    """
    Preprocess the data
    :param ds_train:
    :param ds_validation:
    :param ds_test:
    :param metadata:
    :return:
    """
    """
            Prepare the data for training
            :param ds_subset: 
            :param batch_size: 
            :param shuffle: 
            :param augment: 
            :return: 
            """
    resize_and_rescale = Sequential([
        keras.layers.experimental.preprocessing.Resizing(IMG_SIZE, IMG_SIZE),
        keras.layers.experimental.preprocessing.Rescaling(1. / 255)
    ])

    data_augmentation = Sequential([
        keras.layers.experimental.preprocessing.RandomFlip("horizontal_and_vertical"),
        keras.layers.experimental.preprocessing.RandomRotation(0.1),
        keras.layers.experimental.preprocessing.RandomZoom(0.1)
    ])

    ds_subset = ds_subset.map(lambda x, y: (resize_and_rescale(x), y),
                              num_parallel_calls=tf.data.experimental.AUTOTUNE)

    # shuffle the dataset if needed
    if shuffle:
        ds_subset = ds_subset.shuffle(1000)

    # create data batches
    ds_subset = ds_subset.batch(batch_size)

    # apply data augmentation
    if augment:
        ds_subset = ds_subset.map(lambda x, y: (data_augmentation(x, training=True), y),
                                  num_parallel_calls=tf.data.experimental.AUTOTUNE)

    # Use buffered prefecting on all datasets
    return ds_subset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)


def build_model(num_classes):
    """
    Build the model
    :param num_classes:
    :return:
    """
    model = Sequential([
        layers.Conv2D(16, 3, padding='same', activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes)
    ])
    return model


def train_model(model, ds_train, ds_validation, epochs=10):
    """
    Train the model
    :param model:
    :param ds_train:
    :param ds_validation:
    :param epochs:
    :return:
    """
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )

    history = model.fit(
        ds_train,
        validation_data=ds_validation,
        epochs=epochs
    )
    return history


def get_metrics_figure(history):
    """
    Get the metrics figures
    :param history:
    :return:
    """
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(10)

    fig = plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    return fig


def get_confusion_matrix_figure(model, transformed_ds_test, metadata):
    """
    Confusion matrix
    :param model:
    :param ds_test:
    :param metadata:
    :return:
    """
    labels = metadata.features['label'].names
    y = [labels for imgs, labels in tfds.as_numpy(transformed_ds_test.unbatch())]
    y_pred_probs = model.predict(transformed_ds_test)
    y_pred = np.argmax(y_pred_probs, axis=1)

    fig, _ = plt.subplots(nrows=1, figsize=(10, 10))
    ax = plt.subplot(1, 1, 1)
    ax.grid(False)
    cf = confusion_matrix(y, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cf, display_labels=labels)
    disp.plot(cmap=plt.cm.Blues, values_format='d', ax=ax)
    return fig


def run_experiment(experiment_name: str):
    """
    Run the experiment
    :return:
    """
    # Fetch the data
    ds_train, ds_validation, ds_test, metadata = fetch_data()

    # Preprocess the data
    transformed_ds_train = preprocess_data(ds_train, batch_size=32, shuffle=True, augment=True)
    transformed_ds_validation = preprocess_data(ds_validation, batch_size=32)
    transformed_ds_test = preprocess_data(ds_test, batch_size=32)

    # Build the model
    num_classes = metadata.features['label'].num_classes
    model = build_model(num_classes)

    # Train the model
    history = train_model(model, transformed_ds_train, transformed_ds_validation, epochs=10)

    # Get the metrics figures
    metrics_fig = get_metrics_figure(history)

    # Get the confusion matrix figure
    confusion_matrix_fig = get_confusion_matrix_figure(model, transformed_ds_test, metadata)

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment:
        print("Experiment already exists.")
        experiment_id = experiment.experiment_id
    else:
        print("Creating a new experiment")
        experiment_id = mlflow.create_experiment(experiment_name)

    with mlflow.start_run(experiment_id=experiment_id, run_name="flowers-classification") as run:
        mlflow.log_param("num_classes", num_classes)
        mlflow.log_param("epochs", 10)
        mlflow.log_figure(metrics_fig, "metrics.png")
        mlflow.log_figure(confusion_matrix_fig, "confusion_matrix.png")
        mlflow.log_metric("accuracy", history.history['accuracy'][-1])
        mlflow.log_metric("val_accuracy", history.history['val_accuracy'][-1])
        mlflow.log_metric("loss", history.history['loss'][-1])
        mlflow.log_metric("val_loss", history.history['val_loss'][-1])

        # get model signature
        sample = transformed_ds_test.unbatch().as_numpy_iterator().next()
        sample_img, sample_label = sample
        sample_img = sample_img[None, ...]
        sample_img_predictions = model(sample_img).numpy()
        model_signature = infer_signature(model_input=sample_img, model_output=sample_img_predictions)

        mlflow.keras.log_model(model, "model", signature=model_signature)
        mlflow.log_param("model_summary", model.summary())


if __name__ == '__main__':
    mlflow.set_tracking_uri("http://0.0.0.0:4000")
    experiment_name = "flowers-classification"
    run_experiment(experiment_name)