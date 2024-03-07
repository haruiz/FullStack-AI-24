import streamlit as st
import requests
import json
import os
from streamlit_js_eval import get_geolocation

API_URL = os.getenv('API_URL', 'http://localhost:8080')
print("API_URL", API_URL)


def call_iris_model(sepal_length, sepal_width, petal_length, petal_width):
    """
    This function calls the iris model
    """
    url = f"{API_URL}/iris-model/predict"

    payload = json.dumps({
    "sepal_length": sepal_length,
    "sepal_width": sepal_width,
    "petal_length": petal_length,
    "petal_width": petal_width
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def call_flowers_model(image_file, lat=0.0, lng=0.0):
    """
    This function calls the flowers model
    """
    url = f"{API_URL}/flowers-model/predict"
    payload = {
        'lat': lat,
        'lng': lng
        }
    files=[
    ('image',image_file)
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.json()



def iris_model_form():
    """
    This function creates the form for the iris model
    """
    st.title('Iris Model')
    st.write('This is a web application that allows you to interact with the iris model')
    sepal_length = st.number_input('Sepal length', min_value=0.0, max_value=10.0, value=5.0)
    sepal_width = st.number_input('Sepal width', min_value=0.0, max_value=10.0, value=5.0)
    petal_length = st.number_input('Petal length', min_value=0.0, max_value=10.0, value=5.0)
    petal_width = st.number_input('Petal width', min_value=0.0, max_value=10.0, value=5.0)

    is_clicked = st.button('Classify')
    if is_clicked:
        json_result = call_iris_model(sepal_length, sepal_width, petal_length, petal_width)
        st.write(json_result)
        st.balloons()


def flowers_model_form():
    """
    This function creates the form for the flowers model
    """
    st.title('Flowers Model')
    st.write('This is a web application that allows you to interact with the flowers model')
    lat = st.number_input('Latitude', min_value=-90.0, max_value=90.0, value=0.0)
    lng = st.number_input('Longitude', min_value=-180.0, max_value=180.0, value=0.0)
    image_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    
    if image_file is not None:
        st.image(image_file, caption='Uploaded Image.', use_column_width=True)
        is_clicked = st.button('Classify')
        if is_clicked:
            json_result = call_flowers_model(image_file, lat, lng)
            st.write(json_result)
            st.snow()


def app():

    st.set_page_config(
        page_title='Home Page', 
        page_icon='🌍', 
        layout='centered', 
        initial_sidebar_state='auto'
    )

    # Add a title
    st.title('Welcome to the home page of the model garden app')
    st.write('This is a web application that allows you to interact with the models in the model garden')

    # Add a select box to the sidebar to select a model
    option = st.sidebar.selectbox(
        'Select a model',
        ('Iris Model', 'Flowers Model')
    )

    if option == 'Iris Model':
        iris_model_form()
    elif option == 'Flowers Model':
        flowers_model_form()


if __name__ == '__main__':
    app()