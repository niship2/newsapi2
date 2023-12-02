import pandas as pd
import numpy as np
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

client = bigquery.Client(credentials=credentials)

@st.cache_data
def get_taskname_list():
    query = '''
    SELECT taskname
    FROM `zuba-340305.newsdata.test_newsdata`
    WHERE NOT REGEXP_CONTAINS(taskname,"eu-startup")
    GROUP BY taskname
    '''
    job_config = bigquery.QueryJobConfig(
    )

    dataframe = (
    client.query(query, job_config=job_config)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
        )
    )

    return dataframe



def get_table(task_name):
    task_name_list = task_name
    query = '''
    SELECT 
    STRING_AGG(DISTINCT pubdate) as pubdate,
    url,
    STRING_AGG(DISTINCT title) as title,
    STRING_AGG(DISTINCT IFNULL(description,"-")) as description,
    STRING_AGG(DISTINCT IFNULL(related_industries,"-")) as related_industries,
    STRING_AGG(DISTINCT IFNULL(related_companies,"-")) as related_companies,
    STRING_AGG(DISTINCT IFNULL(keywords,"-")) as keywords,
    STRING_AGG(DISTINCT IFNULL(taskname,"-")) as taskname
        FROM `zuba-340305.newsdata.test_newsdata`
    WHERE taskname IN UNNEST(@task_name_list)
    AND NOT REGEXP_CONTAINS(taskname,"eu-startup")
    GROUP BY url
    
    '''
    job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ArrayQueryParameter("task_name_list", "STRING",task_name_list),
    ]
    )

    
    dataframe = (
    client.query(query, job_config=job_config)
    .result()
    .to_dataframe(
        create_bqstorage_client=True,
        )
    )
    
    
    return dataframe[["taskname","title","url","pubdate","description"]]
