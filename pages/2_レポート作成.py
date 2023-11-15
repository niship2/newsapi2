from typing import Any
import numpy as np
import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import math
import json
import pandas as pd
import requests

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


def get_summary(url_list, additional_point):
    url = (
        summary_url
        + "?additional_point="
        + str(additional_point)
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

    if st.button("サマリ生成"):
        url_list = input_urls.split("\n")
        summary_json = get_summary(url_list, additional_point)

        st.markdown("---")
        st.write("要約生成結果")
        st.markdown(summary_json["answer"])

        st.markdown("---")
        with st.expander("要約生成のソース文章"):
            st.write(pd.DataFrame(summary_json["sourceinfo"]))


st.set_page_config(page_title="News", page_icon="📹", layout="wide")
summary_main()
