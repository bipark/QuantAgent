# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuantAgent is a multi-agent trading analysis system that uses LLMs (OpenAI, Anthropic, Qwen, MiniMax) with LangChain/LangGraph to perform technical indicator analysis, candlestick pattern recognition, trendline analysis, and trading decision synthesis. Based on research paper arXiv:2509.09995.

## Development Setup

```bash
# Environment (Python 3.11 required)
conda create -n quantagents python=3.11
conda activate quantagents

# Dependencies
pip install -r requirements.txt
# TA-Lib often needs conda install:
conda install -c conda-forge ta-lib

# Or with uv:
uv sync
```

## Running

```bash
# Web interface (Flask, runs on http://127.0.0.1:5000)
python web_interface.py
```

## Testing

```bash
# Tests are in tests/ directory
python -m pytest tests/
python -m pytest tests/test_minimax_provider.py  # single test file
```

## Architecture

The system is a **4-agent LangGraph pipeline** that processes OHLCV candlestick data sequentially:

```
Indicator Agent → Pattern Agent → Trend Agent → Decision Agent
```

### Agent Pipeline

- **Indicator Agent** (`indicator_agent.py`): Computes 5 technical indicators (RSI, MACD, ROC, Stochastic, Williams %R) via TA-Lib
- **Pattern Agent** (`pattern_agent.py`): Recognizes 16 candlestick patterns, generates K-line chart images for LLM visual analysis
- **Trend Agent** (`trend_agent.py`): Fits support/resistance trendlines, analyzes market direction
- **Decision Agent** (`decision_agent.py`): LLM synthesizes all agent reports into LONG/SHORT decision with risk-reward ratio

### Core Modules

- `trading_graph.py` — Main orchestrator: initializes LLMs, toolkits, and the LangGraph agent system
- `graph_setup.py` — Graph topology: creates agent nodes and wires sequential edges
- `agent_state.py` — Shared state definition (`IndicatorAgentState` TypedDict) flowing through the graph
- `graph_util.py` — Technical analysis toolkit: indicator calculations and trendline fitting algorithms
- `static_util.py` — Chart generation: candlestick and trendline-annotated charts via matplotlib/mplfinance
- `default_config.py` — Default LLM model names, temperatures, and API key placeholders

### LLM Provider System

Four providers supported, each with model config in `default_config.py`:
- **OpenAI** (gpt-4o, gpt-4o-mini) — default
- **Anthropic** (claude-haiku-4-5-20251001, claude-3-5-sonnet)
- **Qwen/DashScope** (qwen3-max, qwen3-vl-plus) — uses langchain-qwq
- **MiniMax** (MiniMax-M2.7) — OpenAI-compatible API

Provider selection and API keys are configured through the web interface at runtime.

### Web Interface

`web_interface.py` — Flask app with `WebTradingAnalyzer` class that:
- Fetches market data from Yahoo Finance (`yfinance`)
- Supports 12 assets (SPX, BTC, GC, NQ, CL, ES, DJI, QQQ, VIX, DXY, AAPL, TSLA)
- Supports timeframes from 1m to 1mo
- Manages per-provider API keys
- Templates in `templates/`, static assets in `static/`
