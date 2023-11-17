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

# if "newsapi_df" not in st.session_state:
#    st.session_state["newsapi_df"] = pd.DataFrame()


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
    delta = time2 - time1
    # st.write(delta.days)
    googlenews = GoogleNews(period="{}d".format(delta.days))
    googlenews.set_lang("en")
    # googlenews.set_time_range(time1, time2)
    googlenews.set_encode("utf-8")
    googlenews.get_news(word)

    return googlenews.results(sort=True)


@st.cache_data
def get_bing_news(word, page, time1, time2):
    # Add your Bing Search V7 subscription key and endpoint to your environment variables.
    subscription_key = st.secrets["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
    endpoint = st.secrets["BING_SEARCH_V7_ENDPOINT"]

    # Query term(s) to search for.
    query = word

    # Construct a request
    mkt = "en-US"
    params = {"q": query, "mkt": mkt, "since": time1, "count": 100}
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
    searchword = st.text_input(
        "検索語ーカンマ区切りで複数指定可能（複数指定は未実装）",
        value="Direct Air Capture",
        placeholder="Cirect Air Capture",
    )
    # searchword = st.selectbox("検索語指定：", [desig_word, additional_word])

    with st.sidebar:
        st.write("日付指定（指定が効かない場合あり）")
        format = "%Y-%m-%d"
        format2 = "%m/%d/%Y"
        start_d = st.date_input(
            "開始日", disabled=False, value=datetime.now() - timedelta(days=20)
        )
        # st.write(start_d.strftime("%s"))
        end_d = st.date_input("終了日", disabled=False, value=datetime.now())

    with st.expander("スタートアップ新規資金調達情報"):
        # st.write("検索語＆fundingでの検索結果")
        fund_selectword = (
            ""  # st.selectbox("付加キーワード", ["", "raised", "funding", "fund"])
        )
        funding_searchword = searchword + " " + fund_selectword

        st.write("「{}」でのgoogle news".format(funding_searchword))
        result = get_google_news(
            word=funding_searchword,
            page=1,
            time1=start_d,
            time2=end_d,
        )

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

        st.markdown("---")
        st.write("「{}」でのbing news".format(funding_searchword))
        # bing
        content = get_bing_news(
            word=funding_searchword,
            page=1,
            time1=start_d.strftime("%s"),
            time2=end_d.strftime("%s"),
        )
        bingnewsdf = pd.DataFrame(content["value"])
        bingnewsdf["title"] = bingnewsdf["name"]
        bingnewsdf["link"] = bingnewsdf["url"]
        st.dataframe(
            bingnewsdf[["title", "link", "datePublished", "category"]],
            column_config={
                "link": st.column_config.LinkColumn("link"),
            },
            hide_index=True,
        )

    with st.expander("IPO,M&A情報"):
        # st.write("検索語＆M&A,検索語＆IPOでの検索結果")
        ma_selectword = ""  # st.selectbox("付加キーワード", ["", "acquired", "M&A", "IPO"])
        ma_searchword = searchword + " " + ma_selectword
        for sw in [ma_searchword]:
            st.write("「{}」でのgoogle newsサーチ結果".format(sw))
            result = get_google_news(
                word=sw,
                page=1,
                time1=start_d,
                time2=end_d,
            )

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

            st.markdown("---")

            st.write("「{}」でのbing newsサーチ結果".format(sw))
            # bing
            content = get_bing_news(
                word=funding_searchword,
                page=1,
                time1=start_d.strftime("%s"),
                time2=end_d.strftime("%s"),
            )
            bingnewsdf = pd.DataFrame(content["value"])
            bingnewsdf["title"] = bingnewsdf["name"]
            bingnewsdf["link"] = bingnewsdf["url"]
            st.dataframe(
                bingnewsdf[["title", "link", "datePublished", "category"]],
                column_config={
                    "link": st.column_config.LinkColumn("link"),
                },
                hide_index=True,
            )

    with st.expander("業界関連ニュース"):
        st.write("「{}」でのgoogle news".format(searchword))
        result = get_google_news(
            word=searchword,
            page=1,
            time1=start_d,
            time2=end_d,
        )

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

        st.markdown("---")
        st.write("「{}」でのbing news".format(searchword))
        # bing
        content = get_bing_news(
            word=searchword,
            page=1,
            time1=start_d.strftime("%s"),
            time2=end_d.strftime("%s"),
        )
        bingnewsdf = pd.DataFrame(content["value"])
        bingnewsdf["title"] = bingnewsdf["name"]
        bingnewsdf["link"] = bingnewsdf["url"]
        st.dataframe(
            bingnewsdf[["title", "link", "datePublished", "category"]],
            column_config={
                "link": st.column_config.LinkColumn("link"),
            },
            hide_index=True,
        )

    st.session_state["searchword"] = searchword
    st.session_state["google_newsdf"] = google_newsdf
    st.session_state["bingnewsdf"] = bingnewsdf


st.set_page_config(page_title="News", page_icon="📹", layout="wide")
news_main()
