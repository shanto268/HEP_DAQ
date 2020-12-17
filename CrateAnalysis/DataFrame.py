import pandas as pd
# import modin.pandas as pd
import feather
from LC3377 import *
import time
import os


class DataFrame:
    def __init__(self, runNumber):
        self.name = "events_data_frame_" + str(runNumber)
        # self.df0 = pd.DataFrame(
        # columns=['event_num', 'event_time', 'deadtime'])
        self.df0 = pd.DataFrame(columns=[
            'event_num', 'event_time', 'deadtime', 'ADC', 'TDC', 'Scaler',
            'l1hit', 'l2hit', 'l3hit', 'l4hit', 'r1hit', 'r2hit', 'r3hit',
            'r4hit'
        ])
        self.eventNum = 0
        self.eventTime = 0
        self.deadTime = 0
        self.ADC = []
        self.TDC = []
        self.Scaler = []
        self.data_dict = []
        self.l1 = 9
        self.l2 = 9
        self.l3 = 9
        self.l4 = 9
        self.r1 = 9
        self.r2 = 9
        self.r3 = 9
        self.r4 = 9
        if not os.path.exists('processed_data'):
            os.makedirs('processed_data')
        self.path = "processed_data/" + self.name + ".h5"

    def updateDataFrame(self, info, eventNum):
        self.data_dict.append(self.getDataDict(info, eventNum))
        # self.df0 = self.df0.append(data_dict, ignore_index=True)

    def getDataDict(self, info, eventNum):
        self.eventNum = eventNum
        self.eventTime = info.get('timeStamp')
        self.deadTime = info.get('deadtime')
        try:
            self.ADC = info.get((17, 'LeCroy2249'))
        except:
            self.ADC = None
        try:
            self.TDC = info.get("TDC").get("TDC")
            channels = [i[0] for i in self.TDC]
            # 1 is there, 0 is bad
            if 0 in channels:
                self.l1 = 1
            else:
                self.l1 = 0

            if 1 in channels:
                self.r1 = 1
            else:
                self.r1 = 0

            if 2 in channels:
                self.l2 = 1
            else:
                self.l2 = 0

            if 3 in channels:
                self.r2 = 1
            else:
                self.r2 = 0

            if 6 in channels:
                self.l3 = 1
            else:
                self.l3 = 0

            if 7 in channels:
                self.r3 = 1
            else:
                self.r3 = 0

            if 8 in channels:
                self.l4 = 1
            else:
                self.l4 = 0

            if 9 in channels:
                # print(channels)
                self.r4 = 1
            else:
                self.r4 = 0
        except:
            self.TDC = None
            self.l1 = None
            self.l2 = None
            self.l3 = None
            self.l4 = None
            self.r1 = None
            self.r2 = None
            self.r3 = None
            self.r4 = None
        try:
            self.Scaler = info.get((5, 'LeCroy2552'))
        except:
            self.Scaler = None

        event_dict = {
            'event_num': self.eventNum,
            'event_time': self.eventTime,
            'deadtime': self.deadTime,
            'ADC': self.ADC,
            'TDC': self.TDC,
            'Scaler': self.Scaler,
            'l1hit': self.l1,
            'l2hit': self.l2,
            'l3hit': self.l3,
            'l4hit': self.l4,
            'r1hit': self.r1,
            'r2hit': self.r2,
            'r3hit': self.r3,
            'r4hit': self.r4
        }
        return event_dict

    def showDataFrame(self):
        print(self.df0)
        # pass

    def showDataColumns(self):
        print(self.df0.columns)

    def getLC3377Definition(self, info):
        pass

    def LC3377Definition(self, slot, channel, info, invalidtdc):
        pass

    def trial(self, info):
        self.deadTime = info.get('deadtime')
        return {'deadTime': self.deadTime}

    def saveDataFrame(self):
        # start_time = time.time()
        # print("--- %s seconds ---" % (time.time() - start_time))
        # print("Saving the DataFrame....")
        self.df0 = pd.DataFrame.from_dict(self.data_dict)
        self.df0[[
            'SCh0', 'SCh1', 'SCh2', 'SCh3', 'SCh4', 'SCh5', 'SCh6', 'SCh7',
            'SCh8', 'SCh9', 'SCh10', 'SCh11'
        ]] = pd.DataFrame(
            self.df0['Scaler'].to_list(),
            index=self.df0.index,
        )
        self.df0.drop('Scaler', axis=1, inplace=True)
        # self.df0 = self.df0.drop(0)
        # self.df0.to_hdf(self.path, self.name, format="table")
        data_store = pd.HDFStore(self.path)
        data_store[self.name] = self.df0
        data_store.close()

    # data_store.append(self.name, self.df0, data_columns=True)
    # feather.write_dataframe(self.df0, self.path)
    # self.showDataFrame()
    # self.df0.to_feather(self.path)

    # with data_store as hdf:
    # hdf.put(key=self.name,
    # value=self.df0,
    # format='table',
    # data_columns=True)
