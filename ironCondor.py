import weeklyData
import pandas as pd
import datetime
import helper
import os
import traceback
from collections import namedtuple
from enum import IntEnum
from termcolor import colored
import math
from sys import platform

if platform == "win32":
    os.system('color')

class OptionsEnum(IntEnum):
    CE1 = 0
    PE1 = 1
    CE2 = 2
    PE2 = 3
class IronCondor:
    oe = OptionsEnum
    slotSize = 50
    defaultExitTime = datetime.time(15, 14, 59)
    defaultEntryTime = datetime.time(15, 14, 59)
    
    outputFileName = None
    brokerage = 20 * 2
    def __init__(self, stockName, outputFileName = "ironCondorAlgorithm.csv",  entryDay = None, entryTime = None, exitDay = None, exitTime = None):
        self.stockName = stockName
        self.entryDay = entryDay
        self.entryTime = entryTime
        self.exitDay = exitDay
        self.exitTime = exitTime
        IronCondor.outputFileName = self.setOutputFilename()

    def setOutputFilename(self):
        return f"icbt[{self.entryDay}({self.entryTime})-{self.exitDay}({self.exitTime})].csv"
    def calcEntryDate(self, week, prefDay):
        ret = None
        if prefDay is None:
            ret = week[0]
        else:
            wdli = helper.weekDaysList.index
            prefDayIndex = wdli(prefDay)
            for day in week:
                curDay = day['Day']
                curDayIndex = wdli(curDay)
                if curDayIndex >= prefDayIndex:
                    ret = day
                    break
            if ret is None:
                day_arr = []
                for day in week:
                    day_arr.append(wdli(day['Day']))
                if prefDayIndex < day_arr[0]:
                    ret = week[0]
                else:
                    ret = week[-1]
        return ret.Date.date()
    def calcExitDate(self, week, prefDay):
        ret = None
        if prefDay is None:
            ret = week[-1]
        else:
            wdli = helper.weekDaysList.index
            prefDayIndex = wdli(prefDay)
            for day in week:
                curDay = day['Day']
                curDayIndex = wdli(curDay)
                if curDayIndex <= prefDayIndex:
                    ret = day
            if ret is None:
                day_arr = []
                for day in week:
                    day_arr.append(wdli(day['Day']))
                if prefDayIndex < day_arr[0]:
                    ret = week[0]
                else:
                    ret = week[-1]
            
        return ret.Date.date()
    def calcEntryTime(self):
        if self.entryTime is None:
            self.entryTime = IronCondor.defaultEntryTime
        return self.entryTime

    def calcExitTime(self):
        if self.exitTime is None:
            self.exitTime = IronCondor.defaultExitTime
        return self.exitTime

    def selectPriceFromDF(df, ticker, time):
        select = None
        timecopy = time
        #time to reduce each iter
        td = datetime.time(0,0,1)
        while True:
            selectTicker = df[(df["Ticker"] == ticker)]
            #if selectTicker.empty:
            #    raise
            
            selectTime = selectTicker[(selectTicker["Time"] == str(timecopy))]
            select = selectTime['Close']

            if len(select.values) == 0:
                oldTime = timecopy
                timecopy = datetime.datetime.combine(datetime.date.min, timecopy) - datetime.datetime.combine(datetime.date.min, td)
                timecopy = (datetime.datetime.min + timecopy).time()
                print(f"\t\t{oldTime} for {ticker} not found. using:{str(timecopy)}", end="\r")

            else:
                break
        
        return [select.values[0], timecopy]



    def loadPrices(self, dates, strikePrices):
        symbol = "NFO"
        #day, yearstripped, year, month, monthnum, year
        dateDataTuple = namedtuple("dateDataTuple", ["day", "year", "yearStripped", "month", "monthNum"])
        class dateIdEnum(IntEnum):
            ENTRY = 0
            EXIT = 1
        dateData = []
        for d in dates:
            dateData.append(
                dateDataTuple(
                    "{:02d}".format(d.day),
                    d.year,
                    str(d.year)[-2:],
                    helper.Month[d.month - 1],
                    "{:02d}".format(d.month)
                )
            )
        ##generate tickers
        tickers = []
        date = dateData[dateIdEnum.EXIT] #dateData[1] is the exitDay
#        for date in dates:
            #NIFTY03FEB22171800PE.NFO
        for idx, strikePrice in enumerate(strikePrices):
            optionType = None
            if idx % 2 == 0:
                optionType = "CE"
            else:
                optionType = "PE"
            stock_id = f"{self.stockName}{date.day}{date.month}{date.yearStripped}{strikePrice}{optionType}.{symbol}"
            tickers.append(stock_id)

        ##get data from files
        extension = "csv"
        fileNamePrefix = "GFDL"
        data_dir = f"{self.stockName}_OPTIONS_DATA"
        entryPrices = []
        exitPrices = []
        selectedEntryTime = []
        selectedExitTime = []
        for i, dd in enumerate(dateData):
            month_dir = f"{dd.month}_{dd.year}"
            fileName = f"{fileNamePrefix}{symbol}_OPTIONS_{dd.day}{dd.monthNum}{dd.year}.{extension}"
            filePath = os.path.join(data_dir, month_dir, fileName)
            Time = None
            try:
                df = pd.read_csv(filePath)
                debugInfo = [None, None, None]
                if i == dateIdEnum.ENTRY:
                    debugInfo[0] = "Entry"
                    Time = self.entryTime
                    debugInfo[1] = Time
                    for ticker in tickers:
                        debugInfo[2] = ticker
                        [price, t] = IronCondor.selectPriceFromDF(df, ticker, Time)
                        selectedEntryTime.append(t)
                        entryPrices.append(price)
                elif i == dateIdEnum.EXIT:
                    debugInfo[0] = "Exit"
                    Time = self.exitTime
                    debugInfo[1] = Time

                    for ticker in tickers:
                        debugInfo[2] = ticker 
                        [price, t] = IronCondor.selectPriceFromDF(df, ticker, Time)
                        exitPrices.append(price)
                        selectedExitTime.append(t)
            except Exception as e:
                #traceback.print_exc()
                #err in NIFTY11AUG2216850PE.NFO 15:14:59 doesnt exist
                print(e)
                dbgInfo = f"Fail: {debugInfo[0]} [{debugInfo[2]},{debugInfo[1]}] does not exist in {filePath}" 
                print(colored(dbgInfo, "red"))
                print(colored("Skipping", "green"))
            
        return [entryPrices, exitPrices, tickers, selectedEntryTime, selectedExitTime]
    def calcSpread(entryPrices):
            oe = IronCondor.oe
            return (
                entryPrices[oe.CE1]
                +entryPrices[oe.PE1]
                -(
                    entryPrices[oe.CE2]
                    +entryPrices[oe.PE2]
                )
            )
    def _calcProfit(exitPrice, entryPrice, sell):
        net = exitPrice - entryPrice
        net = net * IronCondor.slotSize
        if sell is True:
            net = net * - 1
        return net
    def calcProfits(self, exitPrices, entryPrices):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
            if i < oe.CE2: #sell
                ret.append(IronCondor._calcProfit(exitPrices[i], entryPrices[i], True))
            else: #buy
                ret.append(IronCondor._calcProfit(exitPrices[i], entryPrices[i], False))
        return ret
    def calcSctt(self, exitPrices, entryPrices):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
            if i < oe.CE2: #sell
                ret.append(
                    entryPrices[i] * 50 * 0.05 * 0.01
                )
            else: #buy
                ret.append(
                    exitPrices[i] * 50 * 0.05 * 0.01
                )
        return ret

    def calcTC(exitPrices, entryPrices):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
            ret.append(50 * 0.053 * 0.01 * (exitPrices[i] + entryPrices[i]))
        return ret        

    def calcSEBI(exitPrices, entryPrices):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
             ret.append((10/10000000)*(entryPrices[i]+exitPrices[i])*50)
        return ret

    def calcGST(sebi, tc):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
            ret.append((sebi[i] + tc[i] + IronCondor.brokerage) * 18 * 0.01 )
        return ret
    def calcStampCharges(entryPrices, exitPrices):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
            if i < oe.CE2: #sell
                ret.append(
                    exitPrices[i] * 0.003 * 0.01
                )
            else: #buy
                ret.append(
                    entryPrices[i] * 0.003 * 0.01
                )
        return ret
    def calcTotalCost(sctt, tc, sebi, gst, stamp):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
                ret.append(
                    sctt[i] + tc[i] + sebi[i] + gst[i] + stamp[i]
                )
        return ret

    def calcNetProfits(profits, totalCost):
        ret = []
        oe = IronCondor.oe
        for i in range(0, oe.PE2 + 1):
            ret.append(
                profits[i] - (IronCondor.brokerage + totalCost[i])
            )
        return ret

    def addRowDF(df, data):
        pass

    def calcDrawDown(sumCol):
        drawdown = []
        dd_val = 0
        for i, val in enumerate(sumCol):
            if pd.isna(val):
                drawdown.append(math.nan)
            else:
                dd_val += val
                if dd_val >= 0:
                    dd_val = 0
                drawdown.append(dd_val)

        return drawdown
                    
                
    def testEntry():
        df = pd.read_csv("ic-backtest.csv", parse_dates=["WeekBeginDate"])
        dd = IronCondor.calcDrawDown(df['Sum'])
        exit()

    def stoploss(self):
        #if os.path.exists(IronCondor.outputFileName):
        #    return [pd.read_csv(IronCondor.outputFileName), IronCondor.outputFileName]
        weeklyData_tup = weeklyData.createWeeklyData(self.stockName)
        wd = weeklyData_tup[0]
        weeks = weeklyData_tup[1]
        for idx, data in wd.iterrows():
            progress = '{:.2f}'.format(100 * idx/len(wd))
            print(f"Progress: {progress}", end="\n")
            weekBegin = weeks[idx][0]['Date'].date()
            weekExpiry = weeks[idx][-1]['Date'].date()
            try:
                #set entry date
                entryDate = self.calcEntryDate(weeks[idx], self.entryDay)
                #set exit date
                exitDate = self.calcExitDate(weeks[idx], self.exitDay)
                entryTime = self.calcEntryTime()
                exitTime = self.calcExitTime()
            except Exception as e:
                print(e)
                dbgInfo = f"Fail: Perhaps day {self.entryDay or self.exitDay} not in week #{idx}"
                print(colored(dbgInfo, "red", "on_white"))
                print(pd.DataFrame(weeks[idx]))
            optionStrikePrices = [
                data['CE1'],
                data['PE1'],
                data['CE2'],
                data['PE2'],
            ]
            #get prices based on stockname, date, optiontype
            try:
                oe = IronCondor.oe
                [entryPrices, exitPrices, tickers, entT, extT] = self.loadPrices([entryDate, exitDate], optionStrikePrices)
                #calculate the profits
                profits = self.calcProfits(exitPrices, entryPrices)
                print(profits)
            except:
                pass
        
    def ironCondorAlgorithm(self):
        # IronCondor.testEntry()
        if os.path.exists(IronCondor.outputFileName):
            return [pd.read_csv(IronCondor.outputFileName), IronCondor.outputFileName]
        weeklyData_tup = weeklyData.createWeeklyData(self.stockName)
        wd = weeklyData_tup[0]
        weeks = weeklyData_tup[1]
        df = pd.DataFrame(columns=[
            "WeekBeginDate", #
            "WeekBeginDay",#
            "WeekExpiryDate",#
            "WeekExpiryDay",#
            "EntryDate", #
            "EntryDay",#
            "EntryTime",#
            "ExitDate",#
            "ExitDay",#
            "ExitTime",#
            "Ticker",
            "EntryPrice",
            "Spread", #
            "ExitPrice",
            "Profit", #
            "Sum", #
            "WeekCumulative",
            "SCTT",
            "TC",
            "SEBI",
            "GST",
            "Stamp",
            "TotalCost",
            "NetProfit",
            "NetCumulative",
        ])

        for idx, data in wd.iterrows():
            progress = '{:.2f}'.format(100 * idx/len(wd))
            print(f"Progress: {progress}", end="\n")
            weekBegin = weeks[idx][0]['Date'].date()
            weekExpiry = weeks[idx][-1]['Date'].date()
            try:
                #set entry date
                entryDate = self.calcEntryDate(weeks[idx], self.entryDay)
                #set exit date
                exitDate = self.calcExitDate(weeks[idx], self.exitDay)
                entryTime = self.calcEntryTime()
                exitTime = self.calcExitTime()
            except Exception as e:
                print(e)
                dbgInfo = f"Fail: Perhaps day {self.entryDay or self.exitDay} not in week #{idx}"
                print(colored(dbgInfo, "red", "on_white"))
                print(pd.DataFrame(weeks[idx]))
            optionStrikePrices = [
                data['CE1'],
                data['PE1'],
                data['CE2'],
                data['PE2'],
            ]
            #get prices based on stockname, date, optiontype
            try:
                oe = IronCondor.oe
                [entryPrices, exitPrices, tickers, entT, extT] = self.loadPrices([entryDate, exitDate], optionStrikePrices)
                #calculate the profits
                profits = self.calcProfits(exitPrices, entryPrices)
                weekProfitNet = sum(profits) #sum column in weekly
                sctt = self.calcSctt(exitPrices, entryPrices)
                tc = IronCondor.calcTC(exitPrices, entryPrices)
                sebi = IronCondor.calcSEBI(exitPrices, entryPrices)
                gst = IronCondor.calcGST(sebi, tc)
                stamp = IronCondor.calcStampCharges(entryPrices, exitPrices)
                totalCost = IronCondor.calcTotalCost(sctt, tc, sebi, gst, stamp)
                netProfits = IronCondor.calcNetProfits(profits, totalCost)

                #add first row of four
                entry = oe.CE1
                data = [
                    weekBegin,
                    wd.loc[idx]['FirstDay'],
                    weekExpiry,
                    wd.loc[idx]['LastDay'],
                    entryDate,
                    helper.weekDaysListNormal[entryDate.weekday()],
                    #self.entryTime,
                    entT[entry], #7
                    exitDate,
                    helper.weekDaysListNormal[exitDate.weekday()],
                    extT[entry], #10
                    tickers[entry],
                    entryPrices[entry],
                    None,
                    exitPrices[entry],
                    profits[entry],
                    None, #week profit net only to be printed in PE2
                    None, #cumulative weekly
                    sctt[entry],
                    tc[entry],
                    sebi[entry],
                    gst[entry],
                    stamp[entry],
                    totalCost[entry],
                    netProfits[entry],
                    None, #net cumulative
                ]
                df.loc[len(df)] = data
                #second row
                entry = oe.PE1
                data = [
                    None, None, None, None, None, None,
                    entT[entry],
                    None, None,
                    extT[entry],
                    tickers[entry],
                    entryPrices[entry],
                    None,
                    exitPrices[entry],
                    profits[entry],
                    None, #week profit net only to be printed in PE2
                    None, #cumulative weekly
                    sctt[entry],
                    tc[entry],
                    sebi[entry],
                    gst[entry],
                    stamp[entry],
                    totalCost[entry],
                    netProfits[entry],
                    None, #net cumulative

                ]
                df.loc[len(df)] = data
                #third row
                entry = oe.CE2
                data = [
                    None, None, None, None, None, None,
                    entT[entry],
                    None, None,
                    extT[entry],
                    tickers[entry],
                    entryPrices[entry],
                    None,
                    exitPrices[entry],
                    profits[entry],
                    None, #week profit net only to be printed in PE2
                    None, #cumulative weekly
                    sctt[entry],
                    tc[entry],
                    sebi[entry],
                    gst[entry],
                    stamp[entry],
                    totalCost[entry],
                    netProfits[entry],
                    None, #net cumulative

                ]
                df.loc[len(df)] = data
                #fourth row
                entry = oe.PE2
                data = [
                    None, None, None, None, None, None,
                    entT[entry],
                    None, None,
                    extT[entry],
                    tickers[entry],
                    entryPrices[entry],
                    IronCondor.calcSpread(entryPrices),
                    exitPrices[entry],
                    profits[entry],
                    weekProfitNet,
                    None, #cumulative weekly
                    sctt[entry],
                    tc[entry],
                    sebi[entry],
                    gst[entry],
                    stamp[entry],
                    totalCost[entry],
                    netProfits[entry],
                    None, #net cumulative
                ]
                df.loc[len(df)] = data
            except IndexError as ie:
                #print(ie)
                print(colored(f"Week: #{idx}", "light_red"))
            except Exception as e:
                print(e)
                traceback.print_exception(e)
                dbgInfo = "Fail (Probably value missing): Week#"+ str(idx)
                print(colored(dbgInfo, "red"))

        #set weekly sum cumulative
        weekCumulative = []
        adder = 0
        profit = df['Profit']
        for idx, p in enumerate(profit):
            adder += p
            weekCumulative.append(adder)
        df['WeekCumulative'] = weekCumulative
        #set total cumulateive
        netCumulative = []
        netProfit = df['NetProfit']
        adder = 0
        for p in netProfit:
            adder += p
            netCumulative.append(adder)
        df['NetCumulative'] = netCumulative
        #calculate weekly drawdown
        drawDown = IronCondor.calcDrawDown(df['Sum'])
        df['Drawdown'] = drawDown
        
        #write df to file
        df.to_csv(IronCondor.outputFileName, index=False)
        dbgInfo = "Generated " + IronCondor.outputFileName
        print(colored(dbgInfo, "white", "on_blue"))
        return [df, IronCondor.outputFileName]
