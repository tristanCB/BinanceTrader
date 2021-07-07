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

# Holds binance functions for interacting with api
binance = trader.biance_api()

# Get a list of tickers from a saved text file
file_object = open('./binance_pairs.txt', 'r')
# Load JSON file data to a python dict object.
tickers_unique_pairs = json.load(file_object)['unique_pairs']
file_object.close()

# trys to get info from a dict we will be using to stored pair data
try:
    file_object = open('./binance_pairs_extended.txt', 'r')
    # Load JSON file data to a python dict object.
    tickers = json.load(file_object)
    file_object.close()
except:
    tickers = {}

# Function which takes a ticker and returns a pair's base asset
def add_base_asset(ticker):
    pair_data = binance.exchange_info(ticker)
    base_asset = pair_data["symbols"][0]["baseAsset"]
    tickers[ticker] = {
        "baseAsset"     :base_asset,
        "nonBaseAsset"  :ticker.replace(base_asset,''),
        }
    pp.pprint(tickers[ticker])

# Build the tickers dict
for i in tickers_unique_pairs:
    if i in tickers: continue
    add_base_asset(i)
    time.sleep(0.3)

# %% Checks dict
# pp.pprint(tickers)
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
                try:
                    # print(f"got price: {i['s']}")
                    tickers[i['s']].update({"ask":i['a']})
                except Exception as e:
                    print(f"Base pair not found...")
                    print(e)
                    try:
                        add_base_asset(i['s'])
                    except Exception as e:
                        print(e)
                    
threading.Thread(target=start_socket).start()

# %%

baseAssets = set([tickers[i]["baseAsset"] for i in tickers])
print(baseAssets)
while True:
    
    for i in baseAssets:
        # print(i)
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
            try:
                if i == tickers[j]['baseAsset']:
                    # print(True)
                    print("can buy")
                    matches.append(j)
                    price = 1/float(tickers[j]["ask"])
                    print(f"With {i} i can buy {j}, it will cost me {price}")
                    # print(f"With {i} i can buy {j}")

                if i == tickers[j]['nonBaseAsset']:
                    print("can sell")
                    print(f"Non base asset found {j}")
                    print(tickers[j]["ask"])
                    price = float(tickers[j]["ask"])
                    # matches.append(j)
                    print(f"With {i} i can buy {j}, it will cost me {price}")
            except:
                print("Could not find an asking price")
                # pp.pprint(tickers[j])
        # print(tickers[i])
        # print(getKeysForValueComp(tickers,i))
    time.sleep(60) 


    # time.sleep(60)

# %%
pp.pprint(tickers)
# %%
# ## SAVE A JSON OBJECT TO FILE
# # Get a file object with write permission.
# file_object = open('binance_pairs_extended.txt', 'w')
# # Save dict data into the JSON file.
# json.dump(tickers, file_object)
# file_object.close()
# pp.pprint(set(tickers))
# ##### 