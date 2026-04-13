<div align="center">

![QuantAgent Banner](assets/banner.png)
<h2>QuantAgent: 가격 기반 멀티 에이전트 LLM 고빈도 트레이딩 시스템</h2>

</div>



<div align="center">

<div style="position: relative; text-align: center; margin: 20px 0;">
  <div style="position: absolute; top: -10px; right: 20%; font-size: 1.2em;"></div>
  <p>
    <a href="https://machineily.github.io/">Fei Xiong</a><sup>1,2 ★</sup>&nbsp;
    <a href="https://wyattz23.github.io">Xiang Zhang</a><sup>3 ★</sup>&nbsp;
    <a href="https://scholar.google.com/citations?user=hFhhrmgAAAAJ&hl=en">Aosong Feng</a><sup>4</sup>&nbsp;
    <a href="https://intersun.github.io/">Siqi Sun</a><sup>5</sup>&nbsp;
    <a href="https://chenyuyou.me/">Chenyu You</a><sup>1</sup>
  </p>
  
  <p>
    <sup>1</sup> Stony Brook University &nbsp;&nbsp; 
    <sup>2</sup> Carnegie Mellon University &nbsp;&nbsp;
    <sup>3</sup> University of British Columbia &nbsp;&nbsp; <br>
    <sup>4</sup> Yale University &nbsp;&nbsp; 
    <sup>5</sup> Fudan University &nbsp;&nbsp; 
    ★ Equal Contribution <br>
  </p>
</div>

<br>
<p align="center">
  <a href="https://arxiv.org/abs/2509.09995">
    <img src="https://img.shields.io/badge/💡%20ArXiv-2509.09995-B31B1B?style=flat-square" alt="Paper">
  </a>
  <a href="https://Y-Research-SBU.github.io/QuantAgent">
    <img src="https://img.shields.io/badge/Project-Website-blue?style=flat-square&logo=googlechrome" alt="Project Website">
  </a>
  <a href="https://github.com/Y-Research-SBU/QuantAgent/blob/main/assets/wechat_0203.jpg">
    <img src="https://img.shields.io/badge/WeChat-Group-green?style=flat-square&logo=wechat" alt="WeChat Group">
  </a>
  <a href="https://discord.gg/t9nQ6VXQ">
    <img src="https://img.shields.io/badge/Discord-Community-5865F2?style=flat-square&logo=discord" alt="Discord Community">
  </a>
</p>

</div>

LangChain과 LangGraph를 활용하여 기술적 지표, 패턴 인식, 추세 분석을 결합한 멀티 에이전트 트레이딩 분석 시스템입니다. 웹 인터페이스와 프로그래밍 방식 모두로 종합 시장 분석을 제공합니다.


<div align="center">

[기능](#-기능) | [설치](#-설치) | [사용법](#-사용법) | [아키텍처](#-아키텍처) | [구현 상세](#-구현-상세) | [기여](#-기여) | [라이선스](#-라이선스)

</div>

## 기능

### 에이전트 파이프라인

```
START → 지표 에이전트 → 패턴 에이전트 → 추세 에이전트 → 결정 에이전트 → END
```

4개의 전문 에이전트가 순차적으로 분석을 수행하며, 공유 상태(`IndicatorAgentState`)를 통해 데이터를 전달합니다. 각 에이전트는 분석 리포트와 함께 **방향(LONG/SHORT/NEUTRAL)** 및 **신뢰도 점수(0-100)**를 출력합니다.

---

### 지표 에이전트 (Indicator Agent)

RSI, MACD, Stochastic, Williams %R, ROC 5개 기술적 지표를 TA-Lib으로 계산하고, 내장된 해석 가이드라인에 따라 각 지표의 의미를 분석합니다.

**해석 기준 내장:**
| 지표 | 과매수 | 과매도 |
|------|--------|--------|
| RSI | > 70 | < 30 |
| Stochastic %K | > 80 | < 20 |
| Williams %R | > -20 | < -80 |

![indicator agent](assets/indicator.png)

### 패턴 에이전트 (Pattern Agent)

16개 클래식 캔들스틱 패턴(역헤드앤숄더, 이중바닥, 상승/하강 삼각형 등)을 인식하고, K-line 차트 이미지를 생성하여 LLM에 시각적 분석을 수행합니다.

![pattern agent](assets/pattern.png)

### 추세 에이전트 (Trend Agent)

지지선/저항선 추세선을 자동 피팅하여 차트에 오버레이하고, 시장 방향성을 분석합니다. 계산된 **지지 가격**과 **저항 가격**은 결정 에이전트에 전달되어 실제 위험/보상 비율 계산에 사용됩니다.

![trend agent](assets/trend.png)

### 결정 에이전트 (Decision Agent)

세 에이전트의 리포트, 방향, 신뢰도를 종합하여 최종 매매 결정을 내립니다.

**핵심 개선 사항:**
- **관망(HOLD) 허용** — 신호가 불충분하면 무리하게 방향을 선택하지 않습니다
- **실제 가격 기반 R/R 계산** — 지지선/저항선에서 산출된 수치 사용 (임의 값 아님)
- **신뢰도 기반 판단** — 평균 신뢰도 40 미만 또는 방향 상충 시 자동 관망

| 관망 조건 | 설명 |
|-----------|------|
| 평균 신뢰도 < 40 | 전체적으로 신호가 약함 |
| 방향 상충 | LONG + SHORT + NEUTRAL 혼재 |
| NEUTRAL 다수 | 2개 이상의 에이전트가 중립 |

![decision agent](assets/decision.png)

### 웹 인터페이스

Flask 기반 웹 애플리케이션:
- Yahoo Finance 실시간 시장 데이터
- 12개 자산 선택 (주식, 암호화폐, 원자재, 지수) + 사용자 정의 자산
- 7개 타임프레임 분석 (1분 ~ 1개월)
- 동적 차트 생성 및 시각화
- 4개 LLM 프로바이더 API 키 관리
- **분석 결과 마크다운 파일 저장** 기능

## 설치

### 1. uv 설치

[uv](https://docs.astral.sh/uv/)가 설치되어 있지 않다면 먼저 설치합니다:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 의존성 설치

```bash
uv sync
```

이 명령으로 Python 3.11 환경 생성과 모든 의존성 설치가 한 번에 완료됩니다.

### TA-Lib 설치 참고

`uv sync` 시 TA-Lib 빌드에 실패하는 경우, 시스템에 TA-Lib C 라이브러리가 먼저 설치되어 있어야 합니다:

```bash
# Ubuntu/Debian
sudo apt-get install -y ta-lib

# macOS
brew install ta-lib

# conda를 통한 설치 (대안)
conda install -c conda-forge ta-lib
```

자세한 설치 방법은 [TA-Lib Python 저장소](https://github.com/ta-lib/ta-lib-python)를 참고하세요.

### 3. LLM API 키 설정

웹 인터페이스의 설정 패널에서 직접 입력하거나, 환경 변수로 설정할 수 있습니다:

![alt text](assets/apibox.png)

```bash
# OpenAI
export OPENAI_API_KEY="your_openai_api_key_here"

# Anthropic (Claude)
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Qwen (DashScope)
export DASHSCOPE_API_KEY="your_dashscope_api_key_here"

# MiniMax (204K 컨텍스트, OpenAI 호환 API)
export MINIMAX_API_KEY="your_minimax_api_key_here"
```

## 사용법

### 웹 인터페이스 실행

```bash
uv run python web_interface.py
```

브라우저에서 `http://127.0.0.1:5000` 으로 접속합니다.

### 웹 인터페이스 기능

1. **자산 선택** — 주식, 암호화폐, 원자재, 지수 중 선택 또는 사용자 정의 심볼 입력
2. **타임프레임 선택** — 1분부터 1개월까지 다양한 간격 지원
3. **날짜/시간 범위** — 원하는 분석 기간을 자유롭게 설정
4. **실시간 분석** — 기술적 지표, 패턴, 추세를 종합한 시각화 제공
5. **LLM 프로바이더 관리** — OpenAI, Anthropic, Qwen, MiniMax 전환 및 API 키 설정
6. **마크다운 저장** — 분석 결과를 `.md` 파일로 다운로드

## 데모

![Quick preview](assets/demo.gif)

## 아키텍처

### 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│                    웹 인터페이스 (Flask)                   │
│  자산 선택 → 데이터 수집 (yfinance) → 분석 실행 → 결과 표시  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              TradingGraph (LangGraph 오케스트레이터)        │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  지표 에이전트 │→│ 패턴 에이전트 │→│ 추세 에이전트 │     │
│  │ RSI, MACD,  │  │ 16개 캔들패턴 │  │ 지지/저항선  │     │
│  │ ROC, Stoch, │  │ 차트 시각분석 │  │ 추세선 피팅  │     │
│  │ Williams %R │  │             │  │             │     │
│  │             │  │             │  │             │     │
│  │ direction + │  │ direction + │  │ direction + │     │
│  │ confidence  │  │ confidence  │  │ confidence  │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         └────────────────┼────────────────┘             │
│                          ▼                              │
│                ┌─────────────────┐                      │
│                │   결정 에이전트   │                      │
│                │                 │                      │
│                │ 신뢰도 합산      │                      │
│                │ 관망 조건 판단   │                      │
│                │ R/R 실제 계산   │                      │
│                │                 │                      │
│                │ → LONG / SHORT  │                      │
│                │   / 관망(HOLD)  │                      │
│                └─────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### 공유 상태 (IndicatorAgentState)

모든 에이전트는 `IndicatorAgentState` TypedDict를 통해 데이터를 주고받습니다:

| 필드 | 설명 |
|------|------|
| `kline_data` | OHLCV 캔들 데이터 |
| `indicator_report` / `direction` / `confidence` | 지표 분석 결과 |
| `pattern_report` / `direction` / `confidence` | 패턴 분석 결과 |
| `trend_report` / `direction` / `confidence` | 추세 분석 결과 |
| `support_price` / `resistance_price` | 추세선 기반 지지/저항 가격 |
| `final_trade_decision` | 최종 매매 결정 (JSON) |

### 동적 데이터 포인트

타임프레임에 따라 분석에 사용되는 데이터 포인트 수가 자동 조정됩니다. MACD(26기간) 등 지표의 워밍업 기간을 고려한 설정입니다.

| 타임프레임 | 데이터 포인트 | 비고 |
|-----------|-------------|------|
| 1m, 5m | 80개 | 노이즈가 많아 더 많은 데이터 필요 |
| 15m | 75개 | |
| 30m, 1h | 70개 | |
| 4h | 65개 | |
| 1d, 1w, 1mo | 60개 | |

## 구현 상세

**중요**: 본 시스템은 이미지 입력이 가능한 LLM이 필요합니다. 패턴 에이전트와 추세 에이전트가 차트 이미지를 생성하여 시각적으로 분석하기 때문입니다.

### Python 코드 사용

```python
from trading_graph import TradingGraph

# 트레이딩 그래프 초기화
trading_graph = TradingGraph()

# 초기 상태 생성
initial_state = {
    "kline_data": your_dataframe_dict,
    "analysis_results": None,
    "messages": [],
    "time_frame": "4hour",
    "stock_name": "BTC"
}

# 분석 실행
final_state = trading_graph.graph.invoke(initial_state)

# 결과 접근
print(final_state.get("final_trade_decision"))  # 최종 결정 (JSON)
print(final_state.get("indicator_report"))       # 지표 리포트
print(final_state.get("indicator_direction"))    # 방향: LONG/SHORT/NEUTRAL
print(final_state.get("indicator_confidence"))   # 신뢰도: 0-100
print(final_state.get("pattern_report"))         # 패턴 리포트
print(final_state.get("trend_report"))           # 추세 리포트
print(final_state.get("support_price"))          # 지지 가격
print(final_state.get("resistance_price"))       # 저항 가격
```

### LLM 프로바이더 설정

웹 인터페이스에서 전환하거나, 코드에서 직접 설정할 수 있습니다:

| 프로바이더 | Agent LLM | Graph LLM |
|-----------|-----------|-----------|
| OpenAI | gpt-4o-mini | gpt-4o |
| Anthropic | claude-haiku-4-5-20251001 | claude-haiku-4-5-20251001 |
| Qwen | qwen3-max | qwen3-vl-plus |
| MiniMax | MiniMax-M2.7 | MiniMax-M2.7 |

### 설정 옵션

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `agent_llm_model` | gpt-4o-mini | 개별 에이전트용 모델 |
| `graph_llm_model` | gpt-4o | 그래프 로직 및 의사결정용 모델 |
| `agent_llm_temperature` | 0.1 | 에이전트 응답 온도 |
| `graph_llm_temperature` | 0.1 | 그래프 로직 온도 |

전체 설정 목록은 `default_config.py`에서 확인할 수 있습니다.

### 프로젝트 파일 구조

| 파일 | 역할 |
|------|------|
| `trading_graph.py` | 메인 오케스트레이터 — LLM 초기화 및 그래프 구성 |
| `graph_setup.py` | LangGraph 노드/엣지 토폴로지 설정 |
| `agent_state.py` | 공유 상태 TypedDict 정의 |
| `indicator_agent.py` | 기술적 지표 계산 및 분석 (해석 가이드라인 내장) |
| `pattern_agent.py` | 캔들스틱 패턴 인식 + 시각 분석 |
| `trend_agent.py` | 추세선 피팅 + 지지/저항 가격 산출 |
| `decision_agent.py` | 종합 판단 — 신뢰도 기반 LONG/SHORT/관망 결정 |
| `agent_utils.py` | 에이전트 출력 파싱 유틸리티 |
| `graph_util.py` | 기술적 분석 도구 (지표 계산, 추세선 알고리즘) |
| `static_util.py` | 차트 생성 (캔들스틱, 추세선 오버레이) |
| `web_interface.py` | Flask 웹 애플리케이션 |
| `default_config.py` | 기본 모델/온도/API 키 설정 |

## 원본 프로젝트 대비 변경 사항

이 포크는 [Y-Research-SBU/QuantAgent](https://github.com/Y-Research-SBU/QuantAgent)를 기반으로 하며, 실제 분석 결과를 검토한 후 발견된 구조적 문제점을 개선하기 위해 다음과 같은 변경을 적용했습니다.

---

### 1. 에이전트 신뢰도 시스템 도입

**문제**: 원본에서는 세 에이전트(지표, 패턴, 추세)가 텍스트 리포트만 반환했습니다. 결정 에이전트는 이 텍스트들을 LLM이 주관적으로 종합하여 판단했기 때문에, 각 에이전트가 얼마나 확신하는지 정량적으로 알 수 없었습니다. 예를 들어 추세 에이전트가 "횡보 확률 45%"라고 했어도, 이것이 최종 결정에 어떤 비중으로 반영되었는지 추적이 불가능했습니다.

**변경**: 각 에이전트가 분석 리포트와 함께 **방향(LONG/SHORT/NEUTRAL)**과 **신뢰도 점수(0-100)**를 구조화된 JSON으로 출력하도록 변경했습니다. 결정 에이전트는 이 수치를 명시적으로 참조합니다.

| 변경 파일 | 내용 |
|-----------|------|
| `agent_state.py` | `indicator_direction/confidence`, `pattern_direction/confidence`, `trend_direction/confidence` 6개 필드 추가 |
| `agent_utils.py` | **신규** — LLM 출력에서 JSON 블록을 파싱하는 공통 유틸리티 |
| `indicator_agent.py` | 프롬프트에 JSON 출력 지시 추가, 리턴에 direction/confidence 포함 |
| `pattern_agent.py` | 동일 |
| `trend_agent.py` | 동일 |

---

### 2. 관망(HOLD) 허용

**문제**: 원본 결정 에이전트의 프롬프트에는 `"⚠️ HOLD is prohibited due to HFT constraints"`라는 제약이 있어, 신호가 아무리 불충분하거나 상충해도 반드시 LONG 또는 SHORT를 출력해야 했습니다. 실제 분석에서 추세 에이전트가 "횡보"를, 패턴 에이전트가 "중립"을 판단해도, 결정 에이전트는 억지로 방향을 선택해야 하므로 신뢰할 수 없는 결정이 나올 수밖에 없었습니다.

**변경**: HOLD 금지를 제거하고, 명확한 관망 조건을 도입했습니다:
- 세 에이전트의 평균 신뢰도가 40 미만인 경우
- 세 에이전트의 방향이 서로 상충하는 경우 (예: LONG + SHORT + NEUTRAL)
- 2개 이상의 에이전트가 NEUTRAL인 경우

| 변경 파일 | 내용 |
|-----------|------|
| `decision_agent.py` | 프롬프트 전면 재작성 — 관망 조건 명시, 3단계 출력(LONG/SHORT/관망) |
| `templates/output.html` | `decision-hold` 배지 스타일 추가, 관망 시 R/R 비율 숨김, 종합 신뢰도 표시 |

---

### 3. 실제 가격 기반 위험/보상(R/R) 비율 계산

**문제**: 원본 프롬프트에는 `"Suggest a reasonable risk-reward ratio between 1.2 and 1.8"`이라는 지시가 있어, LLM이 1.2~1.8 범위에서 임의의 숫자를 고르는 구조였습니다. 실제 가격 수준과 무관한 허수였으며, 예를 들어 실제로는 진입 346, 손절 341, 익절 352라면 R/R은 약 1:1 수준인데도 1.5로 보고되는 식이었습니다.

**변경**: 추세 에이전트가 계산한 지지선/저항선 가격을 결정 에이전트에 전달하여, 실제 현재가 대비 R/R을 사전 계산합니다.

```
LONG R/R = (저항선 - 현재가) / (현재가 - 지지선)
SHORT R/R = (현재가 - 지지선) / (저항선 - 현재가)
```

| 변경 파일 | 내용 |
|-----------|------|
| `agent_state.py` | `support_price`, `resistance_price` 필드 추가 |
| `static_util.py` | `generate_trend_image` 리턴에 지지/저항 가격 포함 |
| `web_interface.py` | 초기 상태에 지지/저항 가격 전달 |
| `decision_agent.py` | 현재가·지지선·저항선으로 R/R 사전 계산 후 프롬프트에 주입 |

---

### 4. 타임프레임별 동적 데이터 포인트

**문제**: 원본에서는 타임프레임과 무관하게 항상 `df.tail(45)`로 45개 데이터 포인트만 사용했습니다. MACD(12,26,9)는 최소 35개의 워밍업 기간이 필요하므로, 45개에서 유효한 MACD 값은 약 10개뿐이었습니다. 또한 1분봉처럼 노이즈가 많은 타임프레임과 일봉처럼 안정적인 타임프레임에 동일한 데이터 양을 적용하는 것은 부적절했습니다.

**변경**: 타임프레임별로 최적의 데이터 포인트 수를 자동 조정합니다.

| 변경 파일 | 내용 |
|-----------|------|
| `web_interface.py` | `_get_data_points_for_timeframe()` 메서드 추가, 하드코딩 `45` → 타임프레임별 60~80 동적 조정 |

---

### 5. 지표 해석 가이드라인 내장

**문제**: 원본 지표 에이전트의 프롬프트에는 각 지표의 해석 기준이 없었습니다. LLM이 자체 지식에만 의존하여 해석하다 보니, Williams %R -11.17을 "극도의 강세"로 해석하는 오류가 발생했습니다. 실제로 -20 이상은 기술적으로 **과매수** 영역이며, 하락 반전 가능성을 경고하는 구간입니다.

**변경**: 프롬프트에 각 지표별 과매수/과매도 임계값과 시그널 해석 기준을 명시했습니다.

| 변경 파일 | 내용 |
|-----------|------|
| `indicator_agent.py` | RSI(70/30), Stochastic(80/20), Williams %R(-20/-80), MACD 크로스오버, ROC 0선 돌파 등 해석 기준 프롬프트에 추가 |

---

### 6. 한국어 UI 및 LLM 출력

**문제**: 원본의 모든 프론트엔드 텍스트와 LLM 프롬프트가 영어로 되어 있어 한국어 사용자에게 불편했습니다.

**변경**:

| 변경 파일 | 내용 |
|-----------|------|
| `templates/demo_new.html` | 전체 UI 텍스트 한국어 번역 (라벨, 버튼, 알림, 에러 메시지) |
| `templates/output.html` | 분석 결과 페이지 전체 한국어 번역 |
| `web_interface.py` | 백엔드 에러 메시지, 자산명 한국어 번역 |
| `indicator_agent.py` | LLM 출력 한국어 지시 |
| `pattern_agent.py` | LLM 출력 한국어 지시 |
| `trend_agent.py` | LLM 출력 한국어 지시 |
| `decision_agent.py` | 전체 프롬프트 한국어 작성, justification 한국어 출력 |

---

### 7. 분석 결과 마크다운 저장

**문제**: 원본에서는 분석 결과를 웹 페이지에서만 확인할 수 있었고, 저장하거나 공유하는 기능이 없었습니다.

**변경**: 분석 완료 후 결과 페이지에서 "마크다운 저장" 버튼을 클릭하면, 전체 분석 리포트를 `.md` 파일로 다운로드할 수 있습니다. 파일에는 자산명, 타임프레임, 최종 결정(방향/신뢰도/R/R/근거), 각 에이전트 리포트 전문이 포함됩니다.

| 변경 파일 | 내용 |
|-----------|------|
| `web_interface.py` | `generate_markdown_report()` 메서드 + `/api/download-report` 엔드포인트 추가 |
| `templates/output.html` | "마크다운 저장" 버튼 + `downloadMarkdownReport()` JS 함수 추가 |

---

### 8. 패키지 관리 시스템 변경

**문제**: 원본은 `conda create` + `pip install -r requirements.txt` 2단계 설치가 필요했고, 환경 재현성이 보장되지 않았습니다.

**변경**: `uv`와 `pyproject.toml` 기반으로 전환하여 `uv sync` 한 줄로 Python 환경 생성부터 의존성 설치까지 완료됩니다. `uv.lock` 파일로 정확한 재현성이 보장됩니다.

---

## 기여

1. 저장소를 포크합니다
2. 기능 브랜치를 생성합니다
3. 변경 사항을 작성합니다
4. 해당하는 경우 테스트를 추가합니다
5. 풀 리퀘스트를 제출합니다

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 인용

```
@article{xiong2025quantagent,
  title={QuantAgent: Price-Driven Multi-Agent LLMs for High-Frequency Trading},
  author={Fei Xiong and Xiang Zhang and Aosong Feng and Siqi Sun and Chenyu You},
  journal={arXiv preprint arXiv:2509.09995},
  year={2025}
}
```

## 감사의 말

이 저장소는 다음 라이브러리 및 프레임워크의 도움으로 구축되었습니다:

- [**LangGraph**](https://github.com/langchain-ai/langgraph)
- [**OpenAI**](https://github.com/openai/openai-python)
- [**Anthropic (Claude)**](https://github.com/anthropics/anthropic-sdk-python)
- [**Qwen**](https://github.com/QwenLM/Qwen)
- [**MiniMax**](https://platform.minimaxi.com/) — 204K 컨텍스트, OpenAI 호환 API
- [**yfinance**](https://github.com/ranaroussi/yfinance)
- [**Flask**](https://github.com/pallets/flask)
- [**TechnicalAnalysisAutomation**](https://github.com/neurotrader888/TechnicalAnalysisAutomation/tree/main)
- [**tvdatafeed**](https://github.com/rongardF/tvdatafeed)

## 면책 조항

이 소프트웨어는 교육 및 연구 목적으로만 제공됩니다. 금융 조언을 제공하기 위한 것이 아닙니다. 투자 결정을 내리기 전에 항상 직접 조사하고 금융 전문가와 상담하는 것을 고려하세요.

## 문제 해결

### 일반적인 문제

1. **TA-Lib 설치** — TA-Lib 설치 문제가 발생하면 [공식 저장소](https://github.com/ta-lib/ta-lib-python)에서 플랫폼별 설치 방법을 확인하세요.

2. **LLM API 키** — 환경 변수 또는 웹 인터페이스를 통해 API 키가 올바르게 설정되었는지 확인하세요.

3. **데이터 수집** — Yahoo Finance를 사용합니다. 일부 심볼은 사용할 수 없거나 제한된 과거 데이터만 가질 수 있습니다.

4. **메모리 문제** — 대용량 데이터셋의 경우 분석 기간을 줄이거나 더 작은 타임프레임을 사용해 보세요.

### 지원

문제가 발생하면:

0. 페이지를 새로고침하고 LLM API 키를 다시 입력해 보세요
1. 위의 문제 해결 섹션을 확인하세요
2. 콘솔의 오류 메시지를 검토하세요
3. 모든 의존성이 올바르게 설치되었는지 확인하세요
4. API 키가 유효하고 크레딧이 충분한지 확인하세요

## 연락처

질문, 피드백, 또는 협업 기회에 대해서는 아래로 연락해 주세요:

원저자
**이메일**: [chenyu.you@stonybrook.edu](mailto:chenyu.you@stonybrook.edu), [siqisun@fudan.edu.cn](mailto:siqisun@fudan.edu.cn)

수정저자
**이메일**: [rtlink.park@gmail.com](mailto:rtlink.park@gmail.com), 

