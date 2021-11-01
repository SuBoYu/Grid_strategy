# 匯入套件
from finlab import crypto
import os
import pandas as pd
import numpy as np
import datetime as dt
import json

starttime = dt.datetime.now()

print("Begin...")

# 使用BTCUSDT1hr作為回測資料
data = pd.read_csv("history/crypto/BTCUSDT-1h-data.csv")
data = data.loc[:, ["Timestamp", "Close"]]

# data = data.iloc[144003:, :]
# data.reset_index(inplace=True, drop=True)


# 交易紀錄
Record = open('result/Record.csv', 'w')

# 交易的張數
QTY = '1'

# 初始資金 USDT
fund = 1000000

# 網格上下限，採用過去歷史最高最低價來設定
# auto_set == True => 用過去7天最高最低價來設置網格
# auto_set == False => 手動設置網格
auto_set = True
mid_grid_strategy = True
highest = 65000
lowest = 50000
mid = 0
setting_days = 168

# 網格數
n_grid = 100
return_grid = 0.005
grid_levels = list()
price_levels = list()
# 紀錄最後一個被跨躍的網格
last_price_index = None



# 逐日回測
for index, row in data.iloc[setting_days-1:].iterrows(): # 0 - 167 作為計算網格上界下界的標準

    # 日期
    Date = row["Timestamp"][:10]
    Prod = "BTC/USDT"
    Time = row["Timestamp"][11:]
    print(index)


    # init grid 用前7天的數據設定網格
    if index == setting_days-1:
        if auto_set == True:
            if mid_grid_strategy == True:
                highest = max(data.iloc[:setting_days]["Close"])
                lowest = min(data.iloc[:setting_days]["Close"])
                mid = (highest + lowest) / 2

                # 若可以開倉20單位，grid level要有21個界線
                grid_levels = [x for x in np.arange(1 + return_grid * n_grid/2, 1 - return_grid * n_grid/2 - return_grid/2, -return_grid)]
                price_levels = [mid * x for x in grid_levels]
                last_price_index = None
            else:
                highest = max(data.iloc[:setting_days]["Close"])
                lowest = min(data.iloc[:setting_days]["Close"])
                dif = (highest-lowest)/n_grid
                for i in np.arange(highest, lowest-dif, -dif):
                    price_levels.append(i)
                last_price_index = None

        else:
            dif = (highest - lowest) / n_grid
            for i in np.arange(highest, lowest-dif, -dif):
                price_levels.append(i)
            last_price_index = None



    # start grid strategy
    else:
        if last_price_index == None:
            for i in range(len(price_levels)):
                if row["Close"] > price_levels[i] and fund >= row["Close"]*i:
                    last_price_index = i
                    while i > 0:
                        Record.write(','.join([str(Prod), 'B', Date, Time, str(row["Close"]), QTY + '\n']))
                        fund -= row["Close"]
                        i -= 1
                    break
        else:
            while True:
                upper = None  # 要突破的上界
                lower = None  # 要跌破的下界

                if last_price_index > 0:
                    upper = price_levels[last_price_index - 1]

                if last_price_index < len(price_levels) - 1:
                    lower = price_levels[last_price_index + 1]

                # 突破上界，賣一單位
                if upper is not None and row["Close"] > upper:
                    last_price_index -= 1
                    Record.write(','.join([str(Prod), 'S', Date, Time, str(row["Close"]), QTY + '\n']))
                    fund += row["Close"]
                    continue

                # 跌破下界，買一單位
                if lower is not None and row["Close"] < lower and fund >= row["Close"]:
                    last_price_index += 1
                    Record.write(','.join([str(Prod), 'B', Date, Time, str(row["Close"]), QTY + '\n']))
                    fund -= row["Close"]
                    continue
                break

# 最後一天價格去強制平倉
row = data.iloc[-1]
Date = row["Timestamp"][:10]
Prod = "BTC/USDT"
Time = row["Timestamp"][11:]

# 最後全部強制平倉
while last_price_index > 0:
    last_price_index -= 1
    Record.write(','.join([str(Prod), 'S', Date, Time, str(row["Close"]), QTY + '\n']))

        
Record.close()
endtime = dt.datetime.now()
print("Process time:",endtime-starttime)
