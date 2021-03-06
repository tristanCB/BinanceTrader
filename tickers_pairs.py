# %%
# !/usr/bin/env python3
# Scans for all unique pairs on binance
import asyncio
import json
import pprint
import time
from datetime import datetime
pp = pprint.PrettyPrinter(indent=4)
from websocket import create_connection
import trader
from importlib import reload

# %%
reload(trader)

# Create the 
binance = trader.biance_api()

def on_message(ws, message):
    print(message)
    assert 1 == 2

# Connect to WebSocket API and subscribe to trade feed for XBT/USD and XRP/USD
ws = create_connection("wss://stream.binance.com:9443/ws", on_message = on_message)
payload = {
        "method": "SUBSCRIBE",
        "params":
        [
        # "dogeusdt@aggTrade",
        # "usdtdoge@forceOrder",
        "!ticker@arr",
        # "dogeusdt@depth20@100ms"
        # "dogeusdt@nav_Kline_1m",
        # "dogeusdt@forceOrder",
        # "dogeusdt@ticker",
        ],
        "id": 999
    }
ws.send(json.dumps(payload))
tickers = []
# Infinite loop waiting for WebSocket data

while True:
    payload = json.loads(ws.recv())
    # print(pp.pprint(payload))
    print()
    if 'result' not in [i for i in payload]:
        print(pp.pprint(payload))
        for i in payload:
            print(i['s'])
            tickers.append(i['s'])
            print(len(set(tickers)))
            # get_aggTrades(self, symbol='DOGEUSDT'):
            # binance.get_kline_timeframe()

        # timestamp = payload['lastUpdateId']
        # dtt = datetime.fromtimestamp(int(timestamp)/1000)
        # timestring = dtt.strftime('%d.%m.%Y %H:%M:%S')
        # print(f'--------> Asks: {len(payload["asks"])} Bids: {len(payload["bids"])}')
        # print(timestring, '---' ,str(int(timestamp)/1000).split('.')[-1])
        # binance.inter_socket_strem(str(payload))
    # if payload != {'id': 999, 'result': None}:
    #     if len(payload) not in[7, 11]:
    #         raise ImportWarning()
# %%
## SAVE A JSON OBJECT TO FILE
# Get a file object with write permission.
file_object = open('binance_pairs.txt', 'w')
# Save dict data into the JSON file.
json.dump({'unique_pairs': list(set(tickers))}, file_object)
pp.pprint(set(tickers))
##### 