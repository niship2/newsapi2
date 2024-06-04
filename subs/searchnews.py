import pandas as pd
import requests
import datetime
from datetime import datetime
from serpapi import GoogleSearch
import streamlit as st


SERPAPI_API_KEY = st.secrets["SERPAPI_API_KEY"]


def get_date_format(d):
    dt = datetime.today()  # ローカルな現在の日付と時刻を取得
    if "hours ago" in str(d) or "mins ago" in str(d):
        return dt.date()
    else:
        return str(d)


def return_period(nws, time_op):
    if nws == "google":
        if time_op == "直近24時間":
            return "d1"
        elif time_op == "直近1週間":
            return "w1"
        elif time_op == "直近2週間":
            return "w2"
        elif time_op == "直近1ヶ月":
            return "m1"
        else:
            return "d1"
    else:
        if time_op == "直近24時間":
            return "Day"
        elif time_op == "直近1週間":
            return "Week"
        elif time_op == "直近2週間":
            return "Week"
        elif time_op == "直近1ヶ月":
            return "Month"
        else:
            return "Day"


def exclude_site(url):
    if "movies.yahoo.com" in url:
        return False
    else:
        return True


@st.cache_data(ttl=3600)
def extract_google_news(searchword_list, time_op, additional_word):
    time = return_period(nws="google", time_op=time_op)

    serp_url_list = []
    wds = []
    words = searchword_list
    for wd in words:
        params = {
            "api_key": SERPAPI_API_KEY,
            "engine": "google",
            "q": wd + " " + additional_word,
            "google_domain": "google.com",
            # "hl": "en",
            "filter": 1,
            "tbm": "nws",
            "as_qdr": time,
            "num": 100,
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        # urlを抽出
        import requests

        # serp_url_list.append(results["search_information"]["menu_items"][0]["serpapi_link"])
        serp_url_list.append(results["search_metadata"]["json_endpoint"])
        wds.append(wd)
        try:
            for res in results["serpapi_pagination"]["other_pages"].values():
                jsonres = requests.get(res + "&api_key=" + SERPAPI_API_KEY)
                # print(jsonres.json()["search_metadata"]["json_endpoint"])
                serp_url_list.append(jsonres.json()["search_metadata"]["json_endpoint"])
                wds.append(wd)
        except:
            pass

    gnews_df = pd.DataFrame()
    for url in serp_url_list:
        r = requests.get(url)  # +"&api_key=" + serp_api_key)
        res = r.json()

        try:
            temp_df = pd.DataFrame(res["news_results"])
            temp_df["searchword"] = res["search_information"]["query_displayed"]
            gnews_df = pd.concat([gnews_df, temp_df])
        except:
            pass

    # ちょっと整形
    gnews_df = gnews_df.reset_index().drop(
        columns={"position", "index"}
    )  # ["pubdate","url","title","description","related_industries","related_companies","keywords"]
    gnews_df["date"] = gnews_df["date"].apply(get_date_format)
    gnews_df["exclude"] = gnews_df["link"].apply(exclude_site)
    gnews_df = gnews_df[gnews_df["exclude"] == True]
    # gnews_df["genre"] = task_name
    return gnews_df[["searchword", "title", "link", "date", "source", "snippet"]]


@st.cache_data(ttl=3600)
def get_bing_news(word, time_op, additional_word):
    # Add your Bing Search V7 subscription key and endpoint to your environment variables.
    subscription_key = st.secrets["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
    endpoint = st.secrets["BING_SEARCH_V7_ENDPOINT"]

    # Query term(s) to search for.

    # Construct a request
    mkt = "en-US"
    params = {
        "q": word + " " + additional_word,
        "mkt": mkt,
        "freshness": return_period(nws="bing", time_op=time_op),
        # "since": time1,
        "count": 100,
        "sortBy": "Date",
    }
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}

    # Call the API
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as ex:
        return ex


def extract_bing_news(searchword_list, time_op, additional_word):
    bingnewsdf = pd.DataFrame()
    try:
        for wd in searchword_list:
            content = get_bing_news(
                word=wd, time_op=time_op, additional_word=additional_word
            )
            temp_df = pd.DataFrame(content["value"])
            temp_df["searchword"] = wd + " " + additional_word
            temp_df["title"] = temp_df["name"]
            temp_df["link"] = temp_df["url"]
            bingnewsdf = pd.concat([bingnewsdf, temp_df])

            bignewsdf["exclude"] = bignewsdf"link"].apply(exclude_site)
            bingnewsdf = get_bing_news[bingnewsdf["exclude"] == True]

    except:
        pass

    return bingnewsdf[["searchword", "title", "link", "description", "datePublished"]]
