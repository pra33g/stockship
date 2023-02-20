import weeklyData
import pandas as pd
import datetime
import helper
import os
import traceback
from collections import namedtuple
from enum import IntEnum
from termcolor import colored

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
        IronCondor.outputFileName = outputFileName

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
        for i, dd in enumerate(dateData):
            month_dir = f"{dd.month}_{dd.year}"
            fileName = f"{fileNamePrefix}{symbol}_OPTIONS_{dd.day}{dd.monthNum}{dd.year}.{extension}"
            filePath = os.path.join(data_dir, month_dir, fileName)
            try:
                df = pd.read_csv(filePath)
            except:
                raise
            
            Time = None
            try:
                debugInfo = [None, None, None]
                if i == dateIdEnum.ENTRY:
                    debugInfo[0] = "Entry"
                    Time = self.entryTime
                    debugInfo[1] = Time
                    for ticker in tickers:
                        debugInfo[2] = ticker
                        entryPrices.append(df[(df["Ticker"] == ticker) & (df["Time"] == str(Time))]['Close'].values[0])
                elif i == dateIdEnum.EXIT:
                    debugInfo[0] = "Exit"
                    Time = self.exitTime
                    debugInfo[1] = Time

                    for ticker in tickers:
                        debugInfo[2] = ticker
                        exitPrices.append(df[(df["Ticker"] == ticker) & (df["Time"] == str(Time))]['Close'].values[0])

            except Exception as e:
                #traceback.print_exc()
                #err in NIFTY11AUG2216850PE.NFO 15:14:59 doesnt exist
                #print(e)
                dbgInfo = f"Fail: [{debugInfo[2]},{debugInfo[1]}] does not exist in {filePath}" 
                print(colored(dbgInfo, "red"))
                print(colored("Skipping", "green"))
            
        return [entryPrices, exitPrices, tickers]
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
            sebi[i] + tc[i] + IronCondor.brokerage
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
    def addRowDF(df, data):
        pass

    def ironCondorAlgorithm(self):
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
            "Cumulative",
        ])

        for idx, data in wd.iterrows():
            progress = '{:.2f}'.format(100 * idx/len(wd))
            print(f"Progress: {progress}", end="\r")
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
                [entryPrices, exitPrices, tickers] = self.loadPrices([entryDate, exitDate], optionStrikePrices)
                #calculate the profits
                profits = self.calcProfits(exitPrices, entryPrices)
                weekProfitNet = sum(profits) #sum column in weekly
                sctt = self.calcSctt(exitPrices, entryPrices)
                tc = IronCondor.calcTC(exitPrices, entryPrices)
                sebi = IronCondor.calcSEBI(exitPrices, entryPrices)
                gst = IronCondor.calcGST(sebi, tc)
                stamp = IronCondor.calcStampCharges(entryPrices, exitPrices)
                

                print(sebi)
                
                input()


                
                #add first row of four
                data = [
                    weekBegin,
                    wd.loc[idx]['FirstDay'],
                    weekExpiry,
                    wd.loc[idx]['LastDay'],
                    entryDate,
                    helper.weekDaysListNormal[entryDate.weekday()],
                    self.entryTime,
                    exitDate,
                    helper.weekDaysListNormal[exitDate.weekday()],
                    self.exitTime,
                    tickers[oe.CE1],
                    entryPrices[oe.CE1],
                    None,
                    exitPrices[oe.CE1],
                    profits[oe.CE1],
                    None, None,
                ]
                df.loc[len(df)] = data
                #second row
                data = [
                    None, None, None, None, None, None, None, None, None, None,
                    tickers[oe.PE1],
                    entryPrices[oe.PE1],
                    None,
                    exitPrices[oe.PE1],
                    profits[oe.PE1],
                    None, None,
                ]
                df.loc[len(df)] = data
                #third row
                data = [
                    None, None, None, None, None, None, None, None, None, None,
                    tickers[oe.CE2],
                    entryPrices[oe.CE2],
                    None,
                    exitPrices[oe.CE2],
                    profits[oe.CE2],
                    None, None,
                ]
                df.loc[len(df)] = data
                #fourth row
                data = [
                    None, None, None, None, None, None, None, None, None, None,
                    tickers[oe.PE2],
                    entryPrices[oe.PE2],
                    IronCondor.calcSpread(entryPrices),
                    exitPrices[oe.PE2],
                    profits[oe.PE2],
                    None, None,
                ]
                df.loc[len(df)] = data
            except IndexError as ie:
                #print(ie)
                print(colored(f"Week: #{idx}", "light_red"))
            except Exception as e:
                print(e)
                dbgInfo = "Fail (Probably value missing): Week#"+ str(idx)
                print(colored(dbgInfo, "red"))
            
        df.to_csv(IronCondor.outputFileName, index=False)
        dbgInfo = "Generated " + IronCondor.outputFileName
        print(colored(dbgInfo, "white", "on_light_blue"))
