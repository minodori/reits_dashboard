import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="운정3지구 준공 일정", page_icon="🏢", layout="wide")

# 로그인 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False


# 로그인 함수
def check_credentials(username, password):
    """Streamlit Secrets에서 인증 정보 확인"""
    try:
        # AttrDict 타입의 st.secrets.users 직접 접근
        # st.secrets.users.user1.username 형식으로 접근
        try:
            users = st.secrets.users

            # user1, user2 등 직접 접근
            for i in range(1, 10):
                user_key = f"user{i}"
                try:
                    # users.user1, users.user2 등 속성 접근
                    if hasattr(users, user_key):
                        user_info = getattr(users, user_key)
                        # user_info.username, user_info.password 접근
                        user_username = getattr(user_info, "username", None)
                        user_password = getattr(user_info, "password", None)
                        if user_username and user_password:
                            if user_username == username and user_password == password:
                                return True
                except (AttributeError, TypeError):
                    continue
        except (AttributeError, KeyError):
            pass

        # 딕셔너리 방식으로도 시도 (하위 호환)
        try:
            users = st.secrets["users"]
            # AttrDict나 딕셔너리 모두 .items() 또는 반복 가능
            if hasattr(users, "items"):
                for user_key, user_info in users.items():
                    # 딕셔너리인 경우
                    if isinstance(user_info, dict):
                        if (
                            user_info.get("username") == username
                            and user_info.get("password") == password
                        ):
                            return True
                    # AttrDict나 객체인 경우 속성 접근
                    else:
                        user_username = getattr(user_info, "username", None)
                        user_password = getattr(user_info, "password", None)
                        if user_username and user_password:
                            if user_username == username and user_password == password:
                                return True
        except (KeyError, AttributeError, TypeError):
            pass

        return False
    except Exception:
        return False


# 로그인 페이지
def show_login():
    """로그인 폼 표시"""
    st.title("🔐 로그인")
    st.markdown("운정3지구 준공 일정 대시보드에 접근하려면 로그인이 필요합니다.")

    with st.form("login_form"):
        username = st.text_input("👤 사용자명", placeholder="사용자명을 입력하세요")
        password = st.text_input(
            "🔑 비밀번호", type="password", placeholder="비밀번호를 입력하세요"
        )

        submitted = st.form_submit_button("로그인", width="stretch")

        if submitted:
            if not username or not password:
                st.error("사용자명과 비밀번호를 모두 입력해주세요.")
                st.session_state.login_attempted = True
            elif check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ 사용자명 또는 비밀번호가 올바르지 않습니다.")
                st.session_state.login_attempted = True
                # 디버깅 정보 (개발 환경)
                with st.expander("🔍 디버깅 정보 (개발자용)", expanded=False):
                    try:
                        st.write("**Secrets 구조 확인:**")
                        if hasattr(st.secrets, "users"):
                            users = st.secrets.users
                            st.write(f"✅ st.secrets.users 발견: {type(users)}")
                            if hasattr(users, "user1"):
                                u1 = users.user1
                                st.write(
                                    f"  - user1.username: {getattr(u1, 'username', 'N/A')}"
                                )
                                st.write(
                                    f"  - user1.password: {'***' if getattr(u1, 'password', None) else 'N/A'}"
                                )
                            if hasattr(users, "user2"):
                                u2 = users.user2
                                st.write(
                                    f"  - user2.username: {getattr(u2, 'username', 'N/A')}"
                                )
                                st.write(
                                    f"  - user2.password: {'***' if getattr(u2, 'password', None) else 'N/A'}"
                                )
                        else:
                            st.write("❌ st.secrets.users를 찾을 수 없습니다.")

                        # 딕셔너리 접근 시도
                        try:
                            users_dict = st.secrets["users"]
                            st.write(f"✅ st.secrets['users'] 발견: {type(users_dict)}")
                            if isinstance(users_dict, dict):
                                for k, v in users_dict.items():
                                    st.write(f"  - {k}: {type(v)}")
                        except:
                            st.write("❌ st.secrets['users'] 접근 실패")
                    except Exception as e:
                        st.write(f"디버깅 오류: {str(e)}")


# 로그인되지 않은 경우 로그인 페이지 표시
if not st.session_state.authenticated:
    show_login()
    st.stop()

# 로그인 성공 후 메인 대시보드 표시
# 로그아웃 버튼
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 로그아웃", width="stretch"):
        st.session_state.authenticated = False
        st.session_state.login_attempted = False
        if "username" in st.session_state:
            del st.session_state.username
        st.rerun()

    if "username" in st.session_state:
        st.caption(f"👤 로그인: {st.session_state.username}")

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
st.plotly_chart(fig1, config={"responsive": True, "displayModeBar": False})

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
st.plotly_chart(fig2, config={"responsive": True, "displayModeBar": False})

# 차트 3: 공공 vs 민간
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏘️ 공공 vs 민간 분양")
    형태별 = df_filtered.groupby("형태")["세대수"].sum().reset_index()

    fig3 = px.pie(
        형태별, values="세대수", names="형태", title="분양 형태별 비율", hole=0.4
    )
    st.plotly_chart(fig3, config={"responsive": True, "displayModeBar": False})

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
    st.plotly_chart(fig4, config={"responsive": True, "displayModeBar": False})

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

st.dataframe(display_df, width="stretch", height=400)

# 다운로드 버튼
csv = display_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 CSV 다운로드",
    data=csv,
    file_name="운정3지구_준공일정.csv",
    mime="text/csv",
)
