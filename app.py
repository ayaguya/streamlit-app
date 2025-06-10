import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------
# ページ設定
# -------------------------------------------------
st.set_page_config(
    page_title="沖縄県宿泊施設データ可視化",
    page_icon="🏨",
    layout="wide"
)

# -------------------------------------------------
# データ読み込み
# -------------------------------------------------
@st.cache_data
def load_data():
    try:
        facilities = pd.read_csv("facilities_long.csv")
        rooms      = pd.read_csv("rooms_long.csv")
        capacity   = pd.read_csv("capacity_long.csv")
        return facilities, rooms, capacity
    except FileNotFoundError:
        st.error(
            "CSV ファイルが見つかりません。\n"
            "facilities_long.csv / rooms_long.csv / capacity_long.csv が "
            "同じディレクトリにあることを確認してください。"
        )
        st.stop()

facilities, rooms, capacity = load_data()

# -------------------------------------------------
# 増減数を計算（キャッシュ品を汚染しないよう copy()）
# -------------------------------------------------
def calculate_metrics(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df["増減数"] = (
        df.groupby("市町村")[col]
          .diff()
          .fillna(0)
          .astype(int)
    )
    return df

facilities = calculate_metrics(facilities, "軒数")
rooms      = calculate_metrics(rooms,      "客室数")
capacity   = calculate_metrics(capacity,   "収容人数")

# -------------------------------------------------
# 画面タイトル
# -------------------------------------------------
st.title("🏨 沖縄県宿泊施設データ可視化アプリ")
st.markdown("---")

# -------------------------------------------------
# サイドバー
# -------------------------------------------------
st.sidebar.header("📊 データ選択")

regions = ["南部", "中部", "北部", "宮古", "八重山", "離島"]
municipalities = sorted([
    m for m in facilities["市町村"].unique()
    if m not in regions and m != "沖縄県"
])

selected_regions = st.sidebar.multiselect(
    "エリアを選択してください", regions, default=[]
)
selected_municipalities = st.sidebar.multiselect(
    "市町村を選択してください", municipalities, default=[]
)
years = st.sidebar.slider(
    "期間を選択してください",
    int(facilities["年"].min()),
    int(facilities["年"].max()),
    value=(2007, 2023)
)
elements = st.sidebar.multiselect(
    "要素を選択してください",
    ["軒数", "客室数", "収容人数"],
    default=["軒数"]
)

# -------------------------------------------------
# 沖縄県全体の状況
# -------------------------------------------------
st.header("📈 沖縄県全体の状況")

okinawa_facilities = facilities[facilities["市町村"] == "沖縄県"].sort_values("年")
okinawa_rooms      = rooms[rooms["市町村"] == "沖縄県"].sort_values("年")
okinawa_capacity   = capacity[capacity["市町村"] == "沖縄県"].sort_values("年")

if not okinawa_facilities.empty:
    latest_year       = okinawa_facilities["年"].max()
    latest_facilities = okinawa_facilities.loc[
        okinawa_facilities["年"] == latest_year, "軒数"
    ].iat[0]
    latest_rooms      = okinawa_rooms.loc[
        okinawa_rooms["年"] == latest_year, "客室数"
    ].iat[0]
    latest_capacity   = okinawa_capacity.loc[
        okinawa_capacity["年"] == latest_year, "収容人数"
    ].iat[0]

    # ---------- メトリクス ----------
    c1, c2, c3 = st.columns(3)
    c1.metric("総施設数（2023年）", f"{latest_facilities:,} 軒")
    c2.metric("総客室数（2023年）", f"{latest_rooms:,} 室")
    c3.metric("総収容人数（2023年）", f"{latest_capacity:,} 人")

    # ---------- グラフ ----------
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 客室数
    fig.add_trace(
        go.Bar(
            x=okinawa_rooms["年"],
            y=okinawa_rooms["客室数"],
            name="客室数（室）",
            marker_color="lightblue",
            opacity=0.7,
        ),
        secondary_y=False,
    )

    # 収容人数
    fig.add_trace(
        go.Bar(
            x=okinawa_capacity["年"],
            y=okinawa_capacity["収容人数"],
            name="収容人数（人）",
            marker_color="cornflowerblue",
            opacity=0.7,
        ),
        secondary_y=False,
    )

    # 軒数
    fig.add_trace(
        go.Scatter(
            x=okinawa_facilities["年"],
            y=okinawa_facilities["軒数"],
            mode="lines+markers",
            name="軒数（軒）",
            line=dict(color="darkblue", width=3),
            marker=dict(size=8),
        ),
        secondary_y=True,
    )

    # レイアウト
    fig.update_xaxes(title_text="年")
    fig.update_yaxes(title_text="客室数・収容人数", secondary_y=False)
    fig.update_yaxes(title_text="軒数（軒）",       secondary_y=True)
    fig.update_layout(
        title=dict(text="沖縄県宿泊施設推移状況", x=0.5, xanchor="center"),
        hovermode="x unified",
        height=500,
        margin=dict(l=60, r=30, t=80, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# エリア別可視化
# -------------------------------------------------
if selected_regions:
    st.header("🗺️ エリア別の状況")

    for element in elements:
        st.subheader(f"選択エリアの {element} の推移")

        # データソース選択
        data_source = {
            "軒数": facilities,
            "客室数": rooms,
            "収容人数": capacity,
        }[element]

        fig = go.Figure()
        for reg in selected_regions:
            reg_df = (
                data_source[
                    (data_source["市町村"] == reg)
                    & (data_source["年"].between(years[0], years[1]))
                ]
                .sort_values("年")
            )
            if not reg_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=reg_df["年"],
                        y=reg_df[element],
                        mode="lines+markers",
                        name=reg,
                        line=dict(width=3),
                    )
                )

        fig.update_layout(
            title=f"{years[0]}-{years[1]} 年：選択エリアの {element} 推移",
            xaxis_title="年",
            yaxis_title=element,
            hovermode="x unified",
            height=400,
            margin=dict(l=50, r=20, t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# 市町村別可視化
# -------------------------------------------------
if selected_municipalities:
    st.header("🏘️ 市町村別の状況")

    for element in elements:
        st.subheader(f"選択市町村の {element} の推移")

        data_source = {
            "軒数": facilities,
            "客室数": rooms,
            "収容人数": capacity,
        }[element]

        fig = go.Figure()
        for mun in selected_municipalities:
            mun_df = (
                data_source[
                    (data_source["市町村"] == mun)
                    & (data_source["年"].between(years[0], years[1]))
                ]
                .sort_values("年")
            )
            if not mun_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=mun_df["年"],
                        y=mun_df[element],
                        mode="lines+markers",
                        name=mun,
                        line=dict(width=3),
                    )
                )

        fig.update_layout(
            title=f"{years[0]}-{years[1]} 年：選択市町村の {element} 推移",
            xaxis_title="年",
            yaxis_title=element,
            hovermode="x unified",
            height=400,
            margin=dict(l=50, r=20, t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        # データテーブル（任意表示）
        if st.checkbox(f"{element} のデータテーブルを表示", key=element):
            tbl = (
                data_source[
                    (data_source["市町村"].isin(selected_municipalities))
                    & (data_source["年"].between(years[0], years[1]))
                ]
                .pivot(index="市町村", columns="年", values=element)
                .fillna(0)
                .astype(int)
            )
            st.dataframe(tbl.style.format(thousands=","), use_container_width=True)

# -------------------------------------------------
# エリア定義の説明
# -------------------------------------------------
st.markdown("---")
st.header("🗾 エリアの内訳")

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        "**南部**: 那覇市、糸満市、豊見城市、八重瀬町、南城市、与那原町、南風原町  \n"
        "**中部**: 沖縄市、宜野湾市、浦添市、うるま市、読谷村、嘉手納町、北谷町、北中城村、中城村、西原町  \n"
        "**北部**: 名護市、国頭村、大宜味村、東村、今帰仁村、本部町、恩納村、宜野座村、金武町"
    )
with col2:
    st.markdown(
        "**宮古**: 宮古島市、多良間村  \n"
        "**八重山**: 石垣市、竹富町、与那国町  \n"
        "**離島**: 久米島町、渡嘉敷村、座間味村、粟国村、渡名喜村、南大東村、北大東村、伊江村、伊平屋村、伊是名村"
    )

# -------------------------------------------------
# データ出典
# -------------------------------------------------
st.markdown("---")
st.markdown(
    "本データは、[沖縄県宿泊施設実態調査]"
    "(https://www.pref.okinawa.jp/shigoto/kankotokusan/1011671/1011816/"
    "1003416/1026290.html) を基に独自に集計・加工したものです。"
)
