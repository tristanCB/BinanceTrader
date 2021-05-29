# !/usr/bin/env python3
# This script uses 
# %% BINANCE SCANNER
import asyncio
import json
import pprint
import time
from datetime import datetime
pp = pprint.PrettyPrinter(indent=4)
from websocket import create_connection
from importlib import reload
from numpy import diff
import statistics
import pandas as pd
import statistics
import trader


# Apply rolling windows as smoothing
n = 120
# Use this as timeframe for trading. --> 
GETSOME = 10

reload(trader)
# Create the 
binance = trader.biance_api()
# Get a file object with write permission.
file_object = open('binance_pairs.txt', 'r')
# Load JSON file data to a python dict object.
dict_object = json.load(file_object)

scanner = {}
number_of_trades_per_minutes = {}

best = None
worst = None
highest_variance = None
highest_std_dev = None


for pair in dict_object['unique_pairs']:
    # print(f'Scanning --> {pair}')

    pair_list = []
    num_trades_list = []
    klineDate = binance.get_kline_timeframe(pair, timeframe='1m')
    for kline in klineDate:
        # print('open', kline[1])
        # 8 is index for volume, 2 is index for open price?
        pair_list.append(float(kline[2]))
        num_trades_list.append(float(kline[8]))
    
    mean_numberofTrades = statistics.mean(num_trades_list)
    number_of_trades_per_minutes[pair] = mean_numberofTrades
    
    if mean_numberofTrades < 16:
        continue
    print(f'Scanning --> {pair}')

    # Normalize
    amin, amax = min(pair_list), max(pair_list)
    for i, val in enumerate(pair_list):
        pair_list[i] = (val-amin) / (amax-amin)

    _ = pair_list
    pair_list = pd.Series(pair_list).rolling(window=n).mean().iloc[n-1:].values

    # Take the first derivative
    derv = diff(pair_list)

    average = sum(derv[-GETSOME:]) / len(derv[-GETSOME:])

    variance = statistics.variance(derv)
    standard_deviation = float(statistics.stdev(derv))

    # Nondimentional distance from the moving average
    dMA = sum(_[-GETSOME:]-pair_list[-GETSOME:]) / GETSOME

    scanner[pair] = [average, variance, standard_deviation, mean_numberofTrades, dMA]
    # _scanner = scanner

    # Sort the resulting according to second index ref on kv (key value). the forth represents distance from moving average.
    sorted_scan = sorted(scanner.items(), key=lambda kv: kv[1][4])

    # for i in _scanner:
    #     # pp.pprint(scanner[i])
    #     ii = [abs(float(iii))**-1 if iii != 0.0 else 0 for iii in _scanner[i] ]
    #     _scanner[i] = ii
    #     # pp.pprint(scanner[i])
    #     # assert 1 == 2
    # sorted_scan_closes_to_zero = sorted(_scanner.items(), key=lambda kv: kv[1][0])
    # print(sorted_scan_closes_to_zero)

    # Start printing lists only when we have enough
    if len(sorted_scan) > 10:
        print('LOWEST')
        pp.pprint([i[0] for i in sorted_scan[:10]])
        print('HIGHEST')
        pp.pprint([i[0] for i in sorted_scan[-10:]])
        # print('CLOSEST TO ZERO')
        # pp.pprint([i[0] for i in sorted_scan_closes_to_zero[-10:]])
    else:
        pp.pprint(sorted_scan)
    # pp.pprint(number_of_trades_per_minutes)
    # assert 1 == 2 
