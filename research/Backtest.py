import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import cointegration_test
from src.config import CONFIG

#The Trading rule:
# Long spread (z_score < -2): We need to Long 'ETH' & Short 'BTC'
# Short spread (z_score > +2): We need to Short 'ETH' & Long 'BTC'
# Exit Trade: When Z-Score crosses back to 0 (mean reversion is complete)

# 1. Load df and beta value
data = cointegration_test.test()
df = data[0]
beta = data[1]

# 2. Create a column that define our current position(0: no trade, 1: Long Spread, -1: Short Spread)
df['position'] = 0
current_position = 0
z_stop_threshold = [CONFIG['z_stop_threshold'],-CONFIG['z_stop_threshold']]
z_range = [CONFIG['z_entry_threshold'],-CONFIG['z_entry_threshold']]
wait_for_reset = 0
leverage = CONFIG['leverage']

# 3. Loop through the data to generate trading signals
for i in range(len(df)):
    z = df['z_score'].iloc[i]

    # --- RESET LOGIC ---
    # If we are in a cooldown, check if the Z-score has reverted to the mean (0) to unlock trading
    if wait_for_reset == 1 and z <= 0:
        wait_for_reset = 0

    # If we are currently not in a trade
    if current_position == 0 and wait_for_reset == 0:
        if z < z_range[1] and z > z_stop_threshold[1]:
            current_position = 1 # Long Spread: Long 'ETH' & Short 'BTC'
        elif z > z_range[0] and z < z_stop_threshold[0]:
            current_position = -1 # Short Spread: Short 'ETH' & Long 'BTC'
        else:
            current_position = 0

    # If we are currently in Long spread
    elif current_position == 1:
        if z >= 0 :
            current_position = 0 # Exit trade (mean reversion is complete)
        elif z <= z_stop_threshold[1]:
            current_position = 0
            wait_for_reset = 1 # Enter cooldown until Z-score reverts to mean (0)

    # If we are currently in Short spread
    elif current_position == -1:
        if z <= 0 :
            current_position = 0 # Exit trade (mean reversion is complete)
        elif z >= z_stop_threshold[0]:
            current_position = 0
            wait_for_reset = 1 # Enter cooldown until Z-score reverts to mean (0)

    # Record the position for this timestamp
    df.iloc[i, df.columns.get_loc('position')] = current_position

# 4. Calculate Returns
# Shift position by 1 because we trade on the CLOSE of the signal candle (Avoid the look-ahead bias)
# so we earn the return on the next candle
# Example: ETH: $3000 BTC: $60000
# Beta: 0.05 which means if I Long 1 unit of ETH, I will short 0.05 unit of BTC

df['position_shift'] = df['position'].shift(1).fillna(0)

# Calculate the daily dollar change (PnL) for both assets
df['eth_diff'] = df['eth'].diff()
df['btc_diff'] = df['btc'].diff()

# Calculate the dollar PnL of holding 1 unit of the spread
# Spread PnL = Change in ETH price - (beta * Change in BTC price)
# Example: ETH: $3000>3150 BTC: $60000>61000 (Long Spread)
# eth_diff: 1 unit * 150 = $150
# (beta * df['btc_diff']): 0.05 * 1000 = $50
# spread_pnl = $100

df['spread_pnl'] = df['eth_diff'] - (beta * df['btc_diff'])
df['spread_pnl'] = df['spread_pnl'].fillna(0)

# Calculate the gross capital required to hold this position
# Capital = Price of 1 ETH + Price of (beta * BTC) | use the previous candle price
# Example: 1 unit * 3000 + 0.05unit * 60000 = $6000
df['gross_exposure'] = df['eth'].shift(1) + (beta * df['btc'].shift(1))

# Calculate the margin required to hold this position with leverage
# Margin = Gross Exposure / Leverage
# Example: $6000 / 20 = $300
df['margin_required'] = df['gross_exposure'] / leverage

# Calculate the transaction cost (fee) for both legs of the trade
# position change = when a trade happens (0 to 1 = 1 open, 1 to 0 = 1 close)
# Fee = gross_exposure * fee_rate * position change
# Example: $6000 * 0.0002 * 1 = $1.2
df['position_change'] = df['position_shift'].diff().fillna(0).abs()
df['transaction_cost'] = df['gross_exposure'] * CONFIG['fee_rate'] * df['position_change']
df['transaction_cost'] = df['transaction_cost'].fillna(0)

# Calculate Net Dollar PnL (Gross Profit from spread MINUS Dollar Fees)
df['net_dollar_pnl'] = (df['position_shift'] * df['spread_pnl']) - df['transaction_cost']
df['net_dollar_pnl'] = df['net_dollar_pnl'].fillna(0)

# Calculate the actual percentage return of the spread
# Example = $100 / $6000 = 0.016667
df['strategy_return'] = df['net_dollar_pnl'] / df['margin_required']
df['strategy_return'] = df['strategy_return'].fillna(0)

# If a trade loses more than 100% of your margin, you are liquidated.
# We clip the minimum return at -1.0 (-100%) to simulate a blown account.
df['strategy_return'] = df['strategy_return'].clip(lower=-1.0)

# Calculate final strategy return
# Example = 1(Long spread) * 0.16667 = 0.16667
df['cumulative_return'] = (1 + df['strategy_return']).cumprod()

print(df)

plt.figure(figsize=(12, 6))
plt.plot(df.index, df['cumulative_return'], color='purple', label='Strategy Equity Curve')
plt.axhline(1.0, color='black', linestyle='--')
plt.title('Pairs Trading Strategy Performance')
plt.ylabel('Cumulative Return (1.0 = Initial Capital)')
plt.legend()
plt.show()

