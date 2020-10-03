# -*- coding: utf-8 -*-
"""
@author: Sadman Ahmed Shanto.
@date: 10/02/2020
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class Analyzer():
    """Docstring for Analyzer. """
    def __init__(self):
        """TODO: to be defined. """
        self.runNumber = 0
        self.timeEvent = ""
        self.eventNumber = 0
        self.TDC = {}
        self.ADC = {}
        self.x_asym = 0.0
        self.y_asym = 0.0
        self.deadTime = 0.0
        self.TDC_ch0 = []

    # function definitions
    def getData(self):
        """TODO: Docstring for getData.
        :returns: TODO

        """
        pass

    def createDataFrame(self):
        """TODO: Docstring for createDataFrame.
        :returns: TODO

        """
        pass

    def simulateCAMAC(self):
        """TODO: Docstring for simulateCAMAC.

        :arg1: TODO
        :returns: TODO

        """
        pass

    def saveFile(self):
        """TODO: Docstring for saveFile.
        :returns: TODO

        """
        pass


# main function
if __name__ == "__main__":
    a = Analyzer()
