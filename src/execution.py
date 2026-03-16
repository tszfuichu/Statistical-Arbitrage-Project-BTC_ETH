import ccxt
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
print("Loaded API Key:", os.getenv('APIKEY')[:5] + "...")

#Initialize the exchange
exchange = ccxt.binance({
    'apiKey': os.getenv('APIKEY'),
    'secret': os.getenv('SECRETKEY'),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    }})

exchange.enable_demo_trading(True)


def execute_trade(order_signal, open_positions = None):

    try:
        balance = exchange.fetch_balance()
        if balance['USDT']['free'] < 1000:
            raise Exception("Insufficient balance on testnet")
    except Exception as e:
        logging.error(f"Balance check failed: {e}")
        return

    status = order_signal.get('status')
    btc_symbol = "BTC/USDT"
    eth_symbol = "ETH/USDT"

    if status == 'wait':
        logging.info("Execution: No trade needed right now.")
        return

    if status == 'close_all':
        try:
            exchange.cancel_all_orders()  # Cancel pending
            positions = exchange.fetch_positions()
            for pos in positions:
                if pos['symbol'] in [btc_symbol, eth_symbol] and pos['contracts'] != 0:  # Use 'contracts' for futures
                    side = 'sell' if pos['side'] == 'long' else 'buy'
                    exchange.create_market_order(pos['symbol'], side, abs(pos['contracts']))
            if open_positions:
                open_positions.clear()
        except Exception as e:
            logging.error(f"Failed to close positions: {e}")
        return

    if status in ["open_long_spread", "open_short_spread"]:
        logging.info(f"Execution: Executing {status}...")

        try:
            # 1. Execute ETH Order
            eth_side = 'buy' if order_signal["eth_action"] == "Long" else 'sell'
            logging.info(f"Sending real order to Binance: {eth_side.upper()} {order_signal['eth_qty']} {eth_symbol}")
            eth_order = exchange.create_market_order(eth_symbol, eth_side, order_signal['eth_qty'])
            if not eth_order or 'id' not in eth_order:
                raise Exception(f"ETH order failed: {eth_order}")

            # 2. Execute BTC Order
            btc_side = 'buy' if order_signal["btc_action"] == "Long" else 'sell'
            logging.info(f"Sending real order to Binance: {btc_side.upper()} {order_signal['btc_qty']} {btc_symbol}...")
            btc_order = exchange.create_market_order(btc_symbol, btc_side, order_signal['btc_qty'])
            if not btc_order or 'id' not in btc_order:
                raise Exception(f"BTC order failed: {btc_order}")

            logging.info("Execution: Trades placed successfully on Binance Testnet!")

        except Exception as e:
            logging.info(f"Execution Error: Failed to place order on Binance. Error: {e}")


if __name__ == "__main__":
    # Dummy signal from your risk_manager.py
    dummy_signal = {
        "status": "open_short_spread",
        "eth_action": "Short",
        "eth_qty": 0.82,
        "btc_action": "Long",
        "btc_qty": 0.02,
    }

    execute_trade(dummy_signal)
