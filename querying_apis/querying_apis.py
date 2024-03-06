import requests
import time
import os
from dotenv import load_dotenv
import json
import csv

load_dotenv()


import pandas


def format_df_fast(df: pandas.DataFrame):

    required_cols = ['comment_id', 'comment_text', 'question_type']
    assert all([col in set(df.columns) for col in required_cols]), "Your iput csv doesn't have the right columns"
    filtered_df = df[['comment_id', 'comment_text', 'question_type']]
    filtered_df = filtered_df.replace({pandas.np.nan: ""})
    # filtered_df = filtered_df.replace({"": "egg"})
    filtered_df = filtered_df.replace({None: ""})
    formatted_data = filtered_df.to_dict(orient='records')
    return formatted_data

def format_df_slow(df: pandas.DataFrame):

    required_cols = ['comment_id', 'comment_text', 'question_type']
    assert all([col in set(df.columns) for col in required_cols]), "Your iput csv doesn't have the right columns"
    filtered_df = df[['comment_id', 'comment_text', 'question_type']]
    filtered_df = filtered_df.replace({pandas.np.nan: None})
    formatted_data = filtered_df.to_dict(orient='records')
    
    return formatted_data

def save_labels_to_csv(labeled_data, filename):
    with open(filename, mode='w', newline='') as file:
      writer = csv.DictWriter(file, fieldnames=['comment_id', 'comment_text', 'question_type'])
      writer.writeheader()
      for data in labeled_data:
          writer.writerow(data)
    print(f'Data written to {filename}')

def send_post_to_slow_api(text_data, api_key=None, url=None, target='ms'):

    if api_key==None:
        api_key = os.getenv('SLOW_API_KEY')

    if url==None:
        url = os.getenv('SLOW_API_URL')

    params_dict = {'code': api_key, 'target': target}
    response = requests.post(url, params= params_dict, json = text_data)
    print(response.status_code)
    if response.status_code == 202:
        results_url = response.text
        return results_url
    else:
        print(f"Got a bad response from the post. Status code {response.status_code}")
        # print(f'{response.text}')
        return f"Got a bad response from the post. Status code {response.status_code}. I had url {url}. I had api key {api_key}"


def get_labels_from_response(results_url, query_wait_time):
    while True:
        results_response = requests.get(results_url)
        if results_response.status_code == 200:
            final_labels = results_response.json()
            break
        else:
            print('Not ready! Trying again in 300 seconds...')
            time.sleep(query_wait_time)
    print(final_labels)
    return final_labels

# text_data = format_df(pandas.read_csv("querying_apis/test_data.csv"))
# res = send_post_to_slow_api(text_data=text_data, 
#                             api_key=api_key, url=url
#                             )
# print(res)
