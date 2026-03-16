# Crypto Statistical Arbitrage Trading Bot 📈🤖

A Python-based trading bot that implements a statistical arbitrage (pairs trading) strategy between Bitcoin (BTC) and Ethereum (ETH) on the Binance Futures Testnet. 

The bot continuously monitors the price spread between BTC and ETH, calculates the Z-score based on historical cointegration and a dynamic hedge ratio (beta), and automatically executes beta-neutral trades when the spread deviates significantly from its mean.

## 🌟 Features
* **Statistical Arbitrage Strategy:** Uses the Engle-Granger cointegration test and Ordinary Least Squares (OLS) regression to calculate the hedge ratio (beta) and spread.
* **Live Z-Score Monitoring:** Fetches live market data to calculate the current Z-score of the spread.
* **Automated Execution:** Integrates with the `ccxt` library to automatically place Market Long/Short orders on Binance Futures.
* **Advanced Risk Management:** 
  * Beta-neutral position sizing.
  * Automated Take-Profit (triggers when the Z-score reverts to the mean).
  * Emergency Stop-Loss (triggers if the Z-score exceeds extreme thresholds).
* **State Management:** Safely tracks open positions to prevent over-trading and duplicate orders.

## 📂 Project Structure
* `src/main.py`: The heartbeat of the bot. Runs the infinite loop, connecting the strategy, risk manager, and execution modules.
* `src/strategy.py`: Fetches historical/live data, performs cointegration tests, calculates the beta (saved as a `.pkl` file), and calculates the live Z-score.
* `src/risk_manager.py`: Determines if a trade should be opened, held, or closed based on Z-score thresholds. Calculates exact position sizes based on account balance and risk percentage.
* `src/execution.py`: Handles the actual API connection to Binance Testnet via `ccxt` to open and close futures contracts.
* `src/config.py`: Centralized configuration file for easy tweaking of thresholds, intervals, and risk parameters.
* `Data/fetch_data.py`: Helper script to fetch OHLCV candle data from the exchange (dependency for `strategy.py`).
* `venv/.env`: It is a non-public file used to store the trading platform's API keys.

## 🛠️ Prerequisites
Before running the bot, ensure you have Python 3.8+ installed. You will also need the following Python libraries:
```bash
pip install pandas numpy statsmodels ccxt python-dotenv

