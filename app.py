import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="운정3지구 준공 일정", page_icon="🏢", layout="wide")

# 제목
st.title("🏢 운정3지구 준공 일정")
st.markdown("---")


# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_excel("공급일정.xlsx", sheet_name="운정")
    # 날짜 컬럼 변환
    df["분양"] = pd.to_datetime(df["분양"])
    df["준공"] = pd.to_datetime(df["준공"])
    df["전매"] = pd.to_datetime(df["전매"])
    return df


df = load_data()

# 사이드바 필터
st.sidebar.header("🔍 필터")

# 형태 필터
형태_선택 = st.sidebar.multiselect(
    "분양 형태", options=df["형태"].unique(), default=df["형태"].unique()
)

# 시공사 필터
시공사_선택 = st.sidebar.multiselect(
    "시공사", options=df["시공사"].unique(), default=df["시공사"].unique()
)

# 필터 적용
df_filtered = df[(df["형태"].isin(형태_선택)) & (df["시공사"].isin(시공사_선택))]

# 주요 지표
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("총 단지 수", f"{df_filtered['단지'].nunique()}개")

with col2:
    st.metric("총 세대수", f"{df_filtered['세대수'].sum():,}세대")

with col3:
    공공_비율 = (
        df_filtered[df_filtered["형태"] == "공공 분양"]["세대수"].sum()
        / df_filtered["세대수"].sum()
        * 100
    )
    st.metric("공공분양 비율", f"{공공_비율:.1f}%")

with col4:
    평균_면적 = df_filtered["면적"].mean()
    st.metric("평균 면적", f"{평균_면적:.1f}㎡")

st.markdown("---")

# 차트 1: 준공 시기별 세대수 (히트맵 대신 바 차트)
st.subheader("📅 단지별 준공 일정")

# 준공 월별 집계
df_pivot = (
    df_filtered.groupby(["단지", pd.Grouper(key="준공", freq="ME")])["세대수"]
    .sum()
    .reset_index()
)
df_pivot["준공_월"] = df_pivot["준공"].dt.strftime("%Y.%m")

fig1 = px.bar(
    df_pivot,
    x="준공_월",
    y="세대수",
    color="단지",
    title="월별 준공 세대수",
    labels={"준공_월": "준공 시기", "세대수": "세대수"},
    height=400,
)
st.plotly_chart(fig1, width="stretch")

# 차트 2: 분기별 준공 물량
st.subheader("📊 분기별 준공 물량")

df_filtered["분기"] = df_filtered["준공"].dt.to_period("Q").astype(str)
분기별 = df_filtered.groupby("분기")["세대수"].sum().reset_index()

fig2 = px.bar(
    분기별,
    x="분기",
    y="세대수",
    title="분기별 총 세대수",
    labels={"분기": "분기", "세대수": "세대수"},
    color="세대수",
    color_continuous_scale="Reds",
)
st.plotly_chart(fig2, use_container_width=True)

# 차트 3: 공공 vs 민간
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏘️ 공공 vs 민간 분양")
    형태별 = df_filtered.groupby("형태")["세대수"].sum().reset_index()

    fig3 = px.pie(
        형태별, values="세대수", names="형태", title="분양 형태별 비율", hole=0.4
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🏗️ 시공사별 세대수")
    시공사별 = (
        df_filtered.groupby("시공사")["세대수"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )

    fig4 = px.bar(
        시공사별,
        x="세대수",
        y="시공사",
        orientation="h",
        title="시공사별 세대수",
        color="세대수",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig4, use_container_width=True)

# 전체 데이터 테이블
st.subheader("📋 전체 데이터")

# 표시할 컬럼만 선택
display_df = df_filtered[
    [
        "단지",
        "블럭",
        "형태",
        "분양",
        "준공",
        "전매",
        "시행사",
        "시공사",
        "면적",
        "세대수",
    ]
].copy()

# 날짜 포맷 변경
display_df["분양"] = display_df["분양"].dt.strftime("%Y-%m-%d")
display_df["준공"] = display_df["준공"].dt.strftime("%Y-%m-%d")
display_df["전매"] = display_df["전매"].dt.strftime("%Y-%m-%d")

st.dataframe(display_df, use_container_width=True, height=400)

# 다운로드 버튼
csv = display_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 CSV 다운로드",
    data=csv,
    file_name="운정3지구_준공일정.csv",
    mime="text/csv",
)
