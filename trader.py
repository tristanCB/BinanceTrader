# %%
import requests
import pprint
import json
import pyodbc
import pandas as pd
from datetime import datetime
import uuid
pp = pprint.PrettyPrinter(indent=4)

class biance_api:
    ''' A simple interface with the biance API'''
    def __init__(self):
        self.base_endpoint = "https://api.binance.com/api/v3/klines"

        self.symbols = ['DOGEUSDT']
        self.timeframes = ['5m', '15m','1h', '2h', '4h', '8h', '1d', '3d', '1w', '1M']

        # Uses pyodbc to save stuff on SQL database
        self.cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                            "Server=DESKTOP-ORTN7V7;"
                            "Database=BianceTrader;"
                            "Trusted_Connection=yes;")
        # Connect to databse
        self.cursor = self.cnxn.cursor()

    def get_current_index(self):
        self.cursor.execute("select top 1 [key] from doge2 order by [key] DESC;")
        row = self.cursor.fetchone()
        if row == None: return 0
        return row[0]

    def get_kline_timeframe(self, symbol, timeframe='1m', limit=1000):
        url = "https://api.binance.com/api/v3/klines"
        data = requests.get(
            url,
            params=[
                ('symbol', symbol),
                ('interval', timeframe),
                ('limit',limit)
                ],
            )
        payload = json.loads(data.content)
        # pp.pprint(payload)
        return payload

    # GET /api/v3/trades
    def get_depth(self, symbol='DOGEUSDT', limit=1000):
        url = "https://api.binance.com/api/v3/trades"
        data = requests.get(
            url,
            params=[
                ('symbol', symbol),
                ('limit', limit)
                ],
            )
        dict_depth = json.loads(data.content)
        for i in dict_depth:
            i['timestring'] = datetime.fromtimestamp(int(i['time'])/1000).strftime('%d.%m.%Y %H:%M:%S')
        return dict_depth
        

    # GET /api/v3/aggTrades
    def get_aggTrades(self, symbol='DOGEUSDT'):
        url = "https://api.binance.com/api/v3/aggTrades"
        data = requests.get(
            url,
            params=[
                ('symbol', symbol),
                ('limit',1000)
                ],
            )
        dict_depth = json.loads(data.content)
        for i in dict_depth:
            # pp.pprint(i)
            i['timestring'] = datetime.fromtimestamp(int(i['T'])/1000).strftime('%d.%m.%Y %H:%M:%S')
        return dict_depth

    def data_sql_dump(self, timeframe = '1m'):
        uuid = self.get_current_index() + 1
        data_dict = biance_api.get_kline_timeframe('DOGEUSDT', timeframe)
        for i in data_dict:
            pp.pprint(i)
            print(len(i))
            # Biance time https://stackoverflow.com/questions/48757836/compute-date-out-of-timestamp-from-binance-api-python
            dtt = datetime.fromtimestamp(int(i[0])/1000)
            timestring = dtt.strftime('%d.%m.%Y %H:%M:%S')
            print(timestring)
            # assert 1 == 2
            self.cursor.execute("INSERT INTO doge2([key], opentime, [open], high, low, [close], volume, closetime, quoteasset, numberoftrades, takersbuybase, takerbuyquoteasset, ignore, timeframe, timestring) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (uuid, i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], timeframe, timestring))
            self.cnxn.commit()
            uuid += 1
    
    def get_df_from_query(self):
        SQL_Query = pd.read_sql_query('SELECT * FROM doge2', self.cnxn)
        df = pd.DataFrame(SQL_Query, columns=['key', 'opentime', 'open', 'high', 'low', 'close', 'volume', 'closetime', 'quoteasset', 'numberoftrades', 'takersbuybase', 'takerbuyquoteasset', 'ignore', 'timeframe', 'timestring'])
        print (df)
        return df

    def data_wipe(self, table = 'doge2'):
        # %% Wipes table
        self.cursor.execute(f"truncate table {table}")
        self.cnxn.commit()

    # Little function to select a random row
    def fetch_me_one(self):
        self.cursor.execute('SELECT * FROM doge2')
        row = self.cursor.fetchone()
        print('row:', row)

    def inter_socket_strem(self, payload):
        currency_pair = 'dogeusdt'
        uniqueID = uuid.uuid1()
        print(uniqueID)
        self.cursor.execute("INSERT INTO sockettable(uuid, payload, pair) VALUES (?, ?, ?)", (uniqueID, json.dumps(payload), currency_pair))
        self.cnxn.commit()

    def check_length(self, table):
        """ Counts number of entries in a database """
        all = self.cursor.execute(f"SELECT * FROM {table}")
        # build list of column names to use as dictionary keys from sql results
        columns = [column[0] for column in all.description]
        results = []
        for row in all.fetchall():
            results.append(dict(zip(columns, row)))
        return len(results), results

    
    
if __name__ == "__main__":
    biance_api = biance_api()
    biance_api.get_current_index()
    biance_api.data_sql_dump()
    biance_api.get_current_index()
else:
    pass

# %% Wipes table
# cursor.execute("truncate table doge2")
# cnxn.commit()
# %% 
# # Bianance timeframes
# timeframes = ['5m', '15m','1h', '2h', '4h', '8h', '1d', '3d', '1w', '1M']

# # loop through timeframes and save data to the connected database 
# uuid = 0
# biance_api = biance_api()
# for timeframe in timeframes:
#     # data_dict = get_kline_timeframe(timeframe)
#     data_dict = biance_api.get_kline_timeframe('DOGEUSDT', timeframe)
#     pp.pprint(data_dict)

#     for i in data_dict:
#         pp.pprint(i)
#         print(len(i))
#         cursor.execute("INSERT INTO doge2([key], opentime, [open], high, low, [close], volume, closetime, quoteasset, numberoftrades, takersbuybase, takerbuyquoteasset, ignore, timeframe) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (uuid, i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], timeframe))
#         cnxn.commit()
#         uuid += 1

# %%
# fetch_me_one()
## Biance Payload for candlestick data
# [
#   [
#     1499040000000,      // Open time
#     "0.01634790",       // Open
#     "0.80000000",       // High
#     "0.01575800",       // Low
#     "0.01577100",       // Close
#     "148976.11427815",  // Volume
#     1499644799999,      // Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "17928899.62484339" // Ignore.
#   ]
# ]
# biance will give you 500 hitoric cnadles
