from typing import Any
import numpy as np
import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import math
import json
import pandas as pd


if "searchword" not in st.session_state:
    st.session_state["searchword"] = "CO2"

if "google_newsdf" not in st.session_state:
    st.session_state["google_newsdf"] = pd.DataFrame()

if "bing_newsdf" not in st.session_state:
    st.session_state["bing_newsdf"] = pd.DataFrame()

if "newsapi_df" not in st.session_state:
    st.session_state["newsapi_df"] = pd.DataFrame()


def abst_main():
    st.write("要約生成対象の記事を選択して「要約生成」ボタンを押してください。")
    google_newsdf = st.session_state["google_newsdf"]
    google_newsdf["check"] = False
    st.data_editor(
        google_newsdf[["check", "title", "link", "datetime", "media"]],
        column_config={
            "check": st.column_config.CheckboxColumn(
                "生成チェック",
                help="要約作成対象の場合はチェック",
                default=False,
            ),
            "link": st.column_config.LinkColumn("link"),
        },
        disabled=["widgets"],
        hide_index=True,
    )

    if st.button("全体要約生成"):
        st.write("生成記事・・・（工事中）")

    if st.button("各記事一行要約生成"):
        st.write("生成記事・・・（工事中）")


st.set_page_config(page_title="News", page_icon="📹", layout="wide")
abst_main()
