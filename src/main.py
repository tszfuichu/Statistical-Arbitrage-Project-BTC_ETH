import time
import logging

import strategy
import risk_manager
import execution

# 1. Set up logging to print the console with timestamp
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# 2. Define how often the bot should run (1hour)
run_interval_second = 3600

# 3. Define the assets and account balance
assets = ["BTC/USDT", "ETH/USDT"]
account_balance = 10000.0

def run_bot_cycle():
    logging.info("Starting a new bot cycle")

    try:
        # Step 1: Strategy (Calculate Z-Score and get trading signal data)
        logging.info("Calculate the live z-score")
        z_score,beta,btc_price,eth_price = strategy.cal_live_zscore(assets[0],assets[1])

        # Step 2: Risk Management (Check if we should trade, and how much)
        logging.info("Passing z-score to Risk Manager...")
        order = risk_manager.cal_position(z_score,beta,btc_price,eth_price,account_balance)

        # Step 3: Execution (Send the order to Binance if approved)
        if order and order.get("status") != "wait":
            logging.info(f"Trade approved! ETH action: {order['eth_action']} {order['eth_qty']} BTC action: {order['btc_action']} {order['btc_qty']}")
            execution.execute_trade(order)
            logging.info("Orders placed successfully.")
        else:
            logging.info("No trade executed (No signal or blocked by Risk Manager).")

    except Exception as e:
        # If anything goes wrong (API down, calculation error), catch it here
        # so the bot doesn't completely crash and stop running.
        logging.error(f"An error occurred during the cycle: {e}")


if __name__ == "__main__":
   logging.info("Initializing Statistical Arbitrage Bot...")

   # The Infinite Loop (The Heartbeat)
   while True:
      run_bot_cycle()

      logging.info(f"Cycle complete. Sleeping for {run_interval_second} seconds...\n")
      time.sleep(run_interval_second)
