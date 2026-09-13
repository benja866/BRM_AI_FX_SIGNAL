
# AI Trading Signal Tool

This is the first prototype of the chart-analysis tool discussed in ChatGPT.

## What it does

1. Upload a forex chart screenshot.
2. The AI reads the visible pair, timeframe, candles and price scale.
3. It returns:
   - BUY / SELL / WAIT
   - confidence
   - entry idea
   - stop loss
   - two take-profit levels
   - risk/reward
   - trend
   - support/resistance
   - confirmation condition
   - invalidation condition
   - explanation

It is intentionally conservative and can return WAIT.

## Run it

Python 3.10+ is recommended.

```bash
pip install -r requirements.txt
```

Set your OpenAI API key as an environment variable.

Linux/macOS:
```bash
export OPENAI_API_KEY="your_api_key"
streamlit run app.py
```

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="your_api_key"
streamlit run app.py
```

Then open the local Streamlit address shown in the terminal.

## Important

- Do not put an API key directly into `app.py`.
- Test with a demo trading account.
- Screenshot-only analysis can miss information that would be available from raw OHLC/tick data.
- This prototype does not connect to Deriv, MetaTrader, a broker, or place orders.

## Next upgrades

A production version can add:
- live OHLC data
- multi-timeframe confirmation
- RSI, MACD, EMA and ATR
- automatic support/resistance
- risk-per-trade position sizing
- signal history and performance tracking
- backtesting
- a mobile-friendly hosted interface
- optional Deriv/MT5 data integration without automatic order execution
