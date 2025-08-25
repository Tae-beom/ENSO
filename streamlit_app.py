# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
from utils import inject_css

# 각 페이지에서도 CSS 재사용 가능(선택)
inject_css(max_width_px=1200)


st.header("✅ 엘니뇨와 라니냐란?")


st.subheader("엘니뇨(a)")
st.markdown(
"""
- 엘니뇨는 **동태평양의 해수면 온도**가 **평년보다 높아지는 현상**입니다.
- **무역풍**이 **약**해지면서 따뜻한 해수가 동쪽으로 이동하고, 이는 전 지구적인 기후 변화로 이어집니다.
(예: 남미에 폭우, 동남아시아에 가뭄 등)
"""
)


st.subheader("라니냐(c)")
st.markdown(
"""
- 라니냐는 **동태평양의 해수면 온도**가 **평년보다 낮아지는 현상**입니다.
- **무역풍**이 **강**해져서 서쪽으로 따뜻한 물을 몰아내고, 동쪽에는 찬 물이 솟아오릅니다.
(예: 인도네시아/호주에 폭우, 남미에 가뭄 등)
"""
)


# 이미지 출력
try:
    image = Image.open("images/elninolanina.png")
    st.image(image, caption="엘니뇨 & 라니냐 개념도", use_container_width=True)
except FileNotFoundError:
    st.error("이미지를 찾을 수 없습니다. images/elninolanina.png 경로를 확인하세요.")
except Exception as e:
    st.error(f"이미지를 불러오는 중 오류가 발생했습니다: {e}")
