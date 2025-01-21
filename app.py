import os

# 作業ディレクトリを正しい場所に設定
os.chdir('/workspaces/streamlit-app/streamlit-app/')
print("Working Directory Set To:", os.getcwd())
@st.cache_data

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# データの読み込み
@st.cache_data
def load_data():
    facilities = pd.read_csv('facilities_long.csv')  # 軒数データ
    rooms = pd.read_csv('rooms_long.csv')  # 客室数データ
    capacity = pd.read_csv('capacity_long.csv')  # 収容人数データ
    return facilities, rooms, capacity

facilities, rooms, capacity = load_data()

# 増減数の自動計算
def calculate_metrics(data, value_column):
    data['増減数'] = data.groupby('市町村')[value_column].diff().fillna(0).astype(int)
    return data

facilities = calculate_metrics(facilities, '軒数')
rooms = calculate_metrics(rooms, '客室数')
capacity = calculate_metrics(capacity, '収容人数')

# タイトル
st.markdown("<h1>沖縄県宿泊施設データ<br>可視化アプリ</h1>", unsafe_allow_html=True)


# 県の状況
st.header("沖縄県全体の状況")

# 沖縄県全体のデータ
years_all = [
    1978, 1980, 1982, 1984, 1986, 1988, 1990, 1992, 1994, 1996, 1998, 2000,
    2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
    2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
]
facilities_data_all = [
    655, 689, 693, 662, 620, 593, 634, 668, 676, 661, 682, 673,
    707, 808, 822, 966, 1022, 1087, 1170, 1232, 1299, 1357, 1411, 1441,
    1541, 1664, 1823, 2082, 2488, 3084, 3342, 3480, 3681, 3914
]
rooms_data_all = [
    14026, 14428, 15095, 15532, 16254, 17664, 18976, 19864, 22753, 23186,
    23297, 23781, 25423, 27533, 28303, 31238, 32320, 33654, 35005, 36359,
    37050, 38152, 38891, 38905, 40243, 41037, 42248, 45661, 49144, 54380,
    57759, 59448, 63215, 63497
]
capacity_data_all = [
    36350, 38278, 38904, 40403, 42196, 45696, 48707, 52199, 57990, 57639,
    60345, 60078, 63797, 69344, 71062, 77201, 80746, 82972, 86545, 90066,
    92833, 96954, 99061, 100111, 104724, 107190, 111982, 121403, 132445,
    149216, 160213, 167662, 177191, 184732
]

# Plotlyでグラフ作成
fig_all = go.Figure()

# 客室数（棒グラフ）
fig_all.add_trace(go.Bar(
    x=years_all, y=rooms_data_all,
    name='客室数（室）',
    marker_color='lightblue',
    yaxis='y2'
))

# 収容人数（棒グラフ）
fig_all.add_trace(go.Bar(
    x=years_all, y=capacity_data_all,
    name='収容人数（人）',
    marker_color='cornflowerblue',
    yaxis='y2'
))

# 軒数（折れ線グラフ最前面、濃い青色）
fig_all.add_trace(go.Scatter(
    x=years_all, y=facilities_data_all,
    mode='lines+markers',
    name='軒数（軒）',
    line=dict(color='darkblue', width=2),
    marker=dict(size=8),
    yaxis='y1',
    hovertemplate='年: %{x}<br>軒数: %{y:,}軒<extra></extra>'))

# レイアウト設定
fig_all.update_layout(
    title="沖縄県宿泊施設推移状況",
    xaxis=dict(title="年"),
    yaxis=dict(
        title="軒数（軒）",
        titlefont=dict(color="darkblue"),  # 軸名の色を濃い青色に設定
        tickfont=dict(color="darkblue"),  # 目盛りの色を濃い青色に設定
        showgrid=True
    ),
    yaxis2=dict(
        title="客室数・収容人数",
        titlefont=dict(color="cornflowerblue"),
        tickfont=dict(color="cornflowerblue"),
        overlaying="y",
        side="right",
        showgrid=False
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    hovermode="x unified",
    barmode="stack"
)

st.plotly_chart(fig_all, use_container_width=True)

# エリア選択と市町村選択
st.sidebar.header("データ選択")
selected_regions = st.sidebar.multiselect(
    "エリアを選択してください", ["南部", "中部", "北部", "宮古", "八重山", "離島"]
)
municipalities = st.sidebar.multiselect(
    "市町村を選択してください", options=facilities['市町村'].unique(), default=[]
)
years = st.sidebar.slider(
    "期間を選択してください", min_value=2007, max_value=2023, value=(2007, 2023)
)
elements = st.sidebar.multiselect(
    "要素を選択してください", options=["軒数", "客室数", "収容人数"], default=["軒数"]
)

# エリアごとの可視化
st.header("エリアの状況")
if selected_regions:
    for element in elements:
        st.subheader(f"選択エリアの{element}の推移")
        fig_regions = go.Figure()
        region_data_table = pd.DataFrame()

        for region in selected_regions:
            filtered_region = None

            if element == "軒数":
                filtered_region = facilities[(facilities['市町村'].str.contains(region, na=False)) & ~facilities['市町村'].str.contains("市", na=False) & (facilities['年'].between(years[0], years[1]))]
            elif element == "客室数":
                filtered_region = rooms[(rooms['市町村'].str.contains(region, na=False)) & ~rooms['市町村'].str.contains("市", na=False) & (rooms['年'].between(years[0], years[1]))]
            elif element == "収容人数":
                filtered_region = capacity[(capacity['市町村'].str.contains(region, na=False)) & ~capacity['市町村'].str.contains("市", na=False) & (capacity['年'].between(years[0], years[1]))]

            if filtered_region is not None and not filtered_region.empty:
                fig_regions.add_trace(go.Scatter(
                    x=filtered_region['年'],
                    y=filtered_region[element],
                    mode='lines+markers',
                    name=region,
                    line=dict(width=2)
                ))

                table_data = filtered_region.pivot(index='市町村', columns='年', values=element).fillna(0).astype(int)
                region_data_table = pd.concat([region_data_table, table_data])

        fig_regions.update_layout(
            title=f"選択したエリアの{element}の推移",
            xaxis=dict(title="年"),
            yaxis=dict(title=element),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            hovermode="x unified"
        )
        st.plotly_chart(fig_regions, use_container_width=True)

        # データテーブルの表示
        if not region_data_table.empty:
            st.subheader(f"選択エリアの{element}のデータテーブル")
            st.dataframe(region_data_table.style.format(thousands=','), use_container_width=True)
else:
    st.warning("エリアを選択してください。")

# 市町村ごとの可視化
st.header("市町村の状況")
filtered_data = {}
if municipalities:  # 市町村が選択されている場合
    for element in elements:
        filtered_data[element] = None

        if element == "軒数":
            filtered_data[element] = facilities[
                (facilities['市町村'].isin(municipalities)) & 
                (facilities['年'].between(years[0], years[1]))
            ]
        elif element == "客室数":
            filtered_data[element] = rooms[
                (rooms['市町村'].isin(municipalities)) & 
                (rooms['年'].between(years[0], years[1]))
            ]
        elif element == "収容人数":
            filtered_data[element] = capacity[
                (capacity['市町村'].isin(municipalities)) & 
                (capacity['年'].between(years[0], years[1]))
            ]

        if filtered_data[element] is not None and not filtered_data[element].empty:
            st.subheader(f"{element}の推移")
            fig = go.Figure()

            sorted_data = filtered_data[element][filtered_data[element]['年'] == years[1]].sort_values(by=element, ascending=False)
            sorted_cities = sorted_data['市町村'].tolist()

            for city in sorted_cities:
                city_data = filtered_data[element][filtered_data[element]['市町村'] == city]
                fig.add_trace(go.Scatter(x=city_data['年'], y=city_data[element], mode='lines+markers', name=city))

            fig.update_layout(
                title=f"{element}の推移 ({years[0]}-{years[1]})",
                xaxis_title="年",
                yaxis_title=element,
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)

            # データテーブル表示
            table_data = filtered_data[element].pivot(index='市町村', columns='年', values=element).fillna(0).astype(int)
            st.subheader(f"市町村の{element}のデータテーブル")
            st.dataframe(table_data.style.format(thousands=','), use_container_width=True)
else:
    st.warning("市町村を選択してください。")

# エリア内訳の説明をページの下に表示
st.markdown("""
### エリアの内訳
- **南部**: 那覇市、糸満市、豊見城市、八重瀬町、南城市、与那原町、南風原町  
- **中部**: 沖縄市、宜野湾市、浦添市、うるま市、読谷村、嘉手納町、北谷町、北中城村、中城村、西原町  
- **北部**: 名護市、国頭村、大宜味村、東村、今帰仁村、本部町、恩納村、宜野座村、金武町  
- **宮古**: 宮古島市、多良間村  
- **八重山**: 石垣市、竹富町、与那国町  
- **離島**: 久米島町、渡嘉敷村、座間味村、粟国村、渡名喜村、南大東村、北大東村、伊江村、伊平屋村、伊是名村  
""")

# 出典の表示
st.markdown("""
---
データ出典: [沖縄県宿泊施設実態調査](https://www.pref.okinawa.jp/shigoto/kankotokusan/1011671/1011816/1003416/1026290.html)
""")
