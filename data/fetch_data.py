# Download and format the historical data
import ccxt
import pandas as pd
import time
import os


def fetch_data(symbol, timeframe = '1h', total_candle=20000):
    '''
    Fetch the historical OHLCV data for symbol
    '''
    print(f'Fetch {total_candle} data points for {symbol}')

    # Define the exchange
    exchange = ccxt.binance()
    all_data = []

    # Calculate the start time : Current Time - 20000 * 1h
    hour_in_ms = 60*60*1000
    since = exchange.milliseconds() - (total_candle * hour_in_ms)

    #Fetch the data
    while len(all_data) < total_candle:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe,since = since, limit=1000)
        if not ohlcv:
            break

        all_data.extend(ohlcv)

        #Update since to timestamp of the last candle of the previous fetching and + 1 millisecond
        since = ohlcv[-1][0] + 1

        #Pause for 0.5 seconds to avoid Binance banning for spamming requests
        time.sleep(0.5)

    #convert the data to a dataframe
    df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    #convert the timestamp to a readable datatime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    return df

if __name__ == "__main__":
    #Define the pairs we want to analyze
    symbols = ['BTC/USDT', 'ETH/USDT']

    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)

    for symbol in symbols:
        df = fetch_data(symbol, timeframe = '1h', total_candle= 5000)

        #Clean the symbol name e.g. 'BTC/USDT' > 'BTC_USDT'
        file_name = symbol.replace('/','_')
        file_path = f'data/{file_name}.parquet'

        #Save the dataframe in a parquet format
        df.to_parquet(file_path)
        print(f'Saved {symbol} data to {file_path}')

        #Sleep 1 second to respect the rate limits of exchange(Binance)
        time.sleep(1)

    print('Data fetching complete')



