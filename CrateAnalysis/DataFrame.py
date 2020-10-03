import pandas as pd
import feather


class DataFrame:
    def __init__(self, runNumber):
        self.name = "events_data_frame_" + str(runNumber)
        self.df0 = pd.DataFrame(columns=[
            'event_time', 'deadtime', 'TDC_L1_L', 'TDC_L1_R', 'TDC_L2_L',
            'TDC_L2_R', 'numChannelsRead', 'L1_asym', 'L2_asym', 'L1_TDC_sum',
            'L2_TDC_sum', 'L1_TDC_diff', 'L2_TDC_diff'
        ])
        self.eventTime = 0
        self.deadTime = 0
        self.TDC_L1_L = 0
        self.TDC_L1_R = 0
        self.TDC_L2_L = 0
        self.TDC_L2_R = 0
        self.ADC = []
        self.numChannelsRead = 0
        self.L1_asym = 0
        self.L2_asym = 0
        self.L1_TDC_sum = 0
        self.L2_TDC_sum = 0
        self.L1_TDC_diff = 0
        self.L2_TDC_diff = 0
        self.path = "processed_data/" + self.name + ".ftr"

    def updateDataFrame(self, info):
        data_dict = self.getDataDict(info)
        self.df0 = self.df0.append(data_dict, ignore_index=True)

    def getDataDict(self, info):
        self.eventTime = info.get('timeStamp')
        self.deadTime = info.get('deadtime')
        try:
            self.TDC_L1_L = info.get('unpacked3377Data').get((2, 0))
        except:
            self.TDC_L1_L = None
        try:
            self.TDC_L1_R = info.get('unpacked3377Data').get((2, 1))
        except:
            self.TDC_L1_R = None
        try:
            self.TDC_L2_L = info.get('unpacked3377Data').get((2, 3))
        except:
            self.TDC_L2_L = None
        try:
            self.TDC_L2_R = info.get('unpacked3377Data').get((2, 4))
        except:
            self.TDC_L2_R = None
        try:
            self.ADC = info.get((17, 'LeCroy2249'))
        except:
            self.ADC = None
        try:
            self.numChannelsRead = info.get('len_unpacked_3377Data')
        except:
            self.numChannelsRead = None
        try:
            self.L1_asym = info.get('TDCAnalyzer').get('Layer1asym')
        except:
            self.L1_asym = None
        try:
            self.L2_asym = info.get('TDCAnalyzer').get('Layer2asym')
        except:
            self.L2_asym = None
        try:
            self.L1_TDC_sum = info.get('Layer_1').get('add_TDC')
        except:
            self.L1_TDC_sum = None
        try:
            self.L2_TDC_sum = info.get('Layer_2').get('add_TDC')
        except:
            self.L2_TDC_sum = None
        try:
            self.L1_TDC_diff = info.get('Layer_1').get('sub_TDC')
        except:
            self.L1_TDC_diff = None
        try:
            self.L2_TDC_diff = info.get('Layer_2').get('sub_TDC')
        except:
            self.L2_TDC_diff = None
        event_dict = {
            'time': self.eventTime,
            'deadtime': self.deadTime,
            'TDC_L1_L': self.TDC_L1_L,
            'TDC_L1_R': self.TDC_L1_R,
            'TDC_L2_L': self.TDC_L2_L,
            'TDC_L2_R': self.TDC_L2_R,
            'ADC': self.ADC,
            'numChannelsRead': self.numChannelsRead,
            'L1_asym': self.L1_asym,
            'L2_asym': self.L2_asym,
            'L1_TDC_sum': self.L1_TDC_sum,
            'L2_TDC_sum': self.L2_TDC_sum,
            'L1_TDC_diff': self.L1_TDC_diff,
            'L2_TDC_diff': self.L2_TDC_diff
        }
        return event_dict

    def showDataFrame(self):
        print(self.df0)
        # pass

    def trial(self, info):
        self.deadTime = info.get('deadtime')
        return {'deadTime': self.deadTime}

    def saveDataFrame(self):
        self.df0.to_feather(self.path)
