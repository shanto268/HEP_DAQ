import math
import matplotlib.pyplot as plt

class _ChannelHisto:
    def __init__(self, nBins, dutyCycle, vAdj, hardwareModule,
                 slotsConfigName, xlabel, channels_to_plot):
        self.nBins = nBins
        self.dutyCycle = dutyCycle
        self.vAdj = vAdj
        self.hardwareModule = hardwareModule
        self.slotsConfigName = slotsConfigName
        self.chanToPlot = channels_to_plot
        self.xlabel = xlabel

    def beginJob(self, allModuleNames):
        pass

    def _filterChannels(self, toPlot, slots):
        if toPlot is None:
            filtered = None
        else:
            filtered = []
            for id in toPlot:
                slot, channel = id
                if slot in slots:
                    filtered.append(id)
            if len(filtered) == 0:
                filtered = None
        return filtered

    def beginRun(self, runNumber, runRecord):
        self.runNumber = runNumber
        runConfig = runRecord[(runNumber, "runConfiguration")]
        self.slots = runConfig[self.slotsConfigName]
        self.eventCounter = 0
        toPlot = self.chanToPlot
        if toPlot is None:
            if "connected_channels" in runConfig:
                toPlot = runConfig["connected_channels"]
        self.toPlot = self._filterChannels(toPlot, self.slots)
        self.plotData = dict()
        if not (self.toPlot is None):
            for id in self.toPlot:
                self.plotData[id] = []
            plt.ion()
            self._makePlots()

    def processEvent(self, runNumber, eventNumber, eventRecord):
        if not (self.toPlot is None):
            self._updateData(eventNumber, eventRecord)
        self.eventCounter += 1
        if self.dutyCycle > 1:
            if eventNumber % self.dutyCycle != self.dutyCycle - 1:
                return
        if not (self.toPlot is None):
            self._updatePlots()

    def endRun(self, runNumber, runRecord):
        if not (self.toPlot is None):
            self._updatePlots()
            plt.ioff()

    def endJob(self):
        pass

    def _plotGridDims(self):
        nChannels = len(self.toPlot)
        if nChannels == 1:
            nRows = 1
            nCols = 1
        elif nChannels == 2:
            nRows = 2
            nCols = 1
        elif nChannels <= 4:
            nRows = 2
            nCols = 2
        elif nChannels == 8:
            nRows = 2
            nCols = 4
        else:
            nRows = int(math.sqrt(nChannels))
            nCols = nRows
            while nCols*nRows < nChannels:
                nRows += 1
                if nCols*nRows < nChannels:
                    nCols += 1
        return nRows, nCols

    def _makePlots(self):
        nRows, nCols = self._plotGridDims()
        fig, axes = plt.subplots(nRows, nCols)
        self._nRows = nRows
        self._nCols = nCols
        self._fig = fig
        self._axes = axes.flatten()
        fig.canvas.set_window_title(self.xlabel) 
        fig.suptitle("Run %d, 0 Events" % self.runNumber)
        # fig.subplots_adjust(hspace=self.vAdj)
        fig.tight_layout(rect=[0.02, 0.02, 1, 0.92])
        self._updatePlots()

    def _updateData(self, eventNumber, eventRecord):
        for slot in self.slots:
            channelValues = eventRecord[(slot,self.hardwareModule)]
            for channel, value in enumerate(channelValues):
                id = (slot, channel)
                if id in self.plotData:
                    self.plotData[id].append(value)

    def _xAxisUpperLimit(self, listMax):
        if listMax < self.nBins:
            maxADC = self.nBins
        else:
            roundBy = 500
            maxADC = (listMax // roundBy + 1)*roundBy
        return maxADC

    def _updatePlots(self):
        self._fig.suptitle("Run %d, %d events" % \
                           (self.runNumber, self.eventCounter))
        nChannels = len(self.toPlot)
        for row in range(self._nRows):
            for col in range(self._nCols):
                chnum = row*self._nCols + col
                ax = self._axes[chnum]
                ax.cla()
                if col == 0:
                    ax.set_ylabel("Events")
                if row + 1 == self._nRows:
                    ax.set_xlabel(self.xlabel)
                if chnum < nChannels:
                    ax.grid(True)
                    chId = self.toPlot[chnum]
                    ax.set_title("Slot %d ch %d" % chId)
                    if self.eventCounter > 0:
                        try:
                            maxCount = self._xAxisUpperLimit(max(self.plotData[chId]))
                        except:
                            maxCount = self.nBins
                    else:
                        maxCount = self.nBins
                    ax.hist(self.plotData[chId], self.nBins, range=(0, maxCount))
        plt.pause(1.e-6)


class ADCHisto(_ChannelHisto):
    def __init__(self, nBins, dutyCycle, vAdj, channels_to_plot=None):
        _ChannelHisto.__init__(self, nBins, dutyCycle, vAdj, "LeCroy2249",
                               "adc_slots", "ADC Counts", channels_to_plot)
        self.moduleName = "ADCHisto"

class ScalerHisto(_ChannelHisto):
    def __init__(self, nBins, dutyCycle, vAdj, channels_to_plot=None):
        _ChannelHisto.__init__(self, nBins, dutyCycle, vAdj, "LeCroy2552",
                               "scaler_slots_2552", "Scaler Counts", channels_to_plot)
        self.moduleName = "TDCHisto"

class TDCHisto(_ChannelHisto):
    def __init__(self, nBins, dutyCycle, vAdj, channels_to_plot=None):
        _ChannelHisto.__init__(self, nBins, dutyCycle, vAdj, "LeCroy3377",
                               "tdc_slots_3377", "TDC Counts", channels_to_plot)
        self.moduleName = "TDCHisto"
