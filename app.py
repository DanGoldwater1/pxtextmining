
import streamlit as st
import pandas 
# from querying_apis import querying_apis
import tempfile
import os
import requests
import time

target_dict = {
    "Multilabel": "m",
    "Sentiment" : "s", 
    "Multilabel and Sentiment":"ms"
}


def get_labels_from_response(results_url):
    status_message = st.empty()
    final_labels = None
    query_wait_time = 20

    while True:
        results_response = requests.get(results_url)
        if results_response.status_code == 200:
            final_labels = results_response.json()
            # Update the placeholder with the final labels
            status_message.json(final_labels)  # Use .json() to nicely format the JSON response
            break
        else:
            # Update the status message placeholder to inform the user
            status_message.text(f'Not ready! Trying again in {query_wait_time} seconds...'.format(query_wait_time))
            time.sleep(query_wait_time)

    return final_labels
st.title('Labelling Data Via API')
st.write("Use this to generate labels and sentiment for your input data. This is a very simple wrapper around the APIs described [here](https://the-strategy-unit.github.io/pxtextmining/reference/API/slow_API/#). Expect this to take at least 3 minutes to run. Try to combine your data into fewer, larger files, rather than putting many files through this. ")

url = st.text_input("API URL")
api_key = st.text_input("API Key")
input_df = st.file_uploader("Choose a CSV file", type="csv")
st.write("Probably set this target to 'multilabel and sentiment'. ")
target_key = st.selectbox("Target", target_dict.keys())

if input_df is not None:
    input_df = pandas.read_csv(input_df)
    st.dataframe(input_df.head())  
    text_data = querying_apis.format_df(df=input_df)
    st.write("Preview of uploaded CSV:")

    if st.button('Send to API'):
        params_dict = {'code': api_key, 'target': target_dict[target_key]}
        response = requests.post(url, params= params_dict, json = text_data)
        print(response.status_code)
        if response.status_code == 202:
            results_url = response.text
            st.write("Initial query made successfully. Now for the API to do labelling")
        else:
            st.write(f"Got a bad response from the post. Status code {response.status_code}")

        time_so_far = 0
        time_message = st.empty()
        while True:
            results_response = requests.get(results_url)
            if results_response.status_code == 200:
                labelled_data = results_response.json()
                break
            else:
                time_message.write(f'Not ready! Time so far is {time_so_far} seconds. Trying again in 20 seconds...')
                time_so_far += 20
                time.sleep(20)

        time_message.write("All done!")
            

        st.write("Final Data from API:")
        st.write(labelled_data)

        labelled_data = pandas.DataFrame(labelled_data)
        labelled_data = labelled_data.to_csv(index=False)
        # output_filename = st.text_input("Output Filename")
        # if not output_filename:
        #     output_filename = "labelled_data"
        # output_filename = output_filename if output_filename.endswith(".csv") else f"{output_filename}.csv"
        output_filename = "labelled_data.csv"



        st.download_button(
            label="Download labelled data",
            data=labelled_data,
            file_name=output_filename,
            mime="text/csv"
        )
