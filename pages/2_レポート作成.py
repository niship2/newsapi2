from typing import Any
import numpy as np
import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import math
import json
import pandas as pd
import requests
import time

summary_url = st.secrets["SUMMARY_URL"]

sample_url = """https://mugenlabo-magazine.kddi.com/list/ces2022/
https://routexstartups.com/event-report/event-report-ces-2022-vol2/
https://www.icr.co.jp/newsletter/wtr395-20220225-pkomuro.html
https://www.jetro.go.jp/biznews/2022/01/c84bdeec2511c113.html
https://jbpress.ismedia.jp/articles/-/68461
https://ascii.jp/elem/000/004/080/4080392/
https://www.designnews.com/automotive-engineering/the-hottest-new-cars-of-ces-2022
https://www.counterpointresearch.com/insights/top-10-automotive-announcements-ces-2022/
https://www.digitimes.com/news/a20220105PD200/ces-2022-metaverse.html
https://ja.kardome.com/blog-posts/kardome-partners-with-knowles-demo-voice-recognition-ces
https://jidounten-lab.com/u_33419"""


def get_deepl(sentence, target="en"):
    url = "https://api.deepl.com/v2/translate"
    auth_key = st.secrets["DEEPL_AUTH_KEY"]
    request = "{}?auth_key={}&target_lang={}&text={}".format(
        url, auth_key, target, sentence
    )
    try:
        response = requests.get(request)
        translated_wordtext = json.loads(response.text)["translations"][0]["text"]
    except:
        translated_wordtext = "エラーが発生しました。入力文章を変えてください。"

    return translated_wordtext


def get_summary(url_list, additional_point, get_allsummary):
    url = (
        summary_url
        + "?additional_point="
        + str(additional_point)
        + "&get_allsummary="
        + get_allsummary
        + "&urls="
        + "|".join(url_list)
    )

    r = requests.get(url)
    try:
        return r.json()
    except Exception as e:
        # st.write(e)
        return "エラーが発生しました。"


def summary_main():
    st.write("サマリ対象の記事urlを入力して「サマリ生成」ボタンを押してください。")
    with st.expander("レポート生成対象の記事url入力"):
        input_urls = st.text_area("改行区切りでurl指定", sample_url)

    additional_point = st.text_input(
        "開催概要、注目技術・企業の一般情報以外に、特に抽出したい観点を入力してください。", placeholder="音声認識"
    )

    get_allsummary = st.selectbox("ソース記事の概要を表示しますか？(余分に時間がかかります)", ("no", "yes"))
    exec_summmary = st.button("サマリ生成")

    if exec_summmary:
        time_sta = time.perf_counter()

        url_list = input_urls.split("\n")
        summary_json = get_summary(url_list, additional_point, get_allsummary)

        st.markdown("---")
        st.write("要約生成結果")
        st.markdown(summary_json["answer"])
        st.markdown("---")

        with st.expander("ソース文章の概要"):
            if get_allsummary == "no":
                st.write("省略")
            else:
                sentence = summary_json["allsummary"]
                st.write(get_deepl(sentence, target="ja"))

        with st.expander("要約生成のソース文章"):
            st.write(pd.DataFrame(summary_json["sourceinfo"]))

        time_end = time.perf_counter()
        st.write("処理時間：", time_end - time_sta, "秒")


st.set_page_config(page_title="News", page_icon="📹", layout="wide")
summary_main()
