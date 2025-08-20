import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title="엘니뇨 & 라니냐 학습 앱", layout="wide")
st.set_page_config(page_title="엘니뇨 & 라니냐 학습 앱", layout="wide")

# ✅ 본문 폭 넓히고, iFrame이 컨테이너 안에서 가로를 꽉 채우도록
st.markdown("""
<style>
.block-container { max-width: 1200px !important; }   /* 본문 최대폭 늘리기 */
[data-testid="stIFrame"] { width: 100% !important; } /* iFrame 가로 꽉 채우기 */
</style>
""", unsafe_allow_html=True)
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
# 2. 시뮬레이션 보기  ← 여기 전부 교체
# ----------------------
elif menu == "시뮬레이션 보기":
    st.header("🌐 무역풍/용승/수온약층 · 워커순환 시뮬레이션")

    html_code = """
<!-- ▼ 큰 드롭다운 UI: 캔버스 위, 가운데 정렬 -->
<div style="width:700px; margin:8px auto 10px auto; text-align:center; position:relative;">

  <!-- 드롭다운 박스 -->
  <select id="modeSelect"
    style="
      width: 350px;
      height: 54px;
      font-family: Arial;
      font-size: 28px;
      font-weight: 800;
      text-align: center;
      color: #111;
      background: #fff;
      border: 2px solid #2a4a7f;
      border-radius: 10px;
      box-shadow: 0 3px 10px rgba(0,0,0,0.08);
      padding: 0 64px 0 24px;
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      outline: none;
      cursor: pointer;
      margin-bottom: 12px;  /* 캔버스와 간격 */
    ">
    <option value="엘니뇨">엘니뇨</option>
    <option value="평상시" selected>평상시</option>
    <option value="라니냐">라니냐</option>
  </select>

  <!-- 파란 ▼ 아이콘 (select 위에 겹침) -->
  <div style="
      position:absolute;
      right:190px; /* 드롭다운 오른쪽 정렬 */
      top:17px;
      width:0; height:0;
      border-left:14px solid transparent;
      border-right:14px solid transparent;
      border-top:20px solid #3a66b7;
      pointer-events:none;
    ">
  </div>

  <!-- 캔버스 -->
  <canvas id="myCanvas" width="700" height="430" style="border:1px solid #ccc;"></canvas>
</div>

<script>
const canvas = document.getElementById("myCanvas");
const ctx = canvas.getContext("2d");

/* ========== 모드 상태 ========== */
let currentMode = "평상시";
document.getElementById("modeSelect").addEventListener("change", (e) => {
  currentMode = e.target.value;
  // 모드 바뀔 때, 구름 위치도 모드에 맞게 갱신하고 비 파티클을 재초기화
  const p = getModeParams(currentMode);
  cloudX = p.cloudX;  // 구름 기준 좌표(중앙)
  cloudY = p.cloudY;
  initRain(cloudX, cloudY);
});

/* =========================
   공용 화살표 그리기 함수
   - (변경) lineWidthOpt 추가: 라니냐에서 워커 화살표 두께 ↑ 위해
   ========================= */
function drawArrow(fromX, fromY, toX, toY, color, lineWidthOpt) {
  const headLength = 10;
  const dx = toX - fromX;
  const dy = toY - fromY;
  const angle = Math.atan2(dy, dx);

  ctx.beginPath();
  ctx.moveTo(fromX, fromY);
  ctx.lineTo(toX, toY);
  ctx.strokeStyle = color;
  ctx.lineWidth = (typeof lineWidthOpt === 'number') ? lineWidthOpt : 3;  // ★ 두께 옵션
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(toX, toY);
  ctx.lineTo(
    toX - headLength * Math.cos(angle - Math.PI / 6),
    toY - headLength * Math.sin(angle - Math.PI / 6)
  );
  ctx.lineTo(
    toX - headLength * Math.cos(angle + Math.PI / 6),
    toY - headLength * Math.sin(angle + Math.PI / 6)
  );
  ctx.lineTo(toX, toY);
  ctx.fillStyle = color;
  ctx.fill();
}

/* =========================
   일정 길이 화살표(중심+방향)
   - (변경) lineWidthOpt 전달
   ========================= */
function drawArrowCentered(cx, cy, dirX, dirY, totalLen, color, lineWidthOpt) {
  const len = Math.hypot(dirX, dirY) || 1;
  const ux = dirX / len, uy = dirY / len;

  const headLen = 12;                 // 화살촉 길이
  const tailLen = totalLen - headLen; // 몸통+꼬리

  // 꼬리/몸통 비율
  const fromX = cx - ux * tailLen * 0.6;
  const fromY = cy - uy * tailLen * 0.6;
  const toX   = cx + ux * tailLen * 0.4;
  const toY   = cy + uy * tailLen * 0.4;

  drawArrow(fromX, fromY, toX, toY, color, lineWidthOpt);  // ★ 두께 전달
}

/* =========================
   구름 + 비(애니메이션 파티클)
   (구름 좌표 cloudX, cloudY 기준으로 생성/재생성)
   ========================= */
function drawCloud(x, y, bob=0) {
  ctx.fillStyle = "#eeeeee"; // 밝은 회색 구름

  // 윗부분
  ctx.beginPath();
  ctx.arc(x, y + bob, 15, 0, Math.PI * 2);
  ctx.arc(x + 20, y + bob, 20, 0, Math.PI * 2);
  ctx.arc(x - 20, y + bob, 20, 0, Math.PI * 2);
  ctx.arc(x, y - 10 + bob, 20, 0, Math.PI * 2);
  ctx.fill();

  // 아랫부분(몽실몽실 추가)
  ctx.beginPath();
  ctx.arc(x - 15, y + 15 + bob, 18, 0, Math.PI * 2);
  ctx.arc(x + 15, y + 15 + bob, 18, 0, Math.PI * 2);
  ctx.arc(x, y + 18 + bob, 20, 0, Math.PI * 2);
  ctx.fill();
}

const RAIN_COUNT = 20;
let rainDrops = [];

/* ▶ 구름 기준 좌표(초기값: 평상시 서태평양쪽, 네가 쓰던 위치 그대로) */
let cloudX = 95;
let cloudY = 45;

/* 빗방울 초기화: 구름 아래에서 생성되도록 변경 */
function initRain(cx, cy) {
  rainDrops = [];
  for (let i=0; i<RAIN_COUNT; i++) {
    rainDrops.push({
      x: cx - 20 + Math.random()*40,   // 구름 폭 주변
      y: cy + 10 + Math.random()*20,   // 구름 바로 아래
      vx: -0.6,                        // 약간 왼쪽 기울기(바람 표현)
      vy: 2 + Math.random()*1.5,       // 낙하 속도
      len: 14 + Math.random()*8        // 빗줄기 길이
    });
  }
}

/* 빗방울 업데이트/그리기 (해수면에 닿으면 구름 아래에서 재생성) */
function updateAndDrawRain() {
  ctx.strokeStyle = "rgba(30,100,255,0.55)";
  ctx.lineWidth = 2;
  for (let d of rainDrops) {
    ctx.beginPath();
    ctx.moveTo(d.x, d.y);
    ctx.lineTo(d.x + d.vx*6, d.y + d.len);
    ctx.stroke();
    d.x += d.vx;
    d.y += d.vy;
    if (d.y > 138) { // 해수면 근처에서 재생성
      d.x = cloudX - 20 + Math.random()*40;
      d.y = cloudY + 10 + Math.random()*20;
      d.vx = -0.6;
      d.vy = 2 + Math.random()*1.5;
      d.len = 14 + Math.random()*8;
    }
  }
}

/* =========================
   모드별 파라미터 정의
   (thermocline, SST 띠, 용승, 구름 위치, 워커경로/크기/두께)
   ========================= */
function getModeParams(mode) {
  if (mode === "엘니뇨") {
    /* 엘니뇨:
       1) 용승 약화 → 화살표 머리(끝) 아래쪽(큰 y)으로, 꼬리 위치는 그대로
       2) 수온약층 기울기 축소 + 반대로 약간 기울임(서쪽 얕고, 동쪽 깊음)
       3) 동쪽 수온약층 깊이와 용승 화살표 머리 y를 일치시킴
       4) SST 띠: 서쪽 파랑(음), 중앙 밝은회색, 동쪽 빨강(양)
       6) 워커 순환 반시계(동쪽 상승, 서쪽 하강), 크기 70%
       7) 구름 위치: 동태평양 쪽
    */
    const westY = 240;   // 수온약층(서쪽) y
    const eastY = 270;   // 수온약층(동쪽) y — 평상시보다 더 깊음(큰 y)
    const upwellTail = { x: 660, y: 300 }; // 꼬리(고정)
    const upwellHeadY = eastY;             // 화살표 머리 y를 수온약층 y에 맞춤

    return {
      thermo: { west: {x:0, y:westY}, east: {x:700, y:eastY} },
      // SST 띠 그라데이션(엘니뇨: 파랑-회색-빨강)
      sstStops: [
        {pos:0.0, color:"blue"},
        {pos:0.4, color:"#f5f5f5"},
        {pos:0.6, color:"#f5f5f5"},
        {pos:1.0, color:"red"},
      ],
      // 용승 화살표(동쪽): 꼬리 고정, 머리는 수온약층 y까지 낮춤(약화)
      upwelling: { tailX: upwellTail.x, tailY: upwellTail.y, headY: upwellHeadY, color:"#003366" },
      // 구름/비 위치(동쪽으로 이동)
      cloudX: 600, cloudY: 60,
      // 워커 순환(반시계: 동쪽 상승 → 상층 서쪽 → 서쪽 하강 → 표면 동쪽)
      walkerPoints: [
        { x: 600, y: 70 },  // 동쪽 상승 시작
        { x: 600, y: 30 },  // 상층 도달
        { x: 100, y: 30 },  // 상층 동→서
        { x: 100, y: 70 },  // 서쪽 하강 상단
        { x: 100, y: 110 }, // 하강 중간
        { x: 100, y: 115 }, // 표면 도달
        { x: 600, y: 115 }, // 표면 서→동(글씨 위)
        { x: 600, y: 110 }  // 상승 전환
      ],
      walkerScale: 0.7,           // 길이 70%
      walkerLineWidth: 2.2        // 두께도 약간 얇게(선택)
    };
  }

  if (mode === "라니냐") {
    /* 라니냐(요구사항 반영):
       1) 용승 강화 → 화살표 머리가 표층 근처까지 ↑ (y 값 작게, 예: 170)
       2) 수온약층 경사 심화 → 서쪽 더 깊게(y↑=310), 동쪽 더 얕게(y↓=160)
       3) 워커 순환 강화 → 화살표 길이 1.25배, 두께↑
       4) 수온 편차 더 심함 → 중앙 연회색 띠를 서쪽으로 치우침(0.32~0.48),
          양 끝단(서/동)은 더욱 진하게 보이도록 끝단 대비 강화
       ※ 구름: 평상시처럼 서태평양에 유지
    */
    const westY = 310;      // 서쪽 수온약층 y (평상시 300보다 더 깊게)
    const eastY = 160;      // 동쪽 수온약층 y (평상시 200보다 더 얕게)
    const upwellTail = { x: 660, y: 300 }; // 꼬리(고정, 평상시와 동일)
    const upwellHeadY = 170;               // ★ 표층 근처까지 올림(강한 용승)

    return {
      thermo: { west: {x:0, y:westY}, east: {x:700, y:eastY} },
      // SST 띠 그라데이션(라니냐: 빨강-연회색(서쪽으로 치우침)-파랑, 대비 강화)
      sstStops: [
        {pos:0.0, color:"red"},      // 서쪽 끝 더 따뜻(진하게)
        {pos:0.32, color:"#f5f5f5"}, // 중앙 연회색 시작 → 서쪽으로 당김
        {pos:0.48, color:"#f5f5f5"}, // 중앙 연회색 끝
        {pos:1.0, color:"blue"}      // 동쪽 끝 더 차갑게(진하게)
      ],
      // 용승 화살표(동쪽): 강화 → 머리 y를 170까지 올림
      upwelling: { tailX: upwellTail.x, tailY: upwellTail.y, headY: upwellHeadY, color:"#003366" },
      // 구름/비 위치: 평상시와 동일(서태평양 쪽)
      cloudX: 95, cloudY: 45,
      // 워커 순환(강화: 경로는 평상시와 동일, 길이/두께만 강화)
      walkerPoints: [
        { x: 100, y: 70 },
        { x: 100, y: 30 },
        { x: 600, y: 30 },
        { x: 600, y: 70 },
        { x: 600, y: 110 },
        { x: 600, y: 115 },
        { x: 100, y: 115 },
        { x: 100, y: 110 }
      ],
      walkerScale: 1.25,         // ★ 길이 1.25배
      walkerLineWidth: 4          // ★ 두께 증가
    };
  }

  // 기본(평상시) 파라미터 — 네가 쓰던 그림 값 그대로
  return {
    thermo: { west: {x:0, y:300}, east: {x:700, y:200} },
    sstStops: [
      {pos:0.0, color:"red"},
      {pos:0.4, color:"#f5f5f5"},
      {pos:0.6, color:"#f5f5f5"},
      {pos:1.0, color:"blue"},
    ],
    upwelling: { tailX: 660, tailY: 300, headY: 210, color:"#003366" },
    cloudX: 95, cloudY: 45,   // 서태평양 쪽
    walkerPoints: [
      { x: 100, y: 70 },
      { x: 100, y: 30 },
      { x: 600, y: 30 },
      { x: 600, y: 70 },
      { x: 600, y: 110 },
      { x: 600, y: 115 },
      { x: 100, y: 115 },
      { x: 100, y: 110 }
    ],
    walkerScale: 1.0,
    walkerLineWidth: 3
  };
}

/* =========================
   정적 레이어(배경, 라벨 등)
   ========================= */
function drawBase(){
  const P = getModeParams(currentMode);  // 현재 모드 파라미터

  // 바다 배경
  ctx.fillStyle = "#cceeff";
  ctx.fillRect(0, 150, 700, 250);

  // 수온 편차 띠 (모드별 그라데이션 사용)
  let grad = ctx.createLinearGradient(0, 140, 700, 140);
  for (const s of P.sstStops) grad.addColorStop(s.pos, s.color);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 140, 700, 10);

  // 표층 해수 텍스트
  ctx.font = "14px Arial";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  ctx.fillText("표층 해수", 350, 150);

  // Thermocline (수온약층) — 모드별 선분 사용
  ctx.beginPath();
  ctx.moveTo(P.thermo.west.x, P.thermo.west.y);
  ctx.lineTo(P.thermo.east.x, P.thermo.east.y);
  ctx.strokeStyle = "green";  // (요청) 수온약층 선은 초록
  ctx.lineWidth = 3;
  ctx.stroke();

  // 수온약층 라벨(선과 같은 기울기)
  ctx.save();
  const midX = (P.thermo.west.x + P.thermo.east.x)/2;
  const midY = (P.thermo.west.y + P.thermo.east.y)/2;
  const angle = Math.atan2(P.thermo.east.y - P.thermo.west.y,
                           P.thermo.east.x - P.thermo.west.x);
  ctx.translate(midX, midY + 15);
  ctx.rotate(angle);
  ctx.font = "14px Arial";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  ctx.fillText("수온약층", 0, 0);
  ctx.restore();

  // 용승(동쪽 연안) — 화살표 꼬리는 고정, 머리 높이는 모드별
  drawArrow(P.upwelling.tailX, P.upwelling.tailY,
            P.upwelling.tailX, P.upwelling.headY,
            P.upwelling.color);
  ctx.font = "14px Arial";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  ctx.fillText("용승", P.upwelling.tailX, P.upwelling.tailY + 20);

  // 범례 (작은 그라데이션: 모드와 무관 — 필요시 모드별로 바꿔도 됨)
  let legendY = 360;
  let legendGrad = ctx.createLinearGradient(620, legendY, 680, legendY);
  legendGrad.addColorStop(0, "red");
  legendGrad.addColorStop(0.5, "#f5f5f5");
  legendGrad.addColorStop(1, "blue");
  ctx.fillStyle = legendGrad;
  ctx.fillRect(620, legendY, 60, 10);
  ctx.fillStyle = "black";
  ctx.font = "13px Arial";
  ctx.textAlign = "center";
  ctx.fillText("+", 620, legendY - 5);
  ctx.fillText("-", 680, legendY - 5);
  ctx.fillText("수온 편차", 650, legendY + 25);

  // 경도 라벨 (기존 y=410 유지)
  ctx.font = "12px Arial";
  ctx.textAlign = "center";
  ctx.fillStyle = "black";
  let longitudes = ["120°E", "150°E", "180°", "150°W", "120°W"];
  for (let i = 0; i < 5; i++) {
    ctx.fillText(longitudes[i], 80 + i * 140, 410);
  }
}

/* =========================
   워커 순환 애니메이션
   ========================= */
let walkerT = 0;
const walkerStep = 2;           // 프레임당 진행량 (속도 미세조절)
const cycle = 700;              // 한 바퀴 도는 프레임 수
let arrowColor = "#808080";     // 회색 바람 화살표
const baseArrowLenPx = 64;      // 평상시 화살표 길이(px)

// 최초 1회: 평상시 구름 위치로 비 초기화
initRain(cloudX, cloudY);

function animateWalker() {
  // 전체 지우기 → 잔상 제거
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 현재 모드 파라미터
  const P = getModeParams(currentMode);

  // (모드에 따라) 구름 위치 동기화
  cloudX = P.cloudX;
  cloudY = P.cloudY;

  // 정적 레이어
  drawBase();

  // 구름 + 비 (구름은 살짝 흔들림)
  const cloudBob = Math.sin(walkerT * 0.06) * 2;
  drawCloud(cloudX, cloudY, cloudBob);
  updateAndDrawRain();

  // 워커 순환 경로(모드별) + 크기/두께 스케일
  const points = P.walkerPoints;
  const arrowLenPx = baseArrowLenPx * (P.walkerScale ?? 1.0);
  const walkerLineW = (P.walkerLineWidth ?? 3); // ★ 두께

  // 총 길이 계산
  let totalLength = 0;
  const segmentLengths = [];
  for (let i = 0; i < points.length; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % points.length];
    const len = Math.hypot(p2.x - p1.x, p2.y - p1.y);
    segmentLengths.push(len);
    totalLength += len;
  }

  // 동시에 4개의 화살표가 순차 회전
  const phase = (walkerT % cycle) / cycle;
  for (let n = 0; n < 4; n++) {
    let distance = ((phase + n / 4) % 1.0) * totalLength;

    let segment = 0;
    while (distance > segmentLengths[segment]) {
      distance -= segmentLengths[segment];
      segment++;
    }
    const p1 = points[segment];
    const p2 = points[(segment + 1) % points.length];

    const segLen = segmentLengths[segment] || 1;
    const ratio = distance / segLen;

    const cx = p1.x + (p2.x - p1.x) * ratio;
    const cy = p1.y + (p2.y - p1.y) * ratio;

    // ★ 두께를 전달해서 라니냐에서 더 ‘두껍게’ 보이도록
    drawArrowCentered(cx, cy, p2.x - p1.x, p2.y - p1.y, arrowLenPx, arrowColor, walkerLineW);
  }

  walkerT += walkerStep;
  requestAnimationFrame(animateWalker);
}

animateWalker();
</script>
"""
    components.html(html_code, height=520, width=900)

# ----------------------
# 3. 실제 데이터 비교
# ----------------------
elif menu == "실제 데이터 비교":
    st.header("📊 ENSO 지수 (ONI) 분석")

    st.warning("이 섹션은 구현 준비 중입니다. NOAA 데이터 연동 예정입니다.")
