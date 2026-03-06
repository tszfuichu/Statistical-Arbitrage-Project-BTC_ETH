import pandas as pd
from datetime import datetime, timedelta, timezone
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
import numpy as np

# 1. Import the function from the Data folder
from Data.fetch_data import fetch_data

# 2. Take the last 720 hours live data and calculate the current Z-score
def cal_live_zscore(symbol1, symbol2):
    """
    Fetches the last 720 hours of data and calculates the current Z-score.
    """
    # Calculate the start_time and end_time (720 hours)
    end_time = datetime.now(timezone.utc)
    start_time = end_time-timedelta(hours=720)

    end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

    print(f"Fetching live data from {start_time} to {end_time}...")

    # Fetch the data
    df1 = fetch_data(symbol1, timeframe= '1h', total_candle= 720)
    df2 = fetch_data(symbol2, timeframe= '1h', total_candle= 720)

    # 2. Concat the two file to a dataframe(Pandas will automatically merge two data by timestamp)
    df = pd.concat([df1['close'], df2['close']], axis=1, keys=['btc', 'eth']).dropna()

    # 3. Perform the Cointegration Test (Engle-Granger test)
    score, p_value, _ = coint(df['btc'], df['eth'])

    # Print the p_value in different situation
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

    # Print the Beta(M): coefficient of BTC
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
    print(f'Live z score = {df['z_score'].iloc[-1]}')

    return 3, beta, df['btc'].iloc[-1], df['eth'].iloc[-1]


if __name__ == "__main__":
    z = cal_live_zscore("BTC/USDT", "ETH/USDT")
    print(f"Current Live Z-Score: {z}")
