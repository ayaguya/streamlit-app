import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------- 1. ページ設定 ----------------------------
st.set_page_config(page_title="沖縄県宿泊施設データ可視化", page_icon="🏨", layout="wide")

# ---------------------------- 2. データ読み込み ----------------------------
@st.cache_data
def load_data():
    facilities = pd.read_csv("facilities_long.csv")   # 軒数
    rooms      = pd.read_csv("rooms_long.csv")        # 客室数
    capacity   = pd.read_csv("capacity_long.csv")     # 収容人数
    return facilities, rooms, capacity

facilities, rooms, capacity = load_data()

# ---------------------------- 3. 増減数計算（コピーを取る） ----------------------------
def add_delta(df, col):
    df = df.copy()
    df["増減数"] = df.groupby("市町村")[col].diff().fillna(0).astype(int)
    return df

facilities = add_delta(facilities, "軒数")
rooms      = add_delta(rooms,      "客室数")
capacity   = add_delta(capacity,   "収容人数")

# ---------------------------- 4. 県全体推移グラフ ----------------------------
st.title("沖縄県宿泊施設データ可視化アプリ")
st.header("沖縄県全体の状況")

years_all = [
    1978, 1980, 1982, 1984, 1986, 1988, 1990, 1992, 1994, 1996, 1998, 2000,
    2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
    2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
]
facilities_all = [
    655, 689, 693, 662, 620, 593, 634, 668, 676, 661, 682, 673,
    707, 808, 822, 966, 1022, 1087, 1170, 1232, 1299, 1357, 1411, 1441,
    1541, 1664, 1823, 2082, 2488, 3084, 3342, 3480, 3681, 3914
]
rooms_all = [
    14026, 14428, 15095, 15532, 16254, 17664, 18976, 19864, 22753, 23186,
    23297, 23781, 25423, 27533, 28303, 31238, 32320, 33654, 35005, 36359,
    37050, 38152, 38891, 38905, 40243, 41037, 42248, 45661, 49144, 54380,
    57759, 59448, 63215, 63497
]
capacity_all = [
    36350, 38278, 38904, 40403, 42196, 45696, 48707, 52199, 57990, 57639,
    60345, 60078, 63797, 69344, 71062, 77201, 80746, 82972, 86545, 90066,
    92833, 96954, 99061, 100111, 104724, 107190, 111982, 121403, 132445,
    149216, 160213, 167662, 177191, 184732
]

fig_all = go.Figure()

# 客室数（棒）
fig_all.add_bar(x=years_all, y=rooms_all, name="客室数（室）",
                marker_color="lightblue", yaxis="y1")
# 収容人数（棒）
fig_all.add_bar(x=years_all, y=capacity_all, name="収容人数（人）",
                marker_color="cornflowerblue", yaxis="y1")
# 軒数（折れ線）
fig_all.add_scatter(x=years_all, y=facilities_all, mode="lines+markers",
                    name="軒数（軒）", line=dict(color="darkblue", width=2),
                    marker=dict(size=8), yaxis="y2",
                    hovertemplate="年: %{x}<br>軒数: %{y:,}軒<extra></extra>")

fig_all.update_layout(
    title="沖縄県宿泊施設推移状況",
    xaxis=dict(title="年"),
    # -------- y (右軸：客室数・収容人数) --------
    yaxis=dict(
        title={"text": "客室数・収容人数", "font": {"color": "cornflowerblue"}},
        tickfont=dict(color="cornflowerblue"),
        showgrid=False,
    ),
    # -------- y2 (左軸：軒数) --------
    yaxis2=dict(
        title={"text": "軒数（軒）", "font": {"color": "darkblue"}},
        tickfont=dict(color="darkblue"),
        overlaying="y",
        side="right",
        showgrid=True,
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                xanchor="center", x=0.5),
    hovermode="x unified",
    barmode="stack",
    height=450,
    margin=dict(l=60, r=60, t=80, b=40),
)

st.plotly_chart(fig_all, use_container_width=True)

# ---------------------------- 5. サイドバー選択 ----------------------------
st.sidebar.header("データ選択")
regions_master = ["南部", "中部", "北部", "宮古", "八重山", "離島"]
selected_regions = st.sidebar.multiselect("エリアを選択してください", regions_master)
municipalities = st.sidebar.multiselect(
    "市町村を選択してください",
    options=facilities["市町村"].unique(), default=[]
)
years = st.sidebar.slider("期間を選択してください", 2007, 2023, (2007, 2023))
elements = st.sidebar.multiselect(
    "要素を選択してください", ["軒数", "客室数", "収容人数"], default=["軒数"]
)

# ---------------------------- 6. エリア別グラフ ----------------------------
st.header("エリアの状況")
if selected_regions:
    for element in elements:
        st.subheader(f"選択エリアの{element}の推移")
        fig_r = go.Figure()
        tbl_r = pd.DataFrame()

        src = {"軒数": facilities, "客室数": rooms, "収容人数": capacity}[element]

        for reg in selected_regions:
            df = (src[src["市町村"].str.contains(reg, na=False)  # エリア名を含む行
                   & ~src["市町村"].str.contains("市", na=False)  # 「市」が付く行除外
                   & src["年"].between(years[0], years[1])))
            if not df.empty:
                fig_r.add_scatter(x=df["年"], y=df[element],
                                  mode="lines+markers", name=reg)
                tbl_r = pd.concat([tbl_r,
                                   df.pivot(index="市町村", columns="年",
                                            values=element).fillna(0).astype(int)])

        fig_r.update_layout(
            title=f"選択したエリアの{element}の推移",
            xaxis_title="年", yaxis_title=element,
            legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
            hovermode="x unified", height=400, margin=dict(l=50, r=20, t=60, b=40)
        )
        st.plotly_chart(fig_r, use_container_width=True)

        if not tbl_r.empty:
            st.dataframe(tbl_r.style.format(thousands=","), use_container_width=True)
else:
    st.info("エリアを選択するとグラフが表示されます。")

# ---------------------------- 7. 市町村別グラフ ----------------------------
st.header("市町村の状況")
if municipalities:
    for element in elements:
        df_src = {"軒数": facilities, "客室数": rooms, "収容人数": capacity}[element]
        df_sel = df_src[df_src["市町村"].isin(municipalities)
                        & df_src["年"].between(years[0], years[1])]

        if df_sel.empty:
            continue

        st.subheader(f"{element}の推移")
        fig_c = go.Figure()

        # 最終年の値で並べ替えて見やすく
        order = (df_sel[df_sel["年"] == years[1]]
                 .sort_values(element, ascending=False)["市町村"])

        for city in order:
            d = df_sel[df_sel["市町村"] == city]
            fig_c.add_scatter(x=d["年"], y=d[element],
                              mode="lines+markers", name=city)

        fig_c.update_layout(
            title=f"{element}の推移 ({years[0]}–{years[1]})",
            xaxis_title="年", yaxis_title=element,
            hovermode="x unified", height=400, margin=dict(l=50, r=20, t=60, b=40)
        )
        st.plotly_chart(fig_c, use_container_width=True)

        # テーブル
        tbl_c = (df_sel.pivot(index="市町村", columns="年", values=element)
                 .fillna(0).astype(int))
        st.dataframe(tbl_c.style.format(thousands=","), use_container_width=True)
else:
    st.info("市町村を選択するとグラフが表示されます。")

# ---------------------------- 8. エリア定義と出典 ----------------------------
st.markdown("""---  
### エリアの内訳  
- **南部**: 那覇市、糸満市、豊見城市、八重瀬町、南城市、与那原町、南風原町  
- **中部**: 沖縄市、宜野湾市、浦添市、うるま市、読谷村、嘉手納町、北谷町、北中城村、中城村、西原町  
- **北部**: 名護市、国頭村、大宜味村、東村、今帰仁村、本部町、恩納村、宜野座村、金武町  
- **宮古**: 宮古島市、多良間村  
- **八重山**: 石垣市、竹富町、与那国町  
- **離島**: 久米島町、渡嘉敷村、座間味村、粟国村、渡名喜村、南大東村、北大東村、伊江村、伊平屋村、伊是名村  
---
本データは、[沖縄県宿泊施設実態調査](https://www.pref.okinawa.jp/shigoto/kankotokusan/1011671/1011816/1003416/1026290.html) を基に独自に集計・加工したものです。  
""")
