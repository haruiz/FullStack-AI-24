import streamlit as st
import requests
import json



def call_api(sepal_length, sepal_width, petal_length, petal_width):
    url = "http://localhost:8080/iris-model/predict?model_name=iris_model"

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
    response_json = response.json()
    st.write("The predicted class is: ", response_json['prediction'])



def app():

    st.set_page_config(
        page_title='Home Page', 
        page_icon='🌍', 
        layout='centered', 
        initial_sidebar_state='auto'
    )

    st.title('Welcome to the home page of the iris web app')
    st.write('This is a web application that allows you to explore the famous iris dataset')

    sepal_length = st.number_input('Sepal length', min_value=0.0, max_value=10.0, value=5.0)
    sepal_width = st.number_input('Sepal width', min_value=0.0, max_value=10.0, value=5.0)
    petal_length = st.number_input('Petal length', min_value=0.0, max_value=10.0, value=5.0)
    petal_width = st.number_input('Petal width', min_value=0.0, max_value=10.0, value=5.0)

    
    is_clicked = st.button('Classify')
    if is_clicked:
        call_api(sepal_length, sepal_width, petal_length, petal_width)
        st.balloons()


if __name__ == '__main__':
    app()