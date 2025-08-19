import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="엘니뇨 & 라니냐 학습 앱", layout="wide")
st.title("🌊 엘니뇨 & 라니냐 시각화 학습 앱")

# 사이드바 메뉴
menu = st.sidebar.radio("메뉴 선택", ["개요 보기", "시뮬레이션 보기", "실제 데이터 비교"])

# ----------------------
# 1. 개요 보기
# ----------------------
if menu == "개요 보기":
    st.header("✅ 엘니뇨와 라니냐란?")

    st.subheader("엘니뇨")
    st.markdown("""
    - 엘니뇨는 적도 태평양의 해수면 온도가 **비정상적으로 높아지는 현상**입니다.
    - 무역풍이 약해지면서 따뜻한 해수가 동쪽으로 이동하고, 이는 전 지구적인 기후 변화로 이어집니다.
    
    예시: 남미에 폭우, 동남아시아에 가뭄
    """)

    st.subheader("라니냐")
    st.markdown("""
    - 라니냐는 해수면 온도가 **평년보다 낮아지는 현상**입니다.
    - 무역풍이 강해져서 서쪽으로 따뜻한 물을 몰아내고, 동쪽에는 찬 물이 솟아오릅니다.
    
    예시: 인도네시아/호주에 폭우, 남미에 가뭄
    """)

    # 이미지 출력 (정상적으로 불러오는 코드)
    try:
        image = Image.open("images/elninolanina.png")
        st.image(image, caption="엘니뇨 & 라니냐 개념도", use_container_width=True)
    except Exception as e:
        st.error("이미지를 불러올 수 없습니다. images/elninolanina.png 경로를 확인하세요.")

# ----------------------
# 2. 시뮬레이션 보기
# ----------------------
elif menu == "시뮬레이션 보기":
    st.header("🌐 무역풍 세기에 따른 해수면 시뮬레이션")

    wind_strength = st.slider("무역풍 세기 (%)", 0, 100, 100, step=10)

    import numpy as np
    x = np.linspace(0, 10, 100)
    y = np.linspace(0, 5, 50)
    X, Y = np.meshgrid(x, y)

    gradient_strength = (100 - wind_strength) / 100
    temp_surface = 28 - (X * gradient_strength)

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=temp_surface,
        x=x,
        y=y,
        colorscale="YlOrRd",
        colorbar=dict(title="Temperature (°C)"),
        showscale=True,
        name="Sea Surface Temperature"
    ))

    arrow_count = 8
    for i in range(arrow_count):
        x0 = 1 + i
        fig.add_annotation(
            x=x0 + 0.5,
            y=4.5,
            ax=x0,
            ay=4.5,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            opacity=wind_strength / 100,
            arrowcolor="blue"
        )

    fig.add_annotation(
        x=0.5, y=1.5,
        ax=0.5, ay=0.0,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=3,
        arrowcolor="green",
        opacity=wind_strength / 100
    )

    fig.update_layout(
        title="해수면 온도 및 무역풍/용승 시뮬레이션",
        xaxis_title="서쪽 (인도네시아) → 동쪽 (남미)",
        yaxis_title="수직 위치 (임의 단위)",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------
# 3. 실제 데이터 비교
# ----------------------
elif menu == "실제 데이터 비교":
    st.header("📊 ENSO 지수 (ONI) 분석")

    st.warning("이 섹션은 구현 준비 중입니다. NOAA 데이터 연동 예정입니다.")
