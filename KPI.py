data = open('Result/Record.csv').readlines()
data = [ i.strip('\n').split(',') for i in data ]

Position = {}    # 部位狀態
Record = []      # 進出場的交易紀錄

# 整理交易紀錄
for d in data:
    # 商品代碼、多空方向、日期、時間、價格、張數
    Prod,BS,Date,Time,Price,QTY = d
    for i in range(int(QTY)):
        # 該商品沒有部位
        if Prod not in Position.keys() or Position[Prod] == []:
            Position[Prod] = [[ Prod,BS,Date,Time,Price ]]
        # 該商品已有部位
        else:
            # 同方向
            if BS == Position[Prod][0][1]:
                Position[Prod].append([ Prod,BS,Date,Time,Price ])
            # 反方向
            else:
                # 商品代碼、多空方向、進場日期、進場時間、進場價格、出場日期、出場時間、出場價格
                Record.append( Position[Prod][0] + [Date,Time,Price] )
                del Position[Prod][0]

# 回測結束，檢查是否仍持有部位
Check = [ p for p in Position.keys() if Position[p] != [] ]
if Check != []:
    print('請將全數部位平倉，未平倉代碼:',Check)

# 記錄每筆損益
Profit = []
Return_Rate = []
for i in Record:
    OrderPrice = float(i[4])
    CoverPrice = float(i[7])
    fee = round(OrderPrice * 0.0005) + round(CoverPrice * 0.0005)
    # 多單
    if i[1] == 'B':
        P = CoverPrice-OrderPrice-fee
        Profit.append(P)
        Return_Rate.append(P/OrderPrice)
    # 空單
    elif i[1] == 'S':
        P = OrderPrice-CoverPrice-fee
        Profit.append(P)
        Return_Rate.append(P/OrderPrice)

# 獲利及虧損的資料
Win = [ i for i in Profit if i > 0 ]
Loss = [ i for i in Profit if i < 0 ]

# 總損益
Total_Profit = sum(Profit)
# 總交易次數
Total_Trade = len(Profit)
# 平均損益
Avg_Profit = Total_Profit / Total_Trade
# 勝率
Win_Rate = len(Win) / Total_Trade
# 獲利因子及賺賠比
if len(Loss) == 0:
    Profit_Factor = 'NA'
    Win_Loss_Rate = 'NA'
else:   
    Profit_Factor = sum(Win) / -sum(Loss)
    Win_Loss_Rate = (sum(Win)/len(Win)) / (-sum(Loss)/len(Loss))
# 最大資金回落
MDD,Capital,MaxCapital = 0,0,0
for p in Profit:
    Capital += p
    MaxCapital = max(MaxCapital,Capital)
    DD = MaxCapital - Capital
    MDD = max(MDD,DD)
# 夏普比率 (忽略無風險利率)
import numpy as np
Return_Rate = np.array(Return_Rate)
Sharpe_Ratio = np.mean(Return_Rate) / np.std(Return_Rate)

# 將績效指標匯出
file = open('Result/KPI.csv','w')
file.write(','.join(['總損益','總交易次數','平均損益','勝率','獲利因子','賺賠比','最大資金回落','夏普比率','是否超額交易','\n']))
file.write(','.join([str(Total_Profit),str(Total_Trade),str(Avg_Profit),str(Win_Rate),str(Profit_Factor),str(Win_Loss_Rate),str(MDD),str(Sharpe_Ratio)]))
file.close()
