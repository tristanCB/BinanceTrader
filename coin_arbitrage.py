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
import threading
reload(trader)
tickers = {}
# Create the 
binance = trader.biance_api()

file_object = open('./binance_pairs_extended.txt', 'r')
# Load JSON file data to a python dict object.
tickers = json.load(file_object)
_counter = 0

def add_base_asset(ticker):
    pair_data = binance.exchange_info(ticker)
    base_asset = pair_data["symbols"][0]["baseAsset"]
    tickers[ticker] = {
        "baseAsset"     :base_asset,
        "nonBaseAsset"  :ticker.replace(base_asset,''),
        }

def get_non_base_pairs():
    for i in tickers:
        pp.pprint(tickers[i]["baseAsset"])
        tickers[i].update({"nonBaseAsset":i.replace(tickers[i]["baseAsset"], '')}) 

get_non_base_pairs()
# %%
pp.pprint(tickers)
# %%

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

# Infinite loop waiting for WebSocket data

def start_socket():
    while True:
        payload = json.loads(ws.recv())
        # print(pp.pprint(payload))
        print("GOT PAYLOAD!!")
        if 'result' not in [i for i in payload]:
            for i in payload:
                # print(i['s'])
                try:
                    tickers[i['s']].update({"ask":i['a']})
                except:
                    print(f"Base pair not found...")
                    add_base_asset(i['s'])
                    
threading.Thread(target=start_socket).start()

# %%

baseAssets = set([tickers[i]["baseAsset"] for i in tickers])
print(baseAssets)

for i in baseAssets:
    print(i)
    if i != "USDT": continue
    matches = []
    pp.pprint(len(tickers))
    for j in tickers:
        # prevents from checking itself
        # if i == j:
        #     continue
        # print(tickers[j])
        # print(tickers[i])
        # assert 1 == 2
        if i == tickers[j]['baseAsset']:
            print(True)
            print("can buy")
            matches.append(j)
            try:
                price = 1/float(tickers[j]["ask"])
                print(f"With {i} i can buy {j}, it will cost me {price}")
            except:
                print("Could not find an asking price")
                print(f"With {i} i can buy {j}")
        if i == tickers[j]['nonBaseAsset']:
            print(f"Non base asset found {j}")
            print(tickers[j]["ask"])
            price = float(tickers[j]["ask"])
            print(f"With {i} i can buy {j}, it will cost me {price}")

            # pp.pprint(tickers[j])
    # print(tickers[i])
    # print(getKeysForValueComp(tickers,i))
    


    # time.sleep(60)

# %%
pp.pprint(tickers)
# %%
## SAVE A JSON OBJECT TO FILE
# Get a file object with write permission.
file_object = open('binance_pairs_extended.txt', 'w')
# Save dict data into the JSON file.
json.dump(tickers, file_object)
pp.pprint(set(tickers))
##### 