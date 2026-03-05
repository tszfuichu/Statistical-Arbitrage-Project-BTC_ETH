import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
import pickle

# 1. Load the BTC and ETH parquet files
btc = pd.read_parquet('../Data/data/BTC_USDT.parquet')['close']
eth = pd.read_parquet('../Data/data/ETH_USDT.parquet')['close']

# 2. Concat the two file to a dataframe(Pandas will automatically merge two data by timestamp)
df = pd.concat([btc,eth],axis=1, keys=['btc','eth']).dropna()

# 3. Perform the Cointegration Test (Engle-Granger test)
score, p_value,_ = coint(df['btc'], df['eth'])

#Print the p_value in different situation
if p_value < 0.05:
    print(f'Cointegration P-value: {p_value:.4f}. The pair is cointegrated! ')
else:
    if p_value > 0.05:
        print(f'Cointegration P-value: {p_value:.4f}. Cointegration P-value is too high')
    else:
        print('Unexpected Error')

# 4. Calculate the Hedge Ratio by using Ordinary Least Squares (OLS) Regression (Y = MX + C)
# BTC: independent variable(X) & ETH: dependent variable(Y)
x = df['btc']
y = df['eth']

# Add a constant to the independent variable for the regression model (Make sure the C is not a zero)
x_constant = sm.add_constant(x)

# Fit the regression model result will be a constant(C) & slope(M)
model = sm.OLS(y, x_constant).fit()

#Print the Beta(M): coefficient of BTC
beta = model.params['btc']
print(f'Hedge Ratio (beta): {beta:.6f}')
print(f"This means for every 1 BTC, you need {beta:.6f} ETH to hedge.\n")

# 5. Calculate the Spread
# Formula: spread = P(ETH) - (beta * P(BTC))
# beta * P(BTC) + C is mean the fair price of P(ETH)
# If the result is positive > P(ETH) is currently overpriced
# If the result is negative > P(ETH) is currently underpriced

df['spread'] = df['eth'] - (beta * df['btc'])

# 6. Calculate the Z-Score of the Spread
# Z-score Formula = (x - mean(x))/std(x)
spread_mean = df['spread'].mean()
spread_std = df['spread'].std()

df['z_score'] = (df['spread'] - spread_mean) / spread_std

# 7. Save the value I need for the next file
df.to_parquet('../Data/data/z-score.parquet')
pickle.dump(beta, open('../Data/data/beta.pkl', 'wb'))

# 8. Plot the Z-Score to visualize the trading signals
plt.figure(figsize=(12,6))
plt.plot(df.index, df['z_score'], label='Z-Score')
plt.axhline(0, color='black', linestyle='--')
plt.axhline(1.0, color='red', linestyle='-', label='Upper Threshold (Short Spread)')
plt.axhline(-1.0, color='green', linestyle='-', label='Lower Threshold (Long Spread)')
plt.title('Z-Score of BTC/ETH Spread')
plt.legend()
plt.show()


