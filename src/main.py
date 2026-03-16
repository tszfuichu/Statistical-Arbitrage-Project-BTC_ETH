import time
import logging
import strategy
import risk_manager
import execution
from config import CONFIG

# 1. Set up logging to print the console with timestamp
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# 2. Define how often the bot should run (1hour)
run_interval_second = CONFIG['run_interval_second']

# 3. Define the assets and account balance
assets = CONFIG['assets']
account_balance = CONFIG['account_balance']

#4. Create a variable for tracking order
open_positions = {}

def run_bot_cycle():

    logging.info("Starting a new bot cycle")

    try:
        # Step 1: Strategy (Calculate Z-Score and get trading signal data)
        logging.info("Calculate the live z-score")
        z_score,beta,btc_price,eth_price = strategy.cal_live_zscore(assets[0],assets[1])

        if beta <= 0 or beta > 10:
            if open_positions:
                logging.warning("🚨 Cointegration broke while in an active trade! Force closing positions for safety.")
                execution.execute_trade({"status": "close_all"}, open_positions)
                open_positions.clear()
            else:
                logging.info(f"Skipping Risk Manager because pair is not cointegrated right now. Invalid beta: {beta}")
            return

        # Step 2: Risk Management (Check if we should trade, and how much)
        logging.info("Passing z-score to Risk Manager...")
        order = risk_manager.cal_position(z_score,beta,btc_price,eth_price,account_balance,open_positions=open_positions)

        # Step 3: Execution (Send the order to Binance if approved)
        if order and order.get("status") != "wait":
            if order.get("status") == "close_all":
                logging.info("Executing CLOSE ALL positions...")
                execution.execute_trade(order, open_positions)
                # Note: execution.py already clears the open_positions dict,
                # but we can explicitly clear it here too as a failsafe
                open_positions.clear()
                logging.info("Positions closed successfully.")

                # If the signal is to open new positions
            elif order.get("status") in ["open_long_spread", "open_short_spread"]:

                # --- STATE MANAGEMENT SAFEGUARD ---
                # Double check that we don't already have open positions before executing
                if not open_positions:
                    logging.info(
                        f"Trade approved! ETH action: {order['eth_action']} {order['eth_qty']} BTC action: {order['btc_action']} {order['btc_qty']}")
                    execution.execute_trade(order, open_positions)

                    # Update our state tracking variable
                    open_positions[assets[0]] = {'qty': order['btc_qty'], 'side': order['btc_action'].lower()}
                    open_positions[assets[1]] = {'qty': order['eth_qty'], 'side': order['eth_action'].lower()}
                    logging.info("Orders placed successfully.")
                else:
                    # This shouldn't happen due to risk_manager logic, but protects against bugs
                    logging.warning(
                        "Safeguard triggered: Attempted to open a new position, but a trade is already active! Ignoring signal.")
        else:
            logging.info(f"No trade executed ({order.get('message', 'No signal')}).")

    except ValueError as e:
        logging.warning(f"Data issue, skipping cycle: {e}")

    except Exception as e:
        logging.error(f"Critical error, stopping bot: {e}")
        raise  # Re-raise to stop if critical


if __name__ == "__main__":
   logging.info("Initializing Statistical Arbitrage Bot...")

   # The Infinite Loop (The Heartbeat)
   while True:
      run_bot_cycle()

      logging.info(f"Cycle complete. Sleeping for {run_interval_second} seconds...\n")
      time.sleep(run_interval_second)
