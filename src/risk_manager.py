import numpy as np
import logging
from config import CONFIG

def cal_position(z_score, beta, btc_price, eth_price, account_balance, risk_pct = 0.05, open_positions=None):

    if open_positions is None:
        open_positions = {}

    if not all(isinstance(x, (int, float)) and not np.isnan(x) for x in
               [z_score, beta, btc_price, eth_price, account_balance]):
        raise ValueError("Invalid inputs: must be numbers and not NaN")

    # 1. Emergency Stop-Loss Check
    if abs(z_score) >= CONFIG['z_stop_threshold']:
        logging.warning(f"🚨 EMERGENCY STOP LOSS TRIGGERED! Z-score is {z_score:.2f} (Exceeds +/- 4.0)")
        return {"status": "close_all", "btc_qty": 0, "eth_qty": 0}


    # 2. Check for Take Profit (Mean Reversion) if we have open positions

    in_trade = len(open_positions) > 0
    if in_trade:
        # Determine what kind of spread we have open based on ETH side
        eth_position = open_positions.get("ETH/USDT", {})
        eth_side = eth_position.get('side')

        # If we are Long the spread (Long ETH), we profit when Z-score goes up to 0
        if eth_side == 'long' and z_score >= 0:
            logging.info(f"✅ TAKE PROFIT: Long spread mean reverted. Z-score is {z_score:.2f}")
            return {"status": "close_all", "btc_qty": 0, "eth_qty": 0}

            # If we are Short the spread (Short ETH), we profit when Z-score goes down to 0
        elif eth_side == 'short' and z_score <= 0:
            logging.info(f"✅ TAKE PROFIT: Short spread mean reverted. Z-score is {z_score:.2f}")
            return {"status": "close_all", "btc_qty": 0, "eth_qty": 0}

        # If we are in a trade but the mean hasn't reverted, just hold and wait
        return {"status": "wait","message": f"Holding position. Waiting for mean reversion. Current Z-score: {z_score:.2f}"}


    # 3. Determine Signal (Entry Thresholds)
    signal = None
    if z_score <= -CONFIG['z_entry_threshold']:
        signal = "Long_spread" #Long ETH and Short BTC
    elif z_score >= CONFIG['z_entry_threshold']:
        signal = "Short_spread" #Short ETH and Long BTC
    else:
        return {"status": "wait", "message": "Z-score within normal range. No action."}

    # 3. Position Sizing (Beta-Neutral)
    # Determine how much capital to allocate to this specific trade
    trade_capital = account_balance * risk_pct

    # Calculate the cost of 1 "unit" of the spread
    # 1 unit = 1 ETH + (beta * BTC)
    spread_unit_cost = eth_price + (beta * btc_price)

    # Calculate exact quantities
    eth_qty = max(0.001, min(100, trade_capital / spread_unit_cost))  # Min 0.001, max 100
    btc_qty = max(0.00001, min(1, eth_qty * beta))  # Adjust based on exchange min

    # 4. Format the final order instructions
    if signal == "Long_spread":
        return {
            "status": "open_long_spread",
            "eth_action": "Long",
            "eth_qty": round(eth_qty, 5),
            "btc_action": "Short",
            "btc_qty": round(btc_qty, 5)

        }
    elif signal == "Short_spread":
        return {
            "status": "open_short_spread",
            "eth_action": "Short",
            "eth_qty": round(eth_qty, 5),
            "btc_action": "Long",
            "btc_qty": round(btc_qty, 5)

        }

if __name__ == "__main__":

    # Example
    test_z_score = -7.9  # Try different z-score to see different outputs
    test_beta = 0.032387
    test_btc_price = 65000.0
    test_eth_price = 3500.0
    my_balance = 10000.0  # $10,000 USDT

    orders = cal_position(
        z_score=test_z_score,
        beta=test_beta,
        btc_price=test_btc_price,
        eth_price=test_eth_price,
        account_balance=my_balance
    )

    print(orders)
