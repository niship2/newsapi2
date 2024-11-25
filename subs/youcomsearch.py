import requests
import os
import streamlit as st

from langchain.retrievers.you import YouRetriever
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatAnthropic


YOUCOM_API_KEY = st.secrets["YOUCOM_API_KEY"]
os.environ["YDC_API_KEY"] = YOUCOM_API_KEY


def get_news_snippets_for_query(query):
    headers = {"X-API-Key": YOUCOM_API_KEY}
    params = {
        "query": query,
        "recency": "month",  # day, week, month, year
    }
    return requests.get(
        f"https://api.ydc-index.io/news?q={query}",
        params=params,
        headers=headers,
    ).json()


# os.environ["ANTHROPIC_API_KEY"] = userdata.get('anthropic')
# model = "claude-2"
# qa = RetrievalQA.from_chain_type(llm=ChatAnthropic(model=model), chain_type="stuff", retriever=yr)


def get_llm_answer(query):
    model = "gpt-4o"
    yr = YouRetriever()
    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model=model), chain_type="stuff", retriever=yr
    )
    return qa.invoke(query)
