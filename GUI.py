
# !/usr/bin/env python3
# %% BINANCE SCANNER
import asyncio
import tkinter as tk
import json
import pprint
import time
from datetime import datetime
from tkinter.constants import W
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
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

class Application(tk.Frame):
    # Get a file object with write permission.
    def perform_scan(self, binance_pair):
        binance_pair = binance_pair.strip("\n").split(" ")[0] 
        print(f'Scanning --> {binance_pair} with param: n = {self.n}, GETSOME = {self.GETSOME}')
        # assert 1 == 2
        pair_list = []
        num_trades_list = []
        klineDate = self.binance.get_kline_timeframe(binance_pair, timeframe='1m')
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
        pair_list = pd.Series(pair_list).rolling(window=self.n).mean().iloc[self.n-1:].values

        # Take the first derivative
        derv = diff(pair_list)
        averageDerv = sum(derv[-self.GETSOME:]) / len(derv[-self.GETSOME:])
        varianceDerv = statistics.variance(derv[-self.GETSOME:])
        standard_deviationDerv = float(statistics.stdev(derv[-self.GETSOME:]))
        # Nondimentional distance from the moving average
        dMA = sum(_[-self.GETSOME:]-pair_list[-self.GETSOME:]) / self.GETSOME

        return averageDerv, varianceDerv, standard_deviationDerv, dMA

    def format_url(self, symbol, exchange="BINANCE"):
        return f"https://www.tradingview.com/chart/?symbol={exchange}:{symbol}"

    def go_to(self, callback):
        print(callback)
        for i in callback.widget.curselection():
            dbl_clicked_ticker = callback.widget.get(i).strip("\n").split(" ")[0] 
            print(dbl_clicked_ticker)
            print(type(dbl_clicked_ticker))
            webbrowser.open(self.format_url(dbl_clicked_ticker),new=1)
            print(self.perform_scan(dbl_clicked_ticker))

    # def concurent_request(self, input_tickers):
    #     with ThreadPoolExecutor(max_workers = 3) as executor:
    #         results = executor.map(self.perform_scan, input_tickers)
    #     # for result in results:
    #     #     print(result)

    def start_scan(self, tickers):
        _counter = 0
        # chunks = 10
        # groupped_tickers = [self.dict_object_tickers["unique_pairs"][i * chunks:(i + 1) * chunks] for i in range((len(self.dict_object_tickers["unique_pairs"]) + chunks - 1) // chunks )]
        # for i in groupped_tickers:
        #     self.topppers.delete(0,'end')
        #     self.lowwers.delete(0,'end')
        #     self.concurent_request(i)

        #     print(f"Sorting on {self.index_to_sort}")
        #     sorted_scan = sorted(self.scan_log.items(), key=lambda kv: kv[1][self.index_to_sort])
        #     for i in sorted_scan[:10]:
        #         self.topppers.insert('end', f"{i[0]} --> {i[1][self.index_to_sort]}")
            
        #     for i in sorted_scan[-10:]:
        #         self.lowwers.insert('end', f"{i[0]} --> {i[1][self.index_to_sort]}")

        #     # _counter = 0

        for i in tickers:
            ticker_result = self.perform_scan(i)
            self.scan_log[i] = ticker_result
            formatted_string_log = f'Scanned {i} --> {ticker_result}'
            # print(formatted_string_log)
            self.console.insert(0,formatted_string_log)
            _counter += 1

            if _counter > 10:
                self.topppers.delete(0,'end')
                self.lowwers.delete(0,'end')
                print(f"Sorting on {self.index_to_sort}")
                sorted_scan = sorted(self.scan_log.items(), key=lambda kv: kv[1][self.index_to_sort])
                for i in sorted_scan[:10]:
                    self.topppers.insert('end', f"{i[0]} --> {i[1][self.index_to_sort]}")
                
                for i in sorted_scan[-10:]:
                    self.lowwers.insert('end', f"{i[0]} --> {i[1][self.index_to_sort]}")

                _counter = 0

    def clear_run_anew(self):
        self.topppers.delete(0,'end')
        self.lowwers.delete(0,'end')
        self.console.delete(0,'end')
        self.scan_log = {}
        self.GETSOME = int(self.input_timeframe.get())
        self.input_movingSmotthing = int(self.input_timeframe.get())
        self.run_full()

    def run_full(self):
        chunks = 100
        ticker_threads = [self.dict_object_tickers["unique_pairs"][i * chunks:(i + 1) * chunks] for i in range((len(self.dict_object_tickers["unique_pairs"]) + chunks - 1) // chunks )]
        print(len(ticker_threads))
        # assert 1 == 2
        for i in ticker_threads:
            threading.Thread(target=self.start_scan, args=(i,)).start()

    def selection(self):
        selection = "You selected the option " + str(self.index_to_sort_on.get())
        self.SORT_ON = self.index_to_sort_on.get()
        self.clear_run_anew()

        print(selection)

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        master.title("Binance Scanner")
        # master.geometry("500x400")
        # master.grid_rowconfigure(0, weight=1)
        # master.grid_columnconfigure(0, weight=1)
        # Stores results
        self.scan_log = {}

        self.file_object = open('binance_pairs.txt', 'r')
        # Load JSON file data to a python dict object.
        self.dict_object_tickers = json.load(self.file_object)
        # Apply rolling windows as smoothing
        self.n = 120
        # Use this as timeframe for trading. --> 
        self.GETSOME = 10
        self.index_to_sort = 3

        reload(trader)
        # Create the 
        self.binance = trader.biance_api()

        self.grid()
        self.create_widgets()
        self.all_tickers_listbox.bind('<Double-Button>', self.go_to)
        self.topppers.bind('<Double-Button>', self.go_to)
        self.lowwers.bind('<Double-Button>', self.go_to)

        self.run_full()

    def create_widgets(self):

        self.settings = tk.Frame(self)
        self.settings.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.input_timeframe_label = tk.Label(self.settings, text="Timeframe (mins)")
        self.input_timeframe_label.pack(side="left")

        self.input_timeframe = tk.Entry(self.settings)
        self.input_timeframe.insert(0,"10")
        self.input_timeframe.pack(side="left")

        self.input_movingSmotthing_label = tk.Label(self.settings, text="Moving average smotthing (mins)")
        self.input_movingSmotthing_label.pack(side="left")

        self.input_movingSmotthing = tk.Entry(self.settings)
        self.input_movingSmotthing.insert(0,"120")
        self.input_movingSmotthing.pack(side="left")

        self.rerun_button = tk.Button(self.settings, text="Restart Scan", fg="purple", command=self.clear_run_anew)
        self.rerun_button.pack(side="left")

        self.settings_main = tk.Frame(self)
        self.settings_main.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.index_to_sort_on = tk.IntVar()
        self.R1 = tk.Radiobutton(self.settings_main, text="Distance from moving average (non dimentional)", variable=self.index_to_sort_on, value=3, command=self.selection)
        self.R1.pack(side="left")
        self.R2 = tk.Radiobutton(self.settings_main, text="First derivative (Averaged over timeframe)", variable=self.index_to_sort_on, value=1, command=self.selection)
        self.R2.pack(side="left")
        self.R3 = tk.Radiobutton(self.settings_main, text="Variance of derivative (Averaged over timeframe)", variable=self.index_to_sort_on, value=2, command=self.selection)
        self.R3.pack(side="left")
        self.index_to_sort_on.set(3)

        self.quit = tk.Button(self.settings, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="left")

        self.all_tickers_listbox = tk.Listbox(self, width=50)
        self.all_tickers_listbox.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.yScroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.yScroll.grid(row=0, column=0, rowspan=2, sticky=tk.NE+tk.S)
        self.yScroll['command'] =  self.all_tickers_listbox.yview

        for item in self.dict_object_tickers["unique_pairs"]:
            self.all_tickers_listbox.insert("end",item+"\n")

        self.topppers = tk.Listbox(self, width=50)
        self.topppers.grid(row=0, column=1, sticky="nsew")

        self.lowwers = tk.Listbox(self)
        self.lowwers.grid(row=1, column=1, sticky="nsew")

        self.console = tk.Listbox(self)
        self.console.grid(row=2, column=0, columnspan=2 ,sticky="nsew")
        self.yScroll_console = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.yScroll_console.grid(row=2, column=1,columnspan=2, sticky=tk.NE+tk.S)
        self.yScroll_console['command'] =  self.console.yview
        
root = tk.Tk()
app = Application(master=root)
app.mainloop()

# %%
