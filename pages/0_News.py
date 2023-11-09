from typing import Any
import numpy as np
import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import math
import json
import pandas as pd

from GoogleNews import GoogleNews


if "searchword" not in st.session_state:
    st.session_state["searchword"] = "CO2"

if "google_newsdf" not in st.session_state:
    st.session_state["google_newsdf"] = pd.DataFrame()

if "bing_newsdf" not in st.session_state:
    st.session_state["bing_newsdf"] = pd.DataFrame()

if "newsapi_df" not in st.session_state:
    st.session_state["newsapi_df"] = pd.DataFrame()


@st.cache_data
def get_newsapi_news(word, page, time1, time2):
    url = (
        "https://newsapi.org/v2/everything?"
        "q=" + word + "&"
        "page=" + str(page) + "&"
        "from=" + time1 + "&"
        "to=" + time2 + "&"
        "domains=techcrunch.com,wired.com,ycombinator.com&"
        "sortBy=popularity&"
        "apiKey=" + st.secrets["NEWSAPI_KEY"]
    )

    response = requests.get(url)
    return response


@st.cache_data
def get_google_news(word, page, time1, time2):
    googlenews = GoogleNews()
    googlenews.set_lang("en")
    googlenews.set_time_range(time1, time2)
    googlenews.set_encode("utf-8")
    googlenews.get_news(word)

    return googlenews.results()


@st.cache_data
def get_bing_news(word, page, time1, time2):
    # Add your Bing Search V7 subscription key and endpoint to your environment variables.
    subscription_key = st.secrets["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
    endpoint = st.secrets["BING_SEARCH_V7_ENDPOINT"]

    # Query term(s) to search for.
    query = word
    query2 = word

    # Construct a request
    mkt = "en-US"
    params = {"q": query, "mkt": mkt, "since": time1}
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}

    # Call the API
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as ex:
        return ex


def news_main() -> None:
    # desig_word = st.text_input("指定検索キーワード", disabled=True, value="Air Capture")
    # additional_word = st.text_input("追加キーワード", placeholder="CO2")
    searchword = st.text_input("検索語", value="CO2", placeholder="CO2")
    # searchword = st.selectbox("検索語指定：", [desig_word, additional_word])

    with st.sidebar:
        st.write("可能な場合日付指定")
        format = "%Y-%m-%d"
        start_d = st.date_input(
            "開始日", disabled=False, value=datetime.now() - timedelta(days=10)
        )
        end_d = st.date_input("終了日", disabled=False, value=datetime.now())

    with st.expander("Google News"):
        result = get_google_news(word=searchword, page=1, time1=start_d, time2=end_d)
        google_newsdf = pd.DataFrame(result)
        google_newsdf["link"] = "http://" + google_newsdf["link"]
        # st.data_editor(google_newsdf)
        st.dataframe(
            google_newsdf[["title", "link", "datetime", "media"]],
            column_config={
                "link": st.column_config.LinkColumn("link"),
            },
            hide_index=True,
        )

    with st.expander("Bing News"):
        content = get_bing_news(word=searchword, page=1, time1=start_d, time2=end_d)
        bingnewsdf = pd.DataFrame(content["value"])
        st.write(bingnewsdf)

    with st.expander("NewsAPI"):
        response = get_newsapi_news(
            word=searchword,
            page=1,
            time1=start_d.strftime(format),
            time2=end_d.strftime(format),
        )
        newsapi_df = pd.DataFrame(json.loads(response.text))
        st.write(newsapi_df)

    # format = "%Y-%m-%d"
    # time1 = (datetime.now()).strftime(format)
    # time2 = (datetime.now() - timedelta(days=10)).strftime(format)

    st.session_state["searchword"] = searchword
    st.session_state["google_newsdf"] = google_newsdf
    st.session_state["bingnewsdf"] = bingnewsdf
    st.session_state["newsapi_df"] = newsapi_df


st.set_page_config(page_title="News", page_icon="📹", layout="wide")
news_main()
