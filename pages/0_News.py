from typing import Any
import numpy as np
import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import math
import json
import pandas as pd
import streamlit.components.v1 as components

#from GoogleNews import GoogleNews
from subs.searchnews import extract_google_news
from subs.searchnews import extract_bing_news
from subs.bigQ import get_table
from subs.bigQ import get_taskname_list


#if "searchword" not in st.session_state:
#    st.session_state["searchword"] = "CO2"

#if "google_newsdf" not in st.session_state:
#    st.session_state["google_newsdf"] = pd.DataFrame()

#if "bing_newsdf" not in st.session_state:
#    st.session_state["bing_newsdf"] = pd.DataFrame()

# if "newsapi_df" not in st.session_state:
#    st.session_state["newsapi_df"] = pd.DataFrame()


def get_dates_from_today(n):
    from datetime import datetime, timedelta
    # 現在の日付を取得
    today = datetime.now()
    # 今日からn日前までの日付をyyyymmdd形式で出力する関数
    days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n + 1)]

    # 例として、今日から5日前までの日付を取得
    return "|".join(days)


def news_main() -> None:
    
    with st.sidebar:
        time_op = st.radio("期間指定",options=["直近24時間","直近1週間","直近2週間","直近1ヶ月"])

        time_dic = {"直近24時間":1,"直近1週間":7,"直近2週間":14,"直近1ヶ月":30}
        time_period = get_dates_from_today(time_dic[time_op])

        #format = "%Y-%m-%d"
        #format2 = "%m/%d/%Y"
        #start_d = st.date_input(
        #    "開始日", disabled=False, value=datetime.now() - timedelta(days=20)
        #)
        # st.write(start_d.strftime("%s"))
        #end_d = st.date_input("終了日", disabled=False, value=datetime.now())        

    task_names = get_taskname_list()
    
    with st.expander("スタートアップ新規資金調達情報"):
        fund_task_name_list = st.multiselect("ソース選択",task_names["taskname"].tolist(),default=["vndaily-news","news-asia-technews","fund-eu-startups"],key="fund")
        fund_df = get_table(fund_task_name_list)
        fund_df = fund_df[fund_df["pubdate"].str.contains(time_period)]
        st.dataframe(
            fund_df,
            column_config={
                "url": st.column_config.LinkColumn("url"),
            },
            hide_index=True,
            use_container_width=True
        )
        #components.iframe("https://lookerstudio.google.com/s/qSxFC2WfMzs",height=600)


    with st.expander("IPO,M&A情報"):
        ma_default_list = ["ma-eu-startups","ma-techchurch"]
        ma_task_name_list = st.multiselect("ソース選択",task_names["taskname"].tolist(),default=ma_default_list,key="ma")
        ma_df = get_table(ma_task_name_list)
        ma_df = [ma_df["pubdate"].str.contains(time_period)]
        st.dataframe(
            ma_df,
            column_config={
                "url": st.column_config.LinkColumn("url"),
            },
            hide_index=True,
            use_container_width=True
        )

    with st.expander("関連ニュース"):
        task_name = st.selectbox("カテゴリ選択",["IT","energy","healthcare","material"])
        with st.form("サーチワード指定"):
            if task_name == "IT":
                query = 'AI robotics OR AI semiconductor OR Generative AI OR Lidar OR 3D printing OR AI drone'
            elif task_name == "energy":
                query = 'CO2 recycle OR EV battery OR carbon foot print energy effiency OR hydrogen fuel cell'
            elif task_name == "healthcare":
                query = 'Wearable device OR Femtech Application OR Femtech Platform OR Wellness Application OR Wellness Platform OR Diagnosis Devices OR Medical device AI OR "Healthcare digital platform" OR Healthcare next generation platform'
            elif task_name == "material":
                query = 'Biopolymer OR Synthetic OR Fermentation OR Material recycle OR Semiconductor Material OR Nanotechnology Material OR Metal OR Biomaterial OR Chemical OR construction material OR insulation material OR ammonia OR hydrogen OR magnetic OR cement material'
        
            all_searchword_list = query.split(" OR ")
            searchword_list = st.multiselect("サーチワード選択",all_searchword_list)


            submitted = st.form_submit_button("検索")
            if submitted:        
                gnews_df = extract_google_news(searchword_list,time_op)
                st.write("Googleニュース：{}件hit".format(gnews_df.shape[0]))

                st.dataframe(
                gnews_df,
                column_config={
                    "link": st.column_config.LinkColumn("link"),
                },
                hide_index=True,
                use_container_width=True
                )

                st.markdown("---")

                time1 = "2023-12-01"#start_d
        

                bingnewsdf = extract_bing_news(searchword_list,time1=time1)
                st.write("Bingニュース：{}件hit".format(bingnewsdf.shape[0]))
                st.dataframe(
                    bingnewsdf,
                    column_config={
                        "link": st.column_config.LinkColumn("link"),
                    },
                    hide_index=True,
                )            

            
        


    #st.session_state["searchword"] = task_name
    #st.session_state["google_newsdf"] = gnews_df
    #st.session_state["bingnewsdf"] = bingnewsdf


st.set_page_config(page_title="News", page_icon="📹", layout="wide")
news_main()
