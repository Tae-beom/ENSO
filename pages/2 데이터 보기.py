# -*- coding: utf-8 -*-
"""
데이터 보기 (옵션 A: 페이지는 중앙 정렬, 콘텐츠는 내부 왼쪽 정렬)
- 드롭다운: ONI / SOI / OLR
- 카드 설명: 선택 즉시 표시
- 차트 + 슬라이더: 시점 이동 시 점선/정보 패널 갱신
- 상태 색상: 결과 문구에 '엘니뇨/라니뇨/라니냐/양의 편차/음의 편차'를 컬러로 강조
"""

import os
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ─────────────────────────────────────────────────────────────
# 0) 페이지 전역 설정 (파일 최상단, 첫 st 호출이어야 함)
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="ENSO 데이터 보기", layout="wide")

# ─────────────────────────────────────────────────────────────
# 1) 전역 CSS (옵션 A: 페이지 중앙 정렬 + 공통 폭)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* 페이지 컨테이너: 중앙 정렬 */
  .block-container {
    max-width: 1200px !important;
    margin: 0 auto !important;      /* ⬅ 가운데 정렬 */
    padding: 50px 16px 0 !important;
  }
  /* components.html(iFrame) 폭은 항상 100% */
  [data-testid="stIFrame"] { width: 100% !important; }

  /* 카드 스타일(조금 더 컴팩트) */
  .enso-card {
    border: 1px solid #e6e8eb; border-radius: 10px;
    padding: 10px 12px; background: #fff;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06); margin-top: 6px;
    width: 550px; /* 카드 너비(원하면 조절) */
  }
  .enso-card .title {
    display:flex; align-items:center; gap:6px;
    font-weight:700; font-size:16px; margin-bottom:4px;
  }
  .enso-badge {
    display:inline-block; padding:1px 6px; border-radius:999px;
    font-size:10px; font-weight:700; color:#0b1220;
    background:#f2f4f7; border:1px solid #e6e8eb;
  }
  .enso-body { line-height:1.45; font-size:15px; color:#0b1220; }
  .enso-body b, .enso-body strong { color: inherit; }
  .enso-hl-red, .enso-hl-red b, .enso-hl-red strong { color:#c62828 !important; font-weight:700; }
  .enso-hl-blue, .enso-hl-blue b, .enso-hl-blue strong { color:#1565c0 !important; font-weight:700; }
  .enso-muted { color:#5f6b7a; font-size:11px; margin-top:6px; }
</style>
""", unsafe_allow_html=True)

st.header("📊 데이터 보기")

# ─────────────────────────────────────────────────────────────
# 2) 카드 설명 데이터 & 렌더
# ─────────────────────────────────────────────────────────────
DESC = {
    "ONI 지수": {
        "badge": "SST Anomaly",
        "icon": "🌊",
        "lines": [
            "엘니뇨 감시 구역의 해수면 온도 편차(관측값-평년값)를 나타내는 지수입니다.",            
            "<b><span class='enso-hl-red'>+0.5°C 이상</b>이면 <span class='enso-hl-red'>엘니뇨</span>, ",
            "<b><span class='enso-hl-blue'>-0.5°C 이하</b>이면 <span class='enso-hl-blue'>라니냐</span>로 분류합니다.",
        ],
        "note": "단위: °C (편차)"
    },
    "SOI 지수": {
        "badge": "Tahiti − Darwin SLP",
        "icon": "🌀",
        "lines": [
            "타히티(중앙 태평양)와 다윈(서태평양)의 해면기압 차를 표준화한 지수입니다.",
            "<b><span class='enso-hl-red'>-0.7 이하</b>는 <span class='enso-hl-red'>엘니뇨</span>, ",
            "<b><span class='enso-hl-blue'>+0.7 이상</b>은 <span class='enso-hl-blue'>라니냐</span>로 분류합니다.",
            "(기압 차 → 무역풍 세기 변화와 관련됩니다.)"
        ],
        "note": "단위: 표준화 지수"
    },
    "OLR 지수": {
        "badge": "Outgoing Longwave Radiation",
        "icon": "☀️",
        "lines": [
            "중앙 태평양의 적외선 복사량(OLR) 편차(관측값-평년값)를 표준화한 지수입니다.",
            "적외선 복사량(OLR)은 <b>대류 활동</b>을 나타냅니다.",           
            "<b><span class='enso-hl-red'>음수</b>값은 구름/대류가 강하고(<span class='enso-hl-red'> ⇒ 엘니뇨</span>) ",
            "<b><span class='enso-hl-blue'>양수</b>값은 구름/대류가 약합니다.(<span class='enso-hl-blue'> ⇒ 라니냐</span>)"           
        ],
        "note": "단위: 표준화 지수"
    }
}

def render_index_card(selected: str):
    d = DESC.get(selected)
    if not d:
        st.warning(f"'{selected}' 설명이 준비되지 않았습니다.")
        return
    body_html = "<br>".join(d["lines"])
    st.markdown(
        f"""
        <div class="enso-card">
          <div class="title">
            <span style="font-size:16px">{d['icon']}</span>
            <span>{selected}</span>
            <span class="enso-badge">{d['badge']}</span>
          </div>
          <div class="enso-body">{body_html}</div>
          <div class="enso-muted">{d['note']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 상단 컨트롤: 좌(드롭다운) / 우(카드)
left, right = st.columns([1, 1.4])
with left:
    index_name = st.selectbox("지수 선택", ["ONI 지수", "SOI 지수", "OLR 지수"], index=0)
with right:
    render_index_card(index_name)

# ─────────────────────────────────────────────────────────────
# 3) 데이터 로더 (서로 다른 스키마를 공통 포맷으로)
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_any_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

def wide_to_long_ym(df: pd.DataFrame) -> pd.DataFrame:
    up = df.copy()
    up.columns = [c.strip().upper() for c in up.columns]
    if "YEAR" not in up.columns:
        raise ValueError("YEAR 컬럼이 없습니다.")
    month_cols = [m for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"] if m in up.columns]
    if not month_cols:
        raise ValueError("월(JAN..DEC) 컬럼을 찾지 못했습니다.")
    long_df = up.melt(id_vars=["YEAR"], value_vars=month_cols, var_name="MON_ABBR", value_name="VAL")
    long_df["VAL"] = pd.to_numeric(long_df["VAL"], errors="coerce")
    long_df.loc[long_df["VAL"].isin([-999.9, -99.9, 999, 999.9]), "VAL"] = pd.NA
    from calendar import month_abbr
    abbr_to_num = {m.upper(): i for i, m in enumerate(month_abbr) if m}
    long_df["MON"] = long_df["MON_ABBR"].map(lambda x: abbr_to_num.get(str(x).upper(), None))
    long_df["Date"] = pd.to_datetime(dict(year=long_df["YEAR"], month=long_df["MON"], day=1), errors="coerce")
    out = long_df.dropna(subset=["Date","VAL"]).sort_values("Date").reset_index(drop=True)
    out = out.rename(columns={"VAL":"VALUE"})
    return out[["Date","VALUE"]]

def load_index(index_name: str):
    if index_name == "ONI 지수":
        path = "data/elnino_data.csv"
        if not os.path.exists(path):
            st.error("ONI 파일이 없습니다: data/elnino_data.csv"); st.stop()
        df = load_any_csv(path)
        need = {"YR", "MON", "DATA"}
        if missing := (need - set(df.columns)):
            st.error(f"ONI 컬럼 누락: {', '.join(missing)}"); st.stop()
        df = df.dropna(subset=["DATA"]).copy()
        df["YR"] = pd.to_numeric(df["YR"], errors="coerce").astype("Int64")
        df["MON"] = pd.to_numeric(df["MON"], errors="coerce").astype("Int64")
        df = df.dropna(subset=["YR","MON"]).copy()
        df["YearMonth"] = pd.to_datetime(df["YR"].astype(int).astype(str) + "-" + df["MON"].astype(int).astype(str), errors="coerce")
        df = df.dropna(subset=["YearMonth"]).sort_values("YearMonth").reset_index(drop=True)
        df["VALUE"] = pd.to_numeric(df["DATA"], errors="coerce")
        thr_pos, thr_neg = 0.5, -0.5
        def classify(v):
            if v >= thr_pos: return "엘니뇨", "red"
            if v <= thr_neg: return "라니냐", "blue"
            return "중립", "black"
        df["상태"], df["색"] = zip(*df["VALUE"].apply(classify))
        meta = dict(title="ONI", yaxis="SST anomalies (°C)")
        return df[["YearMonth","VALUE","상태","색"]], meta

    if index_name == "SOI 지수":
        path_candidates = ["data/soi_data.csv", "/mnt/data/soi_data.csv"]
        path = next((p for p in path_candidates if os.path.exists(p)), None)
        if not path: st.error("SOI 파일을 찾지 못했습니다."); st.stop()
        df = load_any_csv(path)
        date_col = next((c for c in df.columns if c.lower()=="date"), None)
        val_col  = next((c for c in df.columns if c.strip().lower() in ["soi","value","data"]), None)
        if date_col and val_col:
            df = df.dropna(subset=[date_col, val_col]).copy()
            df["YearMonth"] = pd.to_datetime(df[date_col], errors="coerce")
            df["VALUE"] = pd.to_numeric(df[val_col], errors="coerce")
            df = df.dropna(subset=["YearMonth","VALUE"]).sort_values("YearMonth").reset_index(drop=True)
        else:
            wide = wide_to_long_ym(df)
            wide["YearMonth"] = pd.to_datetime(wide["Date"], errors="coerce")
            wide["VALUE"] = pd.to_numeric(wide["VALUE"], errors="coerce")
            df = wide.dropna(subset=["YearMonth","VALUE"]).sort_values("YearMonth").reset_index(drop=True)
        thr_pos, thr_neg = 0.7, -0.7  # 요청 반영
        def classify(v):
            if v <= thr_neg: return "엘니뇨", "red"
            if v >= thr_pos: return "라니냐", "blue"
            return "중립", "black"
        df["상태"], df["색"] = zip(*df["VALUE"].apply(classify))
        meta = dict(title="SOI", yaxis="SOI (std.)")
        return df[["YearMonth","VALUE","상태","색"]], meta

    if index_name == "OLR 지수":
        path = "data/olr_data.csv"
        if not os.path.exists(path): st.error("OLR 파일이 없습니다: data/olr_data.csv"); st.stop()
        df = load_any_csv(path)
        date_col = next((c for c in df.columns if c.lower()=="date"), None)
        val_col  = next((c for c in df.columns if c.strip().lower() in ["olr","value","data","soi"]), None)
        if date_col and val_col:
            df = df.dropna(subset=[date_col, val_col]).copy()
            df["YearMonth"] = pd.to_datetime(df[date_col], errors="coerce")
            df["VALUE"] = pd.to_numeric(df[val_col], errors="coerce")
            df = df.dropna(subset=["YearMonth","VALUE"]).sort_values("YearMonth").reset_index(drop=True)
        else:
            wide = wide_to_long_ym(df)
            wide["YearMonth"] = pd.to_datetime(wide["Date"], errors="coerce")
            wide["VALUE"] = pd.to_numeric(wide["VALUE"], errors="coerce")
            df = wide.dropna(subset=["YearMonth","VALUE"]).sort_values("YearMonth").reset_index(drop=True)
        thr = 1.0
        def classify(v):
            if v >= thr: return "양의 편차 ⇒ 라니냐", "blue"
            if v <= -thr: return "음의 편차 ⇒ 엘니뇨", "red"
            return "중립", "black"
        df["상태"], df["색"] = zip(*df["VALUE"].apply(classify))
        meta = dict(title="OLR", yaxis="OLR (anomaly)")
        return df[["YearMonth","VALUE","상태","색"]], meta

    st.error("알 수 없는 지수 선택입니다."); st.stop()

df, meta = load_index(index_name)

# ─────────────────────────────────────────────────────────────
# 4) 차트 + 슬라이더 (옵션 A 중앙 컨테이너 + 내부 왼쪽 정렬)
# ─────────────────────────────────────────────────────────────
ymin = float(df["VALUE"].min()) - 0.2
ymax = float(df["VALUE"].max()) + 0.2

tmp = df.assign(YR=df["YearMonth"].dt.year, MON=df["YearMonth"].dt.month)
ticks = tmp[(tmp["MON"] == 1) & (tmp["YR"] % 5 == 0)]["YearMonth"]
tick_dates = ticks.dt.strftime("%Y-%m-%d").tolist()
tick_texts = [str(d.year) for d in ticks]

dates_js = json.dumps(df["YearMonth"].dt.strftime("%Y-%m-%d").tolist(), ensure_ascii=False)
vals_js  = json.dumps(df["VALUE"].round(3).astype(float).tolist(), ensure_ascii=False)
state_js = json.dumps(df["상태"].tolist(), ensure_ascii=False)
color_js = json.dumps(df["색"].tolist(), ensure_ascii=False)
tick_dates_js = json.dumps(tick_dates, ensure_ascii=False)
tick_texts_js = json.dumps(tick_texts, ensure_ascii=False)

init_idx = len(df) - 1
init_date = df["YearMonth"].iloc[init_idx].strftime("%Y-%m-%d")

# 중앙 컨테이너 + 내부 왼쪽 정렬
W_MAX = 1050  # 중앙 컨테이너 최대폭
html = f"""
<div id="chartWrap"
     style="max-width:{W_MAX}px; width:100%; margin:0 auto; position:relative; text-align:left;">
  <!-- 차트 (width:100%로 부모폭 채움) -->
  <div id="chart" style="width:100%; height:460px; margin:0; padding:0;"></div>

  <!-- 슬라이더 (플롯폭과 정렬) -->
  <div id="sliderWrap" style="position:relative; height:58px; margin-top:0;">
    <input type="range" id="monthSlider" min="0" max="{len(df)-1}" value="{init_idx}"
           style="position:absolute; left:53px; width:910px;">
  </div>

  <!-- 결과 패널 -->
  <div id="info" style="text-align:left; font-size:16px; margin-top:8px;"></div>
</div>

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
  const dates  = {dates_js};
  const vals   = {vals_js};
  const states = {state_js};
  const colors = {color_js};

  const tickDates = {tick_dates_js};
  const tickTexts = {tick_texts_js};
  const yMin = {ymin};
  const yMax = {ymax};

  // 상태별 색(결과 문구용) - 슬라이더 아래 텍스트에 확실히 적용
  function stateColor(name) {{
    if (name === '엘니뇨' || name === '양의 편차') return '#c62828';
    if (name === '라니냐' || name === '음의 편차') return '#1565c0';
    return '#0b1220';
  }}

  const lineTrace = {{
    x: dates, y: vals, mode: 'lines', name: '{meta["title"]}',
    line: {{color: 'dodgerblue', width: 2}}
  }};

  const vlineTrace = {{
    x: ['{init_date}', '{init_date}'], y: [yMin, yMax], mode: 'lines',
    line: {{color: 'red', dash: 'dot', width: 2}},
    hoverinfo: 'skip', showlegend: false
  }};

  const layout = {{
    margin: {{l: 60, r: 60, t: 10, b: 60}},
    height: 460,
    xaxis: {{
      title: 'Year', tickmode: 'array', tickvals: tickDates, ticktext: tickTexts
    }},
    yaxis: {{
      title: '{meta["yaxis"]}', range: [yMin, yMax]
    }},
    template: 'simple_white',
    shapes: [
      {{ type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y', y0: 0, y1: 0,
         line: {{color: 'gray', width: 1, dash: 'dot'}} }}
    ]
  }};

  Plotly.newPlot('chart', [lineTrace, vlineTrace], layout, {{responsive:true}}).then(() => {{
    syncSliderToPlot();
    document.getElementById('chart').on('plotly_relayout', syncSliderToPlot);
    window.addEventListener('resize', syncSliderToPlot);
    // 초기 안정화(두 번 계산)
    requestAnimationFrame(() => syncSliderToPlot());
    setTimeout(syncSliderToPlot, 0);
  }});

  const slider = document.getElementById('monthSlider');
  const info   = document.getElementById('info');

  function update(idx) {{
    const date  = dates[idx];
    const val   = vals[idx];
    const state = states[idx];
    const color = colors[idx];

    // 점선 이동(두번째 트레이스)
    Plotly.restyle('chart', {{ x: [[date, date]], y: [[yMin, yMax]] }}, [1]);

    const valStr = (val >= 0 ? '+' : '') + Number(val).toFixed(2);
    const [year, month] = date.split('-');

    const stateHtml = "<span style='color:" + color + "; font-weight:700'>" + state + "</span>";

    info.innerHTML = "📅 " + year + "년 " + String(parseInt(month)) + "월 "
                   + "{meta['title']}: "
                   + "<span style='color:" + color + "'><b>" + valStr + "</b></span>"
                   + " → " + stateHtml;
  }}

  function syncSliderToPlot() {{
    const chart   = document.getElementById('chart');
    const host    = document.getElementById('sliderWrap');
    const bg = chart.querySelector('.cartesianlayer .bg');
    if (!bg) return;

    const bbox    = bg.getBoundingClientRect();
    const hostBox = host.getBoundingClientRect();

    // 플롯 영역 폭/좌표에 맞춰 슬라이더 정렬
    slider.style.width = (bbox.width) + 'px';
    slider.style.left  = (bbox.left - hostBox.left) + 'px';
    slider.style.top   = (bbox.bottom - hostBox.top + 10) + 'px';
  }}

  slider.addEventListener('input', e => update(+e.target.value));
  update({init_idx});
</script>
"""

# 중앙 컨테이너 안에 삽입
components.html(html, width=1200, height=700)
