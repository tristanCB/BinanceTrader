
# !/usr/bin/env python3
# %% BINANCE SCANNER
import asyncio
import tkinter as tk
import json
import pprint
import time
from datetime import datetime
from typing import Text
pp = pprint.PrettyPrinter(indent=4)
from importlib import reload
from numpy import diff
import statistics
import pandas as pd
import statistics
import trader
import webbrowser
import threading

# %%
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

# scanner = {}
# number_of_trades_per_minutes = {}

# best = None
# worst = None
# highest_variance = None
# highest_std_dev = None

# %%
class Application(tk.Frame):
    def perform_scan(self, binance_pair):
        print(f'Scanning --> {binance_pair}')

        pair_list = []
        num_trades_list = []
        klineDate = binance.get_kline_timeframe(binance_pair.strip("\n"), timeframe='1m')
        # pp.pprint(klineDate)

        for kline in klineDate:
            # print('open', kline[1])
            # 8 is index for volume, 2 is index for open price?
            pair_list.append(float(kline[2]))
            num_trades_list.append(float(kline[8]))
        
        mean_numberofTrades = statistics.mean(num_trades_list)

        # Normalize
        amin, amax = min(pair_list), max(pair_list)
        for i, val in enumerate(pair_list):
            pair_list[i] = (val-amin) / (amax-amin)
        _ = pair_list
        pair_list = pd.Series(pair_list).rolling(window=n).mean().iloc[n-1:].values

        # Take the first derivative
        derv = diff(pair_list)
        averageDerv = sum(derv[-GETSOME:]) / len(derv[-GETSOME:])
        varianceDerv = statistics.variance(derv)
        standard_deviationDerv = float(statistics.stdev(derv))
        # Nondimentional distance from the moving average
        dMA = sum(_[-GETSOME:]-pair_list[-GETSOME:]) / GETSOME

        return averageDerv, varianceDerv, standard_deviationDerv, dMA

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        for item in dict_object["unique_pairs"]:
            self.scan_results.insert("end",item+"\n")

        self.scan_results.bind('<Double-Button>', self.go_to)

    def create_widgets(self):
        # self.inputStonk = tk.Entry(self)
        # self.inputStonk.insert(0,"BNBTRY")
        # self.inputStonk.pack()

        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "scan"
        # self.hi_there["command"] = self.start_scan
        self.hi_there.pack(side="top")

        self.scan_results = tk.Listbox(self)
        self.scan_results.pack()

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    # def start_scan(self, event=None):
    #     print("Scanning Binance")
    #     ticker = self.inputStonk.get()
    #     results = [i for i in perform_scan(ticker)]
    #     print(results)
    #     # scan_results = tk.Label(text=results).pack()
    #     # scan_results = tk.scrolledtext()
    #     webbrowser.open(self.format_url(ticker),new=1)
    #     self.scan_results.insert("end","hey")

    def format_url(self, symbol, exchange="BINANCE"):
        return f"https://www.tradingview.com/chart/?symbol={exchange}:{symbol}"

    def go_to(self, callback):
        print(callback)
        for i in self.scan_results.curselection():
            dbl_clicked_ticker = self.scan_results.get(i)
            print(dbl_clicked_ticker)
            print(type(dbl_clicked_ticker))
        
            webbrowser.open(self.format_url(dbl_clicked_ticker),new=1)
            print(self.perform_scan(dbl_clicked_ticker))

root = tk.Tk()
app = Application(master=root)
app.mainloop()
