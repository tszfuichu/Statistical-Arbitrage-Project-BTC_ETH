
def cal_position(z_score, beta, btc_price, eth_price, account_balance, risk_pct = 0.05):

    # 1. Emergency Stop-Loss Check
    if abs(z_score) >= 4.0:
        print(f"🚨 EMERGENCY STOP LOSS TRIGGERED! Z-score is {z_score:.2f} (Exceeds +/- 4.0)")
        return {"status": "close_all", "btc_qty": 0, "eth_qty": 0}

    # 2. Determine Signal (Entry Thresholds)
    signal = None
    if z_score <= -2.0:
        signal = "Long_spread" #Long ETH and Short BTC
    elif z_score >= 2.0:
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
    eth_qty = trade_capital / spread_unit_cost
    btc_qty = eth_qty * beta

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
    test_z_score = -2.5  # Try different z-score to see different outputs
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
