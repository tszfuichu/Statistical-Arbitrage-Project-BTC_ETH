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
* `.env`: It is a non-public file used to store the trading platform's API keys.

## 🛠️ Prerequisites & Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/tszfuichu/Statistical-Arbitrage-Project-BTC_ETH.git
   cd Statistical-Arbitrage-Project-BTC_ETH

2. **Install dependencies:**
   Ensure you have Python 3.8+ installed, then run:
   ```bash
   pip install pandas numpy statsmodels ccxt python-dotenv
   
4. **Set up Environment Variables:**
   Modify the .env file with your API keys
   ```bash
   APIKEY=your_api_key
   SECRETKEY=your_secret_key
   
## ⚙️ Configuration (config.py)
You can easily customize the bot's behavior without changing the core logic by modifying the variables inside `src/config.py`. Here are the key parameters you can adjust:

* **Time & Data Parameters:**

  * `total_hr_candle`: The number of historical hourly candles used to calculate the cointegration, hedge ratio (beta), and spread mean/std. (e.g., `720` = 30 days of data).
  * `run_interval_second`: How often the bot fetches new data and checks for trade signals, in seconds. (e.g., `3600` = runs once every hour).
  * `assets`: A list containing the two trading pairs you are arbitraging (e.g., `["BTC/USDT", "ETH/USDT"]`).

* **Risk & Capital Management:**

  * `account_balance`: The base capital used for calculating position sizes (e.g., `10000.0`).
  * `risk_pct`: The percentage of the account balance to risk on a single pairs trade (e.g., `0.05` means 5% risk).
 
* **Z-Score Thresholds (Strategy Logic):**

  * `z_entry_threshold`: The Z-score level at which the bot opens a trade (e.g., `2.0`). A higher number means fewer, but potentially safer, trades.
  * `z_stop_threshold`: The extreme Z-score level at which the bot cuts losses to protect capital (e.g., `4.0`).

## 🚀 Usage
   Once your .env is set up and your config.py is tuned to your liking, start the trading bot by running:
   ```bash
   python src/main.py

## ⚠️ Disclaimer
This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. The authors and all affiliates assume no responsibility for your trading results. Always test strategies thoroughly on a Testnet before deploying real capital.

