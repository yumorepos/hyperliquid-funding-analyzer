# Hyperliquid Funding Rate Analyzer

**Real-time analysis of perpetual funding rates on Hyperliquid DEX**

A Python CLI tool that identifies arbitrage opportunities by analyzing funding rate patterns across all perpetual markets. Built with real API integration, statistical analysis, and clean output formatting.

---

## 🎯 What It Does

1. **Fetches live data** from Hyperliquid's public API
2. **Calculates annualized funding rates** from 8-hour periods
3. **Ranks assets** by absolute funding magnitude
4. **Identifies arbitrage opportunities** where funding rates are extreme
5. **Exports results** to CSV for further analysis

---

## 🚀 Quick Start

```bash
# Basic analysis (top 20 assets)
python3 funding_analyzer.py

# Show top 30 with verbose logging
python3 funding_analyzer.py --top 30 --verbose

# Export results
python3 funding_analyzer.py --export funding_report.csv

# Find high-conviction opportunities (>0.2% 8H rate)
python3 funding_analyzer.py --threshold 0.002
```

---

## 📊 Sample Output

```
🔍 Analyzing current funding rates...

📊 Top 20 Assets by Funding Rate:

------------------------------------------------------------------------------------------
Coin       8H Rate      Annual %     Price        Direction      
------------------------------------------------------------------------------------------
DOGE         0.001250       136.88    $0.08       LONG_PAYS      
PEPE         0.000980       107.16    $0.00       LONG_PAYS      
WIF         -0.000850       -93.08    $1.85       SHORT_PAYS     
...

📈 Summary:
  • Total assets: 147
  • Positive funding (longs pay shorts): 89
  • Negative funding (shorts pay longs): 58
  • Mean 8H funding rate: 0.000123
  • Median 8H funding rate: 0.000089

💡 Arbitrage Opportunities (|funding| > 0.10%):

==================================================================================

DOGE:
  • 8H Rate: 0.001250 (+136.88% annualized)
  • Price: $0.08
  • 🔴 SHORT + earn funding from longs
  • Risk: Avoid if strong uptrend (funding can stay high)

WIF:
  • 8H Rate: -0.000850 (-93.08% annualized)
  • Price: $1.85
  • 🟢 LONG + earn funding from shorts
  • Risk: Avoid if strong downtrend (funding can stay negative)

==================================================================================

✅ Analysis complete.
```

---

## 🔧 Dependencies

```bash
pip install requests pandas
```

No API keys required — uses public endpoints.

---

## 📁 Project Structure

```
hyperliquid-funding-analyzer/
├── funding_analyzer.py    # Main CLI tool
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

---

## 🎓 Technical Skills Demonstrated

- **API Integration:** REST API calls with requests library
- **Data Analysis:** Pandas DataFrames, statistical calculations
- **CLI Design:** argparse with subcommands and help docs
- **Error Handling:** Graceful failures with user-friendly messages
- **Code Quality:** Type hints, docstrings, modular class design
- **Financial Concepts:** Funding rates, annualization, arbitrage detection

---

## 💡 Use Cases

- **Traders:** Identify funding rate arbitrage opportunities
- **Researchers:** Analyze market sentiment via funding imbalances
- **Bot Developers:** Integrate as signal source for automated strategies
- **Portfolio Project:** Demonstrates real-world quant/trading system skills

---

## 🛠️ Future Enhancements

- [ ] Historical funding rate trends (time-series visualization)
- [ ] Alert system for extreme funding spikes
- [ ] Cross-exchange funding comparison (Hyperliquid vs. Binance/Bybit)
- [ ] Backtesting module for funding arbitrage strategy
- [ ] WebSocket support for real-time monitoring

---

## 📜 License

MIT License — Free to use and modify.

---

**Author:** Yumo Xu  
**Created:** March 13, 2026  
**Portfolio:** [GitHub Profile](https://github.com/yumorepos)
