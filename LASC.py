import streamlit as st
import os
from collections import OrderedDict
import numpy as np
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup as bs
import lxml.etree as xml
import lxml


st.markdown('<h1 style="text-align: center;">研究室配属スコア計算機 </h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; width: 700px;">（LASC : Laboratory Assignment Score Calculator）</h3>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center;">(v1.0.0-release1, Made by StoicJHS')</h4>', unsafe_allow_html=True)
st.markdown('')

st.markdown('*成績公開ごとにアプリが機能しなくなる可能性があり、アップデートで対処します。')

st.markdown('')

st.markdown('このアプリは、東京工業大学理学院物理学系の研究室配属のためのスコア計算を目的に制作されました。 研究室配属に使われる **「専門科目得点」** とは、「**(専門科目GPA)** x **（履修申告した対象授業科目の単位数）**」=「**履修した専門科目GPの総和**」のことであります。  ただし、100番台科目は含まず、他学系開講の専門科目も含めません（2023年4月13日付通知ずみ）。')

st.markdown('')
st.markdown('')

st.markdown('<h3 style="text-align: left; width: 700px;">・使い方</h3>', unsafe_allow_html=True)
st.markdown('1. 東工大ポータルでログインし、「教務Webシステム」の「成績閲覧」に入ってください。')


st.image("https://raw.githubusercontent.com/StoicJHS/Test/main/1.PNG", caption='「成績閲覧」の状態の画面', width=500)


st.markdown('2. その状態で、「ctrl + s」を入力し、htmlファイルをダウンロードしてください。')
st.markdown('（ブラウザーのページダウンロード機能を用いても大丈夫です。）')

st.image("https://raw.githubusercontent.com/StoicJHS/Test/main/2.PNG", caption='「成績閲覧」の状態の画面', width=500)


st.markdown('3. 「Browse files」をクリックして、先程のhtmlファイルをアップロードしてください。')

st.markdown('')
st.markdown('****アップロードが完了すると、直ちに計算結果が表示されます。**')
st.markdown('****アップロードされたファイルはローカルディレクトリにあるので、プライバシーが保護されています。**')


# adding file uploading function
uploaded_file = st.file_uploader("htmlファイルをアップロード", type=["html"])

if uploaded_file is not None:
    # read the uploaded file as a dataframe
    content = uploaded_file.read()
    soup = bs(content, "lxml")

    t1 = []
    get = []

    results = soup.find_all(class_="tableSet01 resultUnit")
    Senmon = soup.find_all(id="ctl00_ContentPlaceHolder1_ctl01_resultUnit_120900_grid")
    Senmon_table = Senmon[0]

    Senmon_tr = Senmon_table.find_all("tr")

    for j in range(len(Senmon_tr)):
        test1 = Senmon_tr[j]
        Kaku1 = test1.find_all("td")

        for i in range(0,len(Kaku1)):
            puri1 = Kaku1[i]
            h1 = puri1.get_text()
            h1_text = h1.strip()
            t1.append(h1_text)

    tanisu = []
    score = []
    gp = []

    cleaned_t1 = []

    for string in t1:
        cleaned_string = string.replace('\n', '')
        cleaned_string_split = cleaned_string.split('                    ')
        cleaned_t1.extend(cleaned_string_split)

    data = [cleaned_t1[i:i+10] for i in range(0,len(cleaned_t1),10)]
    df = pd.DataFrame(data)

    df = df.drop(df.columns[[2, 3]], axis=1)


    new_columns = {0: '推奨', 1: '科目コード', 4: '授業科目名', 5: '授業担当教員', 6: '単位', 7: '成績', 8: 'Q', 9: '修得時期'}  # 여기서는 원하는 인덱스를 직접 지정

    df = df.rename(columns=new_columns)

    df = df.reset_index(drop=True)

    df_target_first = df[df['科目コード'].str.contains("PHY.")]
    df_target = df_target_first[df_target_first['成績'] != '-']

    def process_data(row):
        values = row['単位'].split('-')
        new_value = sum(int(value) for value in values)
        return new_value

    def score_to_gp(score):
        if score >= 60:
            return (score - 55) / 10
        else:
            return 0

    df_target['総合単位数'] = df_target.apply(process_data, axis=1)
    df_target['gp'] = df_target['成績'].astype(int).apply(score_to_gp)
    df_target['Lab_Score_EA'] = df_target['総合単位数']*df_target['gp']
    df_target.drop(columns=['授業担当教員', 'Q', '修得時期'], inplace=True)
    total_lab_score = df_target['Lab_Score_EA'].sum()

    headers = df_target.columns

    st.write(df_target)
    st.markdown('<h3 style="text-align: left; width: 700px;">計算結果（研究室配属スコア）</h3>', unsafe_allow_html=True)
    st.write('### スコア : ',total_lab_score)
    
    
 
