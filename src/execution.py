import ccxt

#Initialize the exchange
exchange = ccxt.binance({
    'apiKey': 'APIKEY',
    'secret': 'SECRETKEY',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
    'urls': {
        'api': {
            # You MUST include the /fapi/v1 and /fapi/v2 paths!
            'fapiPublic': 'https://demo-fapi.binance.com/fapi/v1',
            'fapiPrivate': 'https://demo-fapi.binance.com/fapi/v1',
            'fapiPrivateV2': 'https://demo-fapi.binance.com/fapi/v2',
            'fapiData': 'https://demo-fapi.binance.com/futures/data'
        }
    }
})


def execute_trade(order_signal):

    status = order_signal.get('status')

    if status == 'wait':
        print("Execution: No trade needed right now.")
        return

    if status == 'close_all':
        print("Execution: Closing all open positions due to Stop-Loss!")
        return

    if status in ["open_long_spread", "open_short_spread"]:
        print(f"Execution: Executing {status}...")

        btc_symbol = "BTC/USDT"
        eth_symbol = "ETH/USDT"

        try:
            # 1. Execute ETH Order
            eth_side = 'buy' if order_signal["eth_action"] == "Long" else 'sell'
            print(f"Sending real order to Binance: {eth_side.upper()} {order_signal['eth_qty']} {eth_symbol}")
            exchange.create_market_order(eth_symbol, eth_side, order_signal['eth_qty'])

            # 2. Execute BTC Order
            btc_side = 'buy' if order_signal["btc_action"] == "Long" else 'sell'
            print(f"Sending real order to Binance: {btc_side.upper()} {order_signal['btc_qty']} {btc_symbol}...")
            exchange.create_market_order(btc_symbol, btc_side, order_signal['btc_qty'])

            print("Execution: Trades placed successfully on Binance Testnet!")

        except Exception as e:
            print(f"Execution Error: Failed to place order on Binance. Error: {e}")


if __name__ == "__main__":
    # Dummy signal from your risk_manager.py
    dummy_signal = {
        "status": "open_short_spread",
        "eth_action": "Short",
        "eth_qty": 0.0892,
        "btc_action": "Long",
        "btc_qty": 0.00289,
    }

    execute_trade(dummy_signal)
