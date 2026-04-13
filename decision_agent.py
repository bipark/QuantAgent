"""
Agent for making final trade decisions in high-frequency trading (HFT) context.
Combines indicator, pattern, and trend reports to issue a LONG, SHORT, or HOLD order.
"""


def create_final_trade_decider(llm):
    """
    Create a trade decision agent node. The agent uses LLM to synthesize indicator, pattern, and trend reports
    and outputs a final trade decision (LONG, SHORT, or 관망) with justification and risk-reward ratio.
    """

    def trade_decision_node(state) -> dict:
        indicator_report = state["indicator_report"]
        pattern_report = state["pattern_report"]
        trend_report = state["trend_report"]
        time_frame = state["time_frame"]
        stock_name = state["stock_name"]

        # --- Agent confidence and direction ---
        indicator_direction = state.get("indicator_direction", "NEUTRAL")
        indicator_confidence = state.get("indicator_confidence", 50)
        pattern_direction = state.get("pattern_direction", "NEUTRAL")
        pattern_confidence = state.get("pattern_confidence", 50)
        trend_direction = state.get("trend_direction", "NEUTRAL")
        trend_confidence = state.get("trend_confidence", 50)

        avg_confidence = (indicator_confidence + pattern_confidence + trend_confidence) / 3

        # --- Price levels for R/R calculation ---
        support_price = state.get("support_price")
        resistance_price = state.get("resistance_price")
        kline_data = state.get("kline_data", {})
        closes = kline_data.get("Close", [])
        current_price = closes[-1] if closes else None

        # Build price level section
        price_section = ""
        if current_price and support_price and resistance_price:
            long_reward = resistance_price - current_price
            long_risk = current_price - support_price
            short_reward = current_price - support_price
            short_risk = resistance_price - current_price

            long_rr = round(long_reward / long_risk, 2) if long_risk > 0 else 0
            short_rr = round(short_reward / short_risk, 2) if short_risk > 0 else 0

            price_section = f"""
            ### 💰 가격 수준 정보:
            - 현재가: {current_price:.2f}
            - 지지선: {support_price:.2f}
            - 저항선: {resistance_price:.2f}

            LONG의 경우 R/R = (저항선 - 현재가) / (현재가 - 지지선) = {long_rr}
            SHORT의 경우 R/R = (현재가 - 지지선) / (저항선 - 현재가) = {short_rr}

            위 계산된 R/R 비율을 사용하세요. 임의로 숫자를 선택하지 마세요.
            관망인 경우 risk_reward_ratio는 null로 출력하세요.
            """
        else:
            price_section = """
            ### 💰 가격 수준 정보:
            지지선/저항선 데이터를 사용할 수 없습니다. 리포트 내용을 기반으로 R/R 비율을 추정하세요.
            """

        # --- System prompt for LLM ---
        prompt = f"""당신은 {stock_name}의 {time_frame} K-line 차트를 분석하는 고빈도 정량 트레이딩(HFT) 분석가입니다.

            당신의 임무는 **LONG**, **SHORT**, 또는 **관망(HOLD)** 중 하나의 실행 명령을 내리는 것입니다.

            예측 대상은 **다음 N개 캔들스틱**의 가격 움직임입니다:
            - 예시: 타임프레임 = 15분, N = 1 → 다음 15분 예측
            - 예시: 타임프레임 = 4시간, N = 1 → 다음 4시간 예측

            ---

            ### 📊 에이전트 신뢰도 요약:
            - 지표 분석: {indicator_direction} (신뢰도: {indicator_confidence}/100)
            - 패턴 분석: {pattern_direction} (신뢰도: {pattern_confidence}/100)
            - 추세 분석: {trend_direction} (신뢰도: {trend_confidence}/100)
            - **평균 신뢰도: {avg_confidence:.1f}/100**

            ---

            ### ⛔ 관망(HOLD) 조건 — 다음 중 하나라도 해당하면 관망을 선택하세요:
            1. 평균 신뢰도가 **40 미만**인 경우
            2. 세 에이전트의 direction이 **서로 상충**하는 경우 (예: LONG + SHORT + NEUTRAL)
            3. 세 에이전트 중 2개 이상이 **NEUTRAL**인 경우
            4. 확인된 신호 없이 추측에 의존해야 하는 경우

            무리하게 방향을 선택하지 마세요. 근거가 불충분하면 "관망"이 가장 정직한 답입니다.

            ---

            ### 1. 기술적 지표 리포트:
            - 모멘텀(MACD, ROC)과 오실레이터(RSI, Stochastic, Williams %R)를 평가하세요.
            - MACD 크로스오버, RSI 다이버전스, 극단적 과매수/과매도 등 **강한 방향성 시그널**에 높은 가중치를 부여하세요.
            - 중립적이거나 혼합된 시그널은 여러 지표가 합치하지 않는 한 **무시 또는 가중치 하향**하세요.

            ### 2. 패턴 리포트:
            - 강세/약세 패턴에 기반해 행동하려면:
              - 패턴이 **명확히 인식 가능하고 거의 완성**되었어야 하며,
              - **돌파 또는 붕괴가 이미 진행 중**이거나 매우 높은 확률이어야 합니다.
            - 초기 단계나 투기적 패턴에는 **행동하지 마세요**.

            ### 3. 추세 리포트:
            - 가격이 지지선/저항선과 어떻게 상호작용하는지 분석하세요.
            - 추세선 사이에서 압축되고 있다면, 강한 캔들이나 지표 확인이 있을 때만 돌파를 예측하세요.
            - **기하학적 구조만으로 돌파 방향을 가정하지 마세요**.

            ---

            ### ✅ 결정 전략

            1. **확인된** 시그널에만 행동하세요 — 신흥, 투기적, 상충하는 시그널은 피하세요.
            2. 세 리포트가 **같은 방향으로 합치**하는 경우를 우선시하세요.
            3. 리포트가 불일치하면: **더 강하고 최근에 확인된** 방향을 선택하되, 불일치가 심하면 관망하세요.

            {price_section}

            ---
            ### 🧠 출력 형식 (JSON, 시스템 파싱용):

            ```json
            {{{{
            "forecast_horizon": "다음 N개 캔들스틱 예측 (시간 단위 명시)",
            "decision": "LONG 또는 SHORT 또는 관망",
            "justification": "근거 요약 (한국어)",
            "risk_reward_ratio": "계산된 float 값 또는 null (관망 시)",
            "combined_confidence": {avg_confidence:.1f}
            }}}}
            ```

            --------
            **기술적 지표 리포트**
            {indicator_report}

            **패턴 리포트**
            {pattern_report}

            **추세 리포트**
            {trend_report}

            ---
            ⚠️ 전체 응답(justification 포함)을 반드시 한국어로 작성하세요. JSON 키와 decision 값(LONG/SHORT/관망)만 그대로 유지하세요.
        """

        # --- LLM call for decision ---
        response = llm.invoke(prompt)

        return {
            "final_trade_decision": response.content,
            "messages": [response],
            "decision_prompt": prompt,
        }

    return trade_decision_node
