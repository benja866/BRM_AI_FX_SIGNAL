
import base64
import json
import os
from pathlib import Path

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="ai trading signal", page_icon="📈", layout="centred")

SYSTEM_PROMPT = """
You are an AI technical-analysis assistant for forex chart screenshots.
Your job is to analyze the supplied chart conservatively and return a trade setup only
when the evidence is reasonably aligned. Never guarantee profit.

Use visible evidence only. Identify:
- instrument and timeframe if visible
- market structure/trend
- support and resistance zones
- recent candlestick behavior
- possible breakout/retest or rejection
- a conservative BUY, SELL, or WAIT signal

If the chart is unclear, the price is between levels, or confirmation is missing, choose WAIT.

Return ONLY valid JSON with exactly these keys:
{
  "pair": "string",
  "timeframe": "string",
  "signal": "BUY|SELL|WAIT",
  "confidence": 0,
  "current_price": "string",
  "entry": "string",
  "stop_loss": "string",
  "take_profit_1": "string",
  "take_profit_2": "string",
  "risk_reward": "string",
  "trend": "string",
  "support": ["string"],
  "resistance": ["string"],
  "confirmation": "string",
  "invalidation": "string",
  "reason": "string"
}

Confidence must be an integer from 0 to 100. If signal is WAIT, entry/SL/TP can be
"Not active" and confirmation should describe what would trigger a valid setup.
Do not invent exact prices that cannot reasonably be read from the chart.
"""

def image_to_data_url(uploaded_file):
    raw = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/png"
    encoded = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{encoded}"

def analyze_chart(uploaded_file, model, extra_context):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    data_url = image_to_data_url(uploaded_file)

    prompt = (
        "Analyze this forex chart screenshot. "
        "Pay special attention to the latest candles and the visible price scale. "
        "Do not treat a screenshot as a guarantee of future price movement.\n\n"
        f"Trader context: {extra_context or 'None provided.'}"
    )

    response = client.responses.create(
        model=model,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": data_url, "detail": "high"},
            ],
        }],
        instructions=SYSTEM_PROMPT,
    )
    text = response.output_text.strip()

    # Remove accidental markdown fences if a model returns them.
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0].strip()

    return json.loads(text)

st.title("📈 AI Trading Signal Tool")
st.caption("Chart screenshot → technical analysis → BUY / SELL / WAIT")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "AI model",
        ["gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"],
        index=0,
    )
    st.markdown(
        "**Rule:** the tool is deliberately conservative. "
        "It can return WAIT when confirmation is missing."
    )
    st.info("For testing, use a demo account. This tool does not place trades.")

if not os.environ.get("OPENAI_API_KEY"):
    st.warning(
        "OPENAI_API_KEY is not set. Add your API key as an environment variable "
        "before running an analysis."
    )

uploaded = st.file_uploader(
    "Upload a forex chart screenshot",
    type=["png", "jpg", "jpeg", "webp"],
)

extra = st.text_input(
    "Optional context",
    placeholder="Example: EURUSD H1, looking for a low-risk setup",
)

if uploaded:
    st.image(uploaded, caption="Chart to analyze", use_container_width=True)

if st.button("🔎 Analyze chart", type="primary", disabled=uploaded is None):
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Please set OPENAI_API_KEY first.")
        st.stop()

    with st.spinner("Analyzing structure, levels and confirmation..."):
        try:
            result = analyze_chart(uploaded, model, extra)
        except json.JSONDecodeError:
            st.error("The AI returned an invalid result. Please try the chart again.")
            st.stop()
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    signal = result.get("signal", "WAIT")
    confidence = result.get("confidence", 0)

    st.subheader(f"Signal: {signal}")
    st.metric("Confidence", f"{confidence}%")

    c1, c2, c3 = st.columns(3)
    c1.metric("Pair", result.get("pair", "Unknown"))
    c2.metric("Timeframe", result.get("timeframe", "Unknown"))
    c3.metric("Trend", result.get("trend", "Unknown"))

    st.markdown("### Trade plan")
    st.write(f"**Current price:** {result.get('current_price', 'Unknown')}")
    st.write(f"**Entry:** {result.get('entry', 'Not active')}")
    st.write(f"**Stop loss:** {result.get('stop_loss', 'Not active')}")
    st.write(f"**Take profit 1:** {result.get('take_profit_1', 'Not active')}")
    st.write(f"**Take profit 2:** {result.get('take_profit_2', 'Not active')}")
    st.write(f"**Risk / reward:** {result.get('risk_reward', 'N/A')}")

    st.markdown("### Key levels")
    st.write("**Support:** " + ", ".join(result.get("support", [])))
    st.write("**Resistance:** " + ", ".join(result.get("resistance", [])))

    st.markdown("### Why")
    st.write(result.get("reason", ""))

    st.markdown("### Confirmation")
    st.write(result.get("confirmation", ""))

    st.markdown("### Invalidation")
    st.write(result.get("invalidation", ""))

    st.caption(
        "Educational technical analysis only. Markets are uncertain; "
        "a signal is not a guarantee of profit."
    )
