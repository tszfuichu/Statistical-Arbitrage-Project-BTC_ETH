import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint


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
