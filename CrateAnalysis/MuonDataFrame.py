# -*- coding: utf-8 -*-
"""
=============================================
Program : CrateAnalysis/MuonDataFrame.py
=============================================
Summary:
"""
__author__ = "Sadman Ahmed Shanto"
__date__ = "10/06/2020"
__email__ = "sadman-ahmed.shanto@ttu.edu"
""""
To DO:
    - Event Display/Tracking
    - Imaging
"""

# import feather
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import os
import matplotlib as mpl
import itertools
import datetime
import qgrid
from matplotlib.backends.backend_pdf import PdfPages
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
from multiprocessing import Pool
from pandas_profiling import ProfileReport
from Histo2d import Histo2D
#from muondataframegui import show
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from multipledispatch import dispatch
from Notify import Notify

np.warnings.filterwarnings('ignore')


# CODE FOR COUNTING
def append_pdf(input, output):
    [
        output.addPage(input.getPage(page_num))
        for page_num in range(input.numPages)
    ]


def parallelize_dataframe(df, func, path, n_cores=2):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    # df.to_hdf(path, key=path, format="table")
    df.to_hdf(path, key=path)
    # feather.write_dataframe(df, path)
    return df


def getPhysicalUnits(asym):
    return (0.55 / 0.5) * asym


def getAsymmetryUnits(phys):
    return (1 / (0.55 / 0.5)) * phys


def remove_if_first_index(l):
    return [
        item for index, item in enumerate(l)
        if item[0] not in [value[0] for value in l[0:index]]
    ]


def conditionParser_multiple(df, conditions):
    qt, op, val = conditions.split(" ")
    if op == "==":
        df = df[df[qt] == float(val)]
        print(df[df[qt] == float(val)])
    elif op == ">":
        df = df[df[qt] > float(val)]
        # print(df[df[qt] > float(val)])
    elif op == "<":
        df = df[df[qt] < float(val)]
        print(df[df[qt] < float(val)])
    elif op == ">=":
        df = df[df[qt] >= float(val)]
        print(df[df[qt] >= float(val)])
    elif op == "<=":
        df = df[df[qt] <= float(val)]
        print(df[df[qt] <= float(val)])
    elif op == "!=":
        df = df[df[qt] != float(val)]
        print(df[df[qt] != float(val)])
    return df


def conditionParser_single(df, conditions):
    qt, op, val = conditions[0].split(" ")
    if op == "==":
        try:
            df = df[df[qt] == float(val)]
            print(df[df[qt] == float(val)])
        except:
            df = df[df[qt] == val]
            print(df[df[qt] == val])
    elif op == ">":
        df = df[df[qt] > float(val)]
        # print(df[df[qt] > float(val)])
    elif op == "<":
        df = df[df[qt] < float(val)]
        print(df[df[qt] < float(val)])
    elif op == ">=":
        df = df[df[qt] >= float(val)]
        print(df[df[qt] >= float(val)])
    elif op == "<=":
        df = df[df[qt] <= float(val)]
        print(df[df[qt] <= float(val)])
    elif op == "!=":
        df = df[df[qt] != float(val)]
        print(df[df[qt] != float(val)])
    return df


def getFilteredEvents(self, df, conditions):
    numConditions = len(conditions)
    if numConditions == 1:
        qt, op, val = conditions[0].split(" ")
        if op == "==":
            print(df[df[qt] == float(val)])
        elif op == ">":
            print(df[df[qt] > float(val)])
        elif op == "<":
            print(df[df[qt] < float(val)])
        elif op == ">=":
            print(df[df[qt] >= float(val)])
        elif op == "<=":
            print(df[df[qt] <= float(val)])
        elif op == "!=":
            print(df[df[qt] != float(val)])


def scrubbedDataFrame(df, queryName, numStd):
    s = df[queryName]
    s_mean = s.mean()
    s_std = s.std()
    v_low = s.mean() - numStd * s_std
    v_hi = s.mean() + numStd * s_std
    df_filtered = df[(df[queryName] < v_hi) & (df[queryName] > v_low)]
    return df_filtered


def getHistogram(df, queryName, title="", nbins=200):
    s = df[queryName]
    ax = s.plot.hist(alpha=0.7, bins=nbins, histtype='step')
    mean, std, count = s.describe().values[1], s.describe(
    ).values[2], s.describe().values[0]
    textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(mean, std, count)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)
    ax.text(0.80,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment='top',
            bbox=props)
    ax.set_title("Histogram of {} {}".format(queryName, title))
    plt.show()


def getFilteredHistogram(df, queryName, filter, nbins=200, title=""):
    df.hist(column=queryName, bins=nbins, by=filter, histtype='step')
    plt.suptitle("Histograms of {} grouped by {} {}".format(
        queryName, filter, title))
    plt.ylabel("Frequency")
    plt.show()


class MuonDataFrame:
    def __init__(self, path, isNew, d1="last"):
        """
        Initialize the MuonDataFrame

        :param path [string]: path to the data file
        :param d1 [string]: type of decision to be made on multiTDC events (acceptable terms are "last", "first", "min", and "max")
                            default value = last
        """
        self.newFileName = path.split(".")[0].split("/")[0] + "/" + path.split(
            ".")[0].split("/")[1] + ".h5"
        self.nbins = 150
        self.d_phys = 2  #distance between two trays in meters
        self.d_lead = 0.42  #distance (m) between top tray and lead brick
        self.d_asym = getAsymmetryUnits(self.d_phys / 2)
        self.quant_query_terms = []
        self.default_query_terms = [
            'event_num', 'event_time', 'deadtime', 'ADC', 'TDC', 'SCh0',
            'SCh1', 'SCh2', 'SCh3', 'SCh4', 'SCh5', 'SCh6', 'SCh7', 'SCh8',
            'SCh9', 'SCh9', 'SCh11', 'l1hit', 'l2hit', 'l3hit', 'l4hit',
            'r1hit', 'r2hit', 'r3hit', 'r4hit'
        ]
        self.query_terms = self.default_query_terms + self.quant_query_terms
        self.d1 = d1
        if isNew == "True":
            try:
                with pd.HDFStore(path) as hdf:
                    key1 = hdf.keys()[0]
                self.events_df = self.getDataFrame(
                    pd.read_hdf(path, key=key1, use_threads=True))
                #format="table",
            except:
                self.events_df = self.getDataFrame(
                    #pd.read_hdf(path, format="table", use_threads=True))
                    pd.read_hdf(path, use_threads=True))
        else:
            with pd.HDFStore(path) as hdf:
                key2 = hdf.keys()[1]
            self.events_df = pd.read_hdf(self.newFileName,
                                         key=key2,
                                         use_threads=True)
            #  format="table",
        self.pdfName = path.split(".")[0].split("/")[1] + ".pdf"
        self.pdfList = []
        self.runNum = self.pdfName.split(".")[0].split("_")[-1]
        self.imagelist = []
        self.og_df = self.events_df
        self.total = len(self.og_df.index)

    def addRunNumColumn(self, df):
        df["Run_Num"] = int(self.runNum)
        return df

    def getJnbDf(self, df):
        return qgrid.show_grid(df, show_toolbar=True)

    def sendReportEmail(self):
        csvName = "processed_data/events_data_frame_{}.csv".format(self.runNum)
        Notify().sendPdfEmail(self.pdfName, csvName)

    def sendReportEmailRecovery(self):
        csvName = "processed_data/events_data_frame_{}.csv".format(self.runNum)
        Notify().sendEmailRecovery(self.pdfName, csvName)

    def getCompleteCSVOutputFile(self):
        df = self.events_df
        df.drop('ADC', axis=1, inplace=True)
        df.drop('TDC', axis=1, inplace=True)
        df.drop('theta_x1', axis=1, inplace=True)
        df.drop('theta_y1', axis=1, inplace=True)
        df.drop('theta_x2', axis=1, inplace=True)
        df.drop('theta_y2', axis=1, inplace=True)
        df.drop('z_angle', axis=1, inplace=True)
        df = self.addRunNumColumn(df)
        name = "processed_data/events_data_frame_{}.csv".format(self.runNum)
        df.to_csv(name, header=True, index=False, compression='gzip')
        print("{} has been created".format(name))

    def getCompleteCSVOutputFile_og(self):
        df = self.events_df
        df.drop('ADC', axis=1, inplace=True)
        df.drop('TDC', axis=1, inplace=True)
        df = self.addRunNumColumn(df)
        name = "processed_data/events_data_frame_{}.csv".format(self.runNum)
        df.to_csv(name, header=True, index=False)
        print("{} has been created".format(name))

    def getCSVOutputFile(self, numEvents):
        df = self.events_df
        df.drop('ADC', axis=1, inplace=True)
        df.drop('TDC', axis=1, inplace=True)
        df.drop('theta_x1', axis=1, inplace=True)
        df.drop('theta_y1', axis=1, inplace=True)
        df.drop('theta_x2', axis=1, inplace=True)
        df.drop('theta_y2', axis=1, inplace=True)
        df.drop('z_angle', axis=1, inplace=True)
        df = self.addRunNumColumn(df)
        name = "processed_data/events_data_frame_{}.csv".format(self.runNum)
        numEvents += 1
        df.iloc[:numEvents, :].to_csv(name, header=True, index=False, compression='gzip')
        print("{} has been created".format(name))

    def reload(self):
        self.events_df = self.og_df

    def generateReport(self):
        profile = ProfileReport(self.events_df,
                                title='Prototype 1B Profiling Report',
                                explorative=True)
        profile.to_file("mdf.html")

    def getStartTime(self):
        x = self.events_df['event_time'].values[0]
        x = pd.to_datetime(str(x))
        return x.strftime("%b %d %Y %H:%M:%S")

    def getEndTime(self):
        x = self.events_df['event_time'].values[-1]
        x = pd.to_datetime(str(x))
        return x.strftime("%b %d %Y %H:%M:%S")

    def getFrontPageInfo(self):
        fLine = "Analysis of Run: " + self.runNum
        sLine = "\nRun Start: " + str(self.getStartTime())
        tLine = "\nRun End: " + str(self.getEndTime())
        foLine = "\n\n\n\nReport Generated at: " + str(
            datetime.datetime.today().strftime("%b %d %Y %H:%M:%S"))
        txt = fLine + sLine + tLine + foLine
        return txt

    def generateAnaReport(self, pdfName=""):
        print("Creating the report pdf...")
        if pdfName == "":
            pdfName = self.pdfName
        with PdfPages(pdfName) as pdf:
            firstPage = plt.figure(figsize=(11.69, 8.27))
            firstPage.clf()
            txt = self.getFrontPageInfo()
            firstPage.text(0.5,
                           0.5,
                           txt,
                           transform=firstPage.transFigure,
                           size=24,
                           ha="center")
            pdf.savefig()
            plt.close()
            self.getDeadtimePlot(pdf=True)
            pdf.savefig()
            plt.close()
            self.getChannelStatusPlot(pdf=True)
            pdf.savefig()
            plt.close()
            self.getNumLayersHitPlot(pdf=True)
            pdf.savefig()
            plt.close()
            self.getScalerPlots_header(pdf=True)
            pdf.savefig()
            plt.close()
            self.getScalerPlots_channels(pdf=True)
            pdf.savefig()
            plt.close()
            self.getCounterPlots(pdf=True)
            pdf.savefig()
            plt.close()
            self.getChannelPlots(pdf=True)
            pdf.savefig()
            plt.close()
            self.getChannelSumPlots(pdf=True, isBinned=True)
            pdf.savefig()
            plt.close()
            self.getChannelDiffPlots(pdf=True, isBinned=True)
            pdf.savefig()
            plt.close()
            self.getAsymmetry1DPlots(pdf=True, isBinned=True, nbin=100)
            pdf.savefig()
            plt.close()
            self.getAsymmetry1DPlotsWithGoodTDCEvents(dev=5,
                                                      pdf=True,
                                                      isBinned=True,
                                                      nbin=150)
            pdf.savefig()
            plt.close()
            self.getXView(pdf=True)
            pdf.savefig()
            plt.close()
            self.getYView(pdf=True)
            pdf.savefig()
            plt.close()
            self.getZView(pdf=True)
            pdf.savefig()
            plt.close()

            d = pdf.infodict()
            d['Title'] = 'Prototype 1B Data Analysis'
            d['Author'] = 'Sadman Ahmed Shanto'
            d['Subject'] = 'Storing Analysis Results'
            d['Keywords'] = 'Muon APDL'
            d['CreationDate'] = datetime.datetime(2020, 12, 21)
            d['ModDate'] = datetime.datetime.today()

        self.get2DTomogram(pdfv=True)
        self.get2DTomogram(pdfv=True, nbins=50, title="(High Binning)")
        self.getFingerPlots(pdfv=True)
        self.allLayerCorrelationPlots(pdfv=True,
                                      nbins=1000,
                                      title="(High Binning)")
        self.allLayerCorrelationPlots(pdfv=True, nbins=22, title="(Bins = 22)")
        self.convertPNG2PDF()
        self.createOnePDF(pdfName)
        # self.mergePDF(pdfName)
        print("The report file {} has been created.".format(pdfName))

    def keepGoodTDCEventsPlot(self, dev=5):
        self.keepEvents("sumL1", self.getStats("sumL1")['mean'] + dev, "<=")
        self.keepEvents("sumL1", self.getStats("sumL1")['mean'] - dev, ">=")
        self.keepEvents("sumL2", self.getStats("sumL2")['mean'] + dev, "<=")
        self.keepEvents("sumL2", self.getStats("sumL2")['mean'] - dev, ">=")
        self.keepEvents("sumL3", self.getStats("sumL3")['mean'] + dev, "<=")
        self.keepEvents("sumL3", self.getStats("sumL3")['mean'] - dev, ">=")
        self.keepEvents("sumL4", self.getStats("sumL4")['mean'] + dev, "<=")
        self.keepEvents("sumL4", self.getStats("sumL4")['mean'] - dev, ">=")

    def keep4by4Events(self):
        self.keepEvents("numLHit", 8, "==")

    def getXView(self,
                 pdf=False,
                 isBinned=True,
                 nbin=90,
                 a_min=-180,
                 a_max=180):
        self.keep4by4Events()
        xmin = a_min
        xmax = a_max
        nbins = self.getBins(xmin, xmax, nbin)
        fig, axes = plt.subplots(nrows=1, ncols=2)
        plt.suptitle("X view")
        ax0, ax1 = axes.flatten()
        ax0.hist(self.events_df['theta_x1'], nbins, histtype='step')
        ax0.set_xlim([xmin, xmax])
        s = self.events_df['theta_x1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Top Tray')
        ax1.hist(self.events_df['theta_x2'], nbins, histtype='step')
        ax1.set_xlim([xmin, xmax])
        ax1.set_title('Bottom Tray')
        s = self.events_df['theta_x2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        self.reload()
        if not pdf:
            plt.show()
        else:
            return fig

    def getYView(self,
                 pdf=False,
                 isBinned=True,
                 nbin=90,
                 a_min=-180,
                 a_max=180):
        self.keep4by4Events()
        xmin = a_min
        xmax = a_max
        nbins = self.getBins(xmin, xmax, nbin)
        fig, axes = plt.subplots(nrows=1, ncols=2)
        plt.suptitle("Y view")
        ax0, ax1 = axes.flatten()
        ax0.hist(self.events_df['theta_y1'], nbins, histtype='step')
        ax0.set_xlim([xmin, xmax])
        s = self.events_df['theta_y1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Top Tray')
        ax1.hist(self.events_df['theta_y2'], nbins, histtype='step')
        ax1.set_xlim([xmin, xmax])
        ax1.set_title('Bottom Tray')
        s = self.events_df['theta_y2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        self.reload()
        if not pdf:
            plt.show()
        else:
            return fig

    def getThetaXPlot(self,
                      theta_x1,
                      theta_x2,
                      pdf=False,
                      isBinned=True,
                      nbin=90,
                      a_min=-180,
                      a_max=180):
        fig, ax = plt.subplots(nrows=1, ncols=2)
        plt.suptitle("X Angle (degrees)")
        ax[0].hist(theta_x1,
                   bins=nbin,
                   range=(a_min, a_max),
                   alpha=0.5,
                   label="Top")
        ax[1].hist(theta_x2,
                   bins=nbin,
                   range=(a_min, a_max),
                   alpha=0.5,
                   label="Bottom")
        plt.legend()
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return ax

    def getThetaYPlot(self,
                      theta_y1,
                      theta_y2,
                      pdf=False,
                      isBinned=True,
                      nbin=90,
                      a_min=-180,
                      a_max=180):
        fig, ax = plt.subplots(nrows=1, ncols=2)
        plt.suptitle("Y Angle (degrees)")
        ax[0].hist(theta_y1,
                   bins=nbin,
                   range=(a_min, a_max),
                   alpha=0.5,
                   label="Top")
        ax[1].hist(theta_y2,
                   bins=nbin,
                   range=(a_min, a_max),
                   alpha=0.5,
                   label="Bottom")
        plt.legend()
        if not pdf:
            plt.show()
        else:
            return ax

    def getTomogram(self, pdf=False, isBinned=True, nbin=11):
        self.keep4by4Events()
        xmin = -1
        ymin = -1
        xmax = 1
        ymax = 1
        nbins = nbin

        fig, axes = plt.subplots(nrows=1, ncols=1)
        ax0 = axes
        ax0.hist(self.events_df['z_angle'], nbins, histtype='step')
        ax0.set_title('Plane of Lead Brick in Asymmetry Space')
        fig.tight_layout()
        self.reload()
        if not pdf:
            plt.show()
        else:
            return fig

    def getZView(self, pdf=False, isBinned=True, nbin=90, a_min=0, a_max=90):
        self.keep4by4Events()
        xmin = a_min
        xmax = a_max
        nbins = self.getBins(xmin, xmax, nbin)
        fig, axes = plt.subplots(nrows=1, ncols=1)
        ax0 = axes
        ax0.hist(self.events_df['z_angle'], nbins, histtype='step')
        ax0.set_xlim([xmin, xmax])
        s = self.events_df['z_angle']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=10,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Zenith Angle')
        fig.tight_layout()
        self.reload()
        if not pdf:
            plt.show()
        else:
            return fig

    def getAsymmetry1DPlotsWithGoodTDCEvents(self,
                                             dev=5,
                                             pdf=False,
                                             isBinned=True,
                                             nbin=150,
                                             amount=5):
        self.keepGoodTDCEventsPlot(dev)
        self.getAsymmetry1DPlots(
            pdf=pdf,
            isBinned=isBinned,
            nbin=nbin,
            amount=amount,
            title=
            "Histogram of Assymetry of each Tray (Events +- {} of Mean of SumTDC)"
            .format(dev))
        self.reload()

    def mergePDF(self, pdfName):
        for i in self.pdfList:
            os.remove(i + ".png")
        self.pdfList = [i + ".pdf" for i in self.pdfList]
        self.pdfList.insert(0, pdfName)
        output = PdfFileWriter()
        for i in self.pdfList:
            append_pdf(PdfFileReader(file(i, "rb")), output)
        output.write(file(pdfName, "wb"))

    def createOnePDF(self, pdfName):
        for i in self.pdfList:
            os.remove(i + ".png")
        self.pdfList = [i + ".pdf" for i in self.pdfList]
        self.pdfList.insert(0, pdfName)

        merger = PdfFileMerger()
        for pdf in self.pdfList:
            merger.append(PdfFileReader(pdf), 'rb')
        with open(pdfName, 'wb') as new_file:
            merger.write(new_file)

        # with open(output, 'wb') as f:
        # merger.write(pdfName)
        merger.close()
        self.pdfList.pop(0)
        for i in self.pdfList:
            os.remove(i)

    def convertPNG2PDF(self):
        for i in self.pdfList:
            image1 = Image.open(i + ".png")
            im1 = image1.convert('RGB')
            im1.save(i + ".pdf")

    # def gui(self):
    # show(self.events_df, settings={'block': True})
    # show(self.events_df)

    def getAnaReport(self):
        self.getDeadtimePlot()
        self.getChannelPlots()
        self.getChannelSumPlots()
        self.getChannelDiffPlots()
        self.getAsymmetry1DPlots()
        self.getNumLayersHitPlot()
        self.allLayerCorrelationPlots(nbins=200)
        self.allLayerCorrelationPlots(nbins=22)
        self.getScalerPlots_header()
        self.getScalerPlots_channels()

    def getScalerPlots_channels(self, pdf=False, amount=5):
        fig, axes = plt.subplots(nrows=4, ncols=2)
        plt.suptitle("Histogram of Scaler Readings (Ch 4 - 11)")
        ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7 = axes.flatten()
        s = self.events_df['SCh4']
        nbins = round(max(s.values) - min(s.values) // amount)
        ax0.hist(self.events_df['SCh4'], nbins, histtype='step')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Ch4 (1L)')
        s = self.events_df['SCh5']
        nbins = (max(s.values) - min(s.values)) // amount
        ax1.hist(self.events_df['SCh5'], nbins, histtype='step')
        ax1.set_title('Ch5 (1R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh6']
        nbins = (max(s.values) - min(s.values)) // amount
        ax2.hist(self.events_df['SCh6'], nbins, histtype='step')
        ax2.set_title('Ch6 (2L)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.80,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh7']
        nbins = (max(s.values) - min(s.values)) // amount
        ax3.hist(self.events_df['SCh7'], nbins, histtype='step')
        ax3.set_title('Ch7 (2R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.80,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh8']
        nbins = (max(s.values) - min(s.values)) // amount
        ax4.hist(self.events_df['SCh8'], nbins, histtype='step')
        ax4.set_title('Ch8 (3L)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax4.text(0.80,
                 0.95,
                 textstr,
                 transform=ax4.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh9']
        nbins = (max(s.values) - min(s.values)) // amount
        ax5.hist(self.events_df['SCh9'], nbins, histtype='step')
        ax5.set_title('Ch9 (3R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax5.text(0.80,
                 0.95,
                 textstr,
                 transform=ax5.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh10']
        nbins = (max(s.values) - min(s.values)) // amount
        ax6.hist(self.events_df['SCh9'], nbins, histtype='step')
        ax6.set_title('Ch10 (4L)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax6.text(0.80,
                 0.95,
                 textstr,
                 transform=ax6.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh11']
        nbins = (max(s.values) - min(s.values)) // amount
        ax7.hist(self.events_df['SCh11'], nbins, histtype='step')
        ax7.set_title('Ch11 (4R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax7.text(0.80,
                 0.95,
                 textstr,
                 transform=ax7.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getScalerPlots_header(self, pdf=False, amount=5):
        fig, axes = plt.subplots(nrows=4, ncols=1)
        plt.suptitle("Histogram of Scaler Readings (Ch 0 - 3)")
        ax0, ax1, ax2, ax3 = axes.flatten()
        s = self.events_df['SCh0']
        ax0.hist(self.events_df['SCh0'], 200, histtype='step')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\n".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Ch0')
        s = self.events_df['SCh1']
        nbins = (max(s.values) - min(s.values)) // amount
        ax1.hist(self.events_df['SCh1'], nbins, histtype='step')
        ax1.set_title('Ch1')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh2']
        nbins = (max(s.values) - min(s.values)) // amount
        ax2.hist(self.events_df['SCh2'], nbins, histtype='step')
        ax2.set_title('Ch2')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.80,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh3']
        ax3.hist(self.events_df['SCh3'], 200, histtype='step')
        ax3.set_title('Ch3')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\n".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.80,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getAsymPlotFig(self, term1, term2, nbins=500):
        xmin = -0.65
        xmax = 0.65
        ymin = -0.65
        ymax = 0.65
        x = self.get2DHistogram(self.events_df[term1].values,
                                self.events_df[term2].values,
                                "{} vs {}".format(term1, term2),
                                "Asymmetry in X", "Asymmetry in Y", xmin, xmax,
                                ymin, ymax, nbins, True)
        print(x)
        return x

    def x(self, t):
        asymT1 = self.events_df["asymL1"].values
        asymT3 = self.events_df["asymL3"].values
        return asymT1 + asymT3 * t

    def y(self, t):
        asymT2 = self.events_df["asymL2"].values
        asymT4 = self.events_df["asymL4"].values
        return asymT2 + asymT4 * t

    def z(self, t):
        return -(self.d_phys / 2) + self.d_phys * t

    def getTValue(self):
        return -(self.d_phys / 2) - self.d_lead

    def get2DTomogram(self, pdfv=False, nbins=11, title=""):
        self.keep4by4Events()
        xmin = -1
        xmax = 1
        ymin = -1
        ymax = 1
        t = self.getTValue()
        xx = self.x(t)
        yy = self.y(t)
        self.get2DHistogram(xx,
                            yy,
                            "{} Z Plane of Lead Brick".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv,
                            zLog=False)
        self.reload()

    def allLayerCorrelationPlots(self, pdfv=False, nbins=1000, title=""):
        xmin = -0.65
        xmax = 0.65
        ymin = -0.65
        ymax = 0.65
        self.get2DHistogram(self.events_df['asymL1'].values,
                            self.events_df['asymL2'].values,
                            "{} Asymmetry: L1 vs L2".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL3'].values,
                            self.events_df['asymL4'].values,
                            "{} Asymmetry: L3 vs L4".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL1'].values,
                            self.events_df['asymL3'].values,
                            "{} Asymmetry: L1 vs L3".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL2'].values,
                            self.events_df['asymL4'].values,
                            "{} Asymmetry: L2 vs L4".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL1'].values,
                            self.events_df['asymL4'].values,
                            "{} Asymmetry: L1 vs L4".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL2'].values,
                            self.events_df['asymL3'].values,
                            "{} Asymmetry: L2 vs L3".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)

    def getFingerPlots(self, pdfv=False):
        xmin = 0
        xmax = 300
        ymin = -0
        ymax = 300
        nbins = 250
        x = "L1"
        y = "R1"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        x = "L2"
        y = "R2"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        x = "L3"
        y = "R3"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        x = "L4"
        y = "R4"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)

    def getDeadtimePlot(self, pdf=False):
        x = self.getHistogram("deadtime", pdf=pdf)
        return x

    def getEfficiencyPlot(self, pdf=False):
        ax = ""
        return ax

    def getChannelStatusPlot(self, pdf=False):
        l1_p = list(self.og_df['l1hit'].values).count(1)
        l2_p = list(self.og_df['l2hit'].values).count(1)
        l3_p = list(self.og_df['l3hit'].values).count(1)
        l4_p = list(self.og_df['l4hit'].values).count(1)

        r1_p = list(self.og_df['r1hit'].values).count(1)
        r2_p = list(self.og_df['r2hit'].values).count(1)
        r3_p = list(self.og_df['r3hit'].values).count(1)
        r4_p = list(self.og_df['r4hit'].values).count(1)

        yvals = [
            l1_p / self.total, r1_p / self.total, l2_p / self.total,
            r2_p / self.total, l3_p / self.total, r3_p / self.total,
            l4_p / self.total, r4_p / self.total
        ]
        yvals = [i * 100 for i in yvals]
        xvals = [
            "Ch 0", "Ch 1", "Ch 2", "Ch 3", "Ch 6", "Ch 7", "Ch 8", "Ch 9"
        ]
        barlist = plt.bar(xvals, yvals)
        barlist[0].set_color('r')
        barlist[1].set_color('r')
        barlist[4].set_color('r')
        barlist[5].set_color('r')
        plt.title("Percentage of Good Events")
        ax = barlist
        if not pdf:
            plt.show()
        else:
            return ax

    def getADCPlot(self):
        pass

    def getNumLayersHitPlot(self, pdf=False):
        x = self.getHistogram("numLHit",
                              title="(TDC Hits Registered Per Event)",
                              pdf=pdf)
        return x

    def getBins(self, xmin, xmax, nbins):
        x = list(range(xmin, xmax))
        n = round((xmax - xmin) / nbins)
        return x[::n]

    def getCounterPlots(self, pdf=False, nbin=100):
        xmin = 0
        xmax = 100
        nbins = self.getBins(xmin, xmax, nbin)
        fig, axes = plt.subplots(nrows=1, ncols=2)
        plt.suptitle("Top and Bottom Counters")
        ax0, ax1 = axes.flatten()
        ax0.hist(self.events_df['TopCounter'], nbins, histtype='step')
        ax0.set_xlim([xmin, xmax])
        s = self.events_df['TopCounter']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Top Counter')
        ax1.hist(self.events_df['BottomCounter'], nbins, histtype='step')
        ax1.set_xlim([xmin, xmax])
        ax1.set_title('Bottom Counter')
        s = self.events_df['BottomCounter']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getChannelPlots(self, pdf=False, nbin=200):
        xmin = 0
        xmax = 200
        nbins = self.getBins(xmin, xmax, nbin)
        fig, axes = plt.subplots(nrows=2, ncols=4)
        plt.suptitle("Histogram of All Individual Channels")
        ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7 = axes.flatten()
        ax0.hist(self.events_df['L1'], nbins, histtype='step')
        ax0.set_xlim([xmin, xmax])
        s = self.events_df['L1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Ch0')
        ax1.hist(self.events_df['R1'], nbins, histtype='step')
        ax1.set_xlim([xmin, xmax])
        ax1.set_title('Ch1')
        s = self.events_df['R1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax2.hist(self.events_df['L2'], nbins, histtype='step')
        ax2.set_title('Ch2')
        ax2.set_xlim([xmin, xmax])
        s = self.events_df['L2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.80,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax3.hist(self.events_df['R2'], nbins, histtype='step')
        ax3.set_xlim([xmin, xmax])
        ax3.set_title('Ch3')
        s = self.events_df['R2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.80,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax4.hist(self.events_df['L3'], nbins, histtype='step')
        ax4.set_xlim([xmin, xmax])
        ax4.set_title('Ch6')
        s = self.events_df['L3']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax4.text(0.80,
                 0.95,
                 textstr,
                 transform=ax4.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax5.hist(self.events_df['R3'], nbins, histtype='step')
        ax5.set_xlim([xmin, xmax])
        ax5.set_title('Ch7')
        s = self.events_df['R3']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax5.text(0.80,
                 0.95,
                 textstr,
                 transform=ax5.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax6.hist(self.events_df['L4'], nbins, histtype='step')
        ax6.set_xlim([xmin, xmax])
        ax6.set_title('Ch8')
        s = self.events_df['L4']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax6.text(0.80,
                 0.95,
                 textstr,
                 transform=ax6.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax7.hist(self.events_df['R4'], nbins, histtype='step')
        ax7.set_xlim([xmin, xmax])
        ax7.set_title('Ch9')
        s = self.events_df['R4']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        ovflow = ((xmax < s.values) | (s.values < xmin)).sum()
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBins: {}\nOverflow: {}".format(
            mean, std, count, nbin, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax7.text(0.80,
                 0.95,
                 textstr,
                 transform=ax7.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getChannelSumPlots(self, pdf=False, isBinned=True, nbin=50, amount=5):
        if isBinned:
            fig, axes = plt.subplots(nrows=4, ncols=1)
            xmin, xmax = 150, 250
            nbins = self.getBins(xmin, xmax, nbin)
            plt.suptitle(
                "Histogram of Sum of Channels in their Respective Trays")
            ax0, ax1, ax2, ax3 = axes.flatten()
            ovflow = ((xmax < self.events_df['sumL1'].values) |
                      (self.events_df['sumL1'].values < xmin)).sum()
            ax0.hist(self.events_df['sumL1'], bins=nbins, histtype='step')
            ax0.set_xlim([xmin, xmax])
            s = self.events_df['sumL1']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax0.text(0.90,
                     0.95,
                     textstr,
                     transform=ax0.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ax0.set_title('Tray 1')
            ovflow = ((xmax < self.events_df['sumL2'].values) |
                      (self.events_df['sumL2'].values < xmin)).sum()
            ax1.hist(self.events_df['sumL2'], nbins, histtype='step')
            ax1.set_xlim([xmin, xmax])
            ax1.set_title('Tray 2')
            s = self.events_df['sumL2']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.90,
                     0.95,
                     textstr,
                     transform=ax1.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ovflow = ((xmax < self.events_df['sumL3'].values) |
                      (self.events_df['sumL3'].values < xmin)).sum()
            ax2.hist(self.events_df['sumL3'], nbins, histtype='step')
            ax2.set_xlim([xmin, xmax])
            ax2.set_title('Tray 3')
            s = self.events_df['sumL3']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax2.text(0.90,
                     0.95,
                     textstr,
                     transform=ax2.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ovflow = ((xmax < self.events_df['sumL4'].values) |
                      (self.events_df['sumL4'].values < xmin)).sum()
            ax3.hist(self.events_df['sumL4'], nbins, histtype='step')
            ax3.set_xlim([xmin, xmax])
            ax3.set_title('Tray 4')
            s = self.events_df['sumL4']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax3.text(0.90,
                     0.95,
                     textstr,
                     transform=ax3.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            fig.tight_layout()
            if not pdf:
                plt.show()
            else:
                return fig
        else:
            fig, axes = plt.subplots(nrows=4, ncols=1)
            xmin, xmax = 150, 250
            plt.suptitle(
                "Histogram of Sum of Channels in their Respective Trays")
            ax0, ax1, ax2, ax3 = axes.flatten()
            nbins = len(self.events_df['sumL1']) // amount
            ovflow = ((xmax < self.events_df['sumL1'].values) |
                      (self.events_df['sumL1'].values < xmin)).sum()
            ax0.hist(self.events_df['sumL1'], bins=nbins, histtype='step')
            ax0.set_xlim([xmin, xmax])
            s = self.events_df['sumL1']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax0.text(0.90,
                     0.95,
                     textstr,
                     transform=ax0.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ax0.set_title('Tray 1')
            nbins = len(self.events_df['sumL2']) // amount
            ovflow = ((xmax < self.events_df['sumL2'].values) |
                      (self.events_df['sumL2'].values < xmin)).sum()
            ax1.hist(self.events_df['sumL2'], nbins, histtype='step')
            ax1.set_xlim([xmin, xmax])
            ax1.set_title('Tray 2')
            s = self.events_df['sumL2']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.90,
                     0.95,
                     textstr,
                     transform=ax1.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            nbins = len(self.events_df['sumL3']) // amount
            ovflow = ((xmax < self.events_df['sumL3'].values) |
                      (self.events_df['sumL3'].values < xmin)).sum()
            ax2.hist(self.events_df['sumL3'], nbins, histtype='step')
            ax2.set_xlim([xmin, xmax])
            ax2.set_title('Tray 3')
            s = self.events_df['sumL3']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax2.text(0.90,
                     0.95,
                     textstr,
                     transform=ax2.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            nbins = len(self.events_df['sumL4']) // amount
            ovflow = ((xmax < self.events_df['sumL4'].values) |
                      (self.events_df['sumL4'].values < xmin)).sum()
            ax3.hist(self.events_df['sumL4'], nbins, histtype='step')
            ax3.set_xlim([xmin, xmax])
            ax3.set_title('Tray 4')
            s = self.events_df['sumL4']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax3.text(0.90,
                     0.95,
                     textstr,
                     transform=ax3.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            fig.tight_layout()
            if not pdf:
                plt.show()
            else:
                return fig

    def getChannelDiffPlots(self, pdf=False, isBinned=True, nbin=50, amount=5):
        if isBinned:
            fig, axes = plt.subplots(nrows=4, ncols=1)
            xmin = -100
            xmax = 100
            plt.suptitle(
                "Histogram of Difference of Channels in their Respective Trays"
            )
            nbins = self.getBins(xmin, xmax, nbin)
            ovflow = ((xmax < self.events_df['diffL1'].values) |
                      (self.events_df['diffL1'].values < xmin)).sum()
            ax0, ax1, ax2, ax3 = axes.flatten()
            ax0.hist(self.events_df['diffL1'], nbins, histtype='step')
            ax0.set_xlim([xmin, xmax])
            s = self.events_df['diffL1']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax0.text(0.90,
                     0.95,
                     textstr,
                     transform=ax0.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ax0.set_title('Tray 1')
            ovflow = ((xmax < self.events_df['diffL2'].values) |
                      (self.events_df['diffL2'].values < xmin)).sum()
            ax1.hist(self.events_df['diffL2'], nbins, histtype='step')
            ax1.set_xlim([xmin, xmax])
            ax1.set_title('Tray 2')
            s = self.events_df['diffL2']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.90,
                     0.95,
                     textstr,
                     transform=ax1.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ovflow = ((xmax < self.events_df['diffL3'].values) |
                      (self.events_df['diffL3'].values < xmin)).sum()
            ax2.hist(self.events_df['diffL3'], nbins, histtype='step')
            ax2.set_xlim([xmin, xmax])
            ax2.set_title('Tray 3')
            s = self.events_df['diffL3']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax2.text(0.90,
                     0.95,
                     textstr,
                     transform=ax2.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ovflow = ((xmax < self.events_df['diffL4'].values) |
                      (self.events_df['diffL4'].values < xmin)).sum()
            ax3.hist(self.events_df['diffL4'], nbins, histtype='step')
            ax3.set_xlim([xmin, xmax])
            ax3.set_title('Tray 4')
            s = self.events_df['diffL4']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax3.text(0.90,
                     0.95,
                     textstr,
                     transform=ax3.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            fig.tight_layout()
            if not pdf:
                plt.show()
            else:
                return fig
        else:
            fig, axes = plt.subplots(nrows=4, ncols=1)
            xmin = -100
            xmax = 100
            plt.suptitle(
                "Histogram of Difference of Channels in their Respective Trays"
            )
            nbins = len(self.events_df['diffL1']) // amount
            ovflow = ((xmax < self.events_df['diffL1'].values) |
                      (self.events_df['diffL1'].values < xmin)).sum()
            ax0, ax1, ax2, ax3 = axes.flatten()
            ax0.hist(self.events_df['diffL1'], nbins, histtype='step')
            ax0.set_xlim([xmin, xmax])
            s = self.events_df['diffL1']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax0.text(0.90,
                     0.95,
                     textstr,
                     transform=ax0.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ax0.set_title('Tray 1')
            nbins = len(self.events_df['diffL2']) // amount
            ovflow = ((xmax < self.events_df['diffL2'].values) |
                      (self.events_df['diffL2'].values < xmin)).sum()
            ax1.hist(self.events_df['diffL2'], nbins, histtype='step')
            ax1.set_xlim([xmin, xmax])
            ax1.set_title('Tray 2')
            s = self.events_df['diffL2']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.90,
                     0.95,
                     textstr,
                     transform=ax1.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            nbins = len(self.events_df['diffL3']) // amount
            ovflow = ((xmax < self.events_df['diffL3'].values) |
                      (self.events_df['diffL3'].values < xmin)).sum()
            ax2.hist(self.events_df['diffL3'], nbins, histtype='step')
            ax2.set_xlim([xmin, xmax])
            ax2.set_title('Tray 3')
            s = self.events_df['diffL3']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax2.text(0.90,
                     0.95,
                     textstr,
                     transform=ax2.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            nbins = len(self.events_df['diffL4']) // amount
            ovflow = ((xmax < self.events_df['diffL4'].values) |
                      (self.events_df['diffL4'].values < xmin)).sum()
            ax3.hist(self.events_df['diffL4'], nbins, histtype='step')
            ax3.set_xlim([xmin, xmax])
            ax3.set_title('Tray 4')
            s = self.events_df['diffL4']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax3.text(0.90,
                     0.95,
                     textstr,
                     transform=ax3.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            fig.tight_layout()
            if not pdf:
                plt.show()
            else:
                return fig

    def getAsymmetry1DPlots(self,
                            pdf=False,
                            isBinned=True,
                            nbin=50,
                            amount=5,
                            title="Histogram of Asymmetry of each Tray"):
        if isBinned:
            fig, axes = plt.subplots(nrows=4, ncols=1)
            plt.suptitle(title)
            ax0, ax1, ax2, ax3 = axes.flatten()
            xmin, xmax = -0.5, 0.5
            # nbins = self.getBins(xmin, xmax, nbin)
            nbins = nbin
            ovflow = ((xmax < self.events_df['asymL1'].values) |
                      (self.events_df['asymL1'].values < xmin)).sum()
            ax0.hist(self.events_df['asymL1'],
                     range=(xmin, xmax),
                     bins=nbins,
                     histtype='step')
            s = self.events_df['asymL1']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax0.text(0.90,
                     0.95,
                     textstr,
                     transform=ax0.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ax0.set_xlim([xmin, xmax])
            ax0.set_title('Tray 1')
            ovflow = ((xmax < self.events_df['asymL2'].values) |
                      (self.events_df['asymL2'].values < xmin)).sum()
            ax1.hist(self.events_df['asymL2'],
                     range=(xmin, xmax),
                     bins=nbins,
                     histtype='step')
            ax1.set_xlim([xmin, xmax])
            ax1.set_title('Tray 2')
            s = self.events_df['asymL2']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.90,
                     0.95,
                     textstr,
                     transform=ax1.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ovflow = ((xmax < self.events_df['asymL3'].values) |
                      (self.events_df['asymL3'].values < xmin)).sum()
            ax2.hist(self.events_df['asymL3'],
                     range=(xmin, xmax),
                     bins=nbins,
                     histtype='step')
            ax2.set_xlim([xmin, xmax])
            ax2.set_title('Tray 3')
            s = self.events_df['asymL3']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax2.text(0.90,
                     0.95,
                     textstr,
                     transform=ax2.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ovflow = ((xmax < self.events_df['asymL4'].values) |
                      (self.events_df['asymL4'].values < xmin)).sum()
            ax3.hist(self.events_df['asymL4'],
                     range=(xmin, xmax),
                     bins=nbins,
                     histtype='step')
            ax3.set_xlim([xmin, xmax])
            ax3.set_title('Tray 4')
            s = self.events_df['asymL4']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax3.text(0.90,
                     0.95,
                     textstr,
                     transform=ax3.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            fig.tight_layout()
            if not pdf:
                plt.show()
            else:
                return fig
        else:
            fig, axes = plt.subplots(nrows=4, ncols=1)
            plt.suptitle("Histogram of Asymmetry of each Tray")
            ax0, ax1, ax2, ax3 = axes.flatten()
            xmin, xmax = -0.25, 0.25
            nbins = len(self.events_df['asymL1']) // amount
            ovflow = ((xmax < self.events_df['asymL1'].values) |
                      (self.events_df['asymL1'].values < xmin)).sum()
            ax0.hist(self.events_df['asymL1'], nbins, histtype='step')
            s = self.events_df['asymL1']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax0.text(0.90,
                     0.95,
                     textstr,
                     transform=ax0.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            ax0.set_xlim([xmin, xmax])
            ax0.set_title('Tray 1')
            nbins = len(self.events_df['asymL2']) // amount
            ovflow = ((xmax < self.events_df['asymL2'].values) |
                      (self.events_df['asymL2'].values < xmin)).sum()
            ax1.hist(self.events_df['asymL2'], nbins, histtype='step')
            ax1.set_xlim([xmin, xmax])
            ax1.set_title('Tray 2')
            s = self.events_df['asymL2']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.90,
                     0.95,
                     textstr,
                     transform=ax1.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            nbins = len(self.events_df['asymL3']) // amount
            ovflow = ((xmax < self.events_df['asymL3'].values) |
                      (self.events_df['asymL3'].values < xmin)).sum()
            ax2.hist(self.events_df['asymL3'], nbins, histtype='step')
            ax2.set_xlim([xmin, xmax])
            ax2.set_title('Tray 3')
            s = self.events_df['asymL3']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax2.text(0.90,
                     0.95,
                     textstr,
                     transform=ax2.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            nbins = len(self.events_df['asymL4']) // amount
            ovflow = ((xmax < self.events_df['asymL4'].values) |
                      (self.events_df['asymL4'].values < xmin)).sum()
            ax3.hist(self.events_df['asymL4'], nbins, histtype='step')
            ax3.set_xlim([xmin, xmax])
            ax3.set_title('Tray 4')
            s = self.events_df['asymL4']
            mean, std, count = s.describe().values[1], s.describe(
            ).values[2], s.describe().values[0]
            textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
                mean, std, count, nbin, ovflow)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax3.text(0.90,
                     0.95,
                     textstr,
                     transform=ax3.transAxes,
                     fontsize=5,
                     verticalalignment='top',
                     bbox=props)
            fig.tight_layout()
            if not pdf:
                plt.show()
            else:
                return fig

    def getDataFrame(self, df):
        # return self.serialize_dataframe(df, self.newFileName)
        return parallelize_dataframe(df, self.completeDataFrameNoADCTDC,
                                     self.newFileName)

    def serialize_dataframe(self, df, path):
        df = self.completeDataFrameNoADCTDC(df)
        # feather.write_dataframe(df, path)
        df.to_hdf(path, key=path)
        return df

    def completeDataFrameNoADCTDC(self, df):
        df['L1'] = self.getTDC(df['TDC'].to_numpy(), 0)
        df['R1'] = self.getTDC(df['TDC'].values, 1)
        df['L2'] = self.getTDC(df['TDC'].values, 2)
        df['R2'] = self.getTDC(df['TDC'].values, 3)
        df['L3'] = self.getTDC(df['TDC'].values, 6)
        df['R3'] = self.getTDC(df['TDC'].values, 7)
        df['L4'] = self.getTDC(df['TDC'].values, 8)
        df['R4'] = self.getTDC(df['TDC'].values, 9)
        df['TopCounter'] = self.getTDC(df['TDC'].values, 4)
        df['BottomCounter'] = self.getTDC(df['TDC'].values, 10)
        df['sumL1'] = df.eval('L1 + R1')
        df['sumL2'] = df.eval('L2 + R2')
        df['sumL3'] = df.eval('L3 + R3')
        df['sumL4'] = df.eval('L4 + R4')
        df['diffL1'] = df.eval('L1 - R1')
        df['diffL2'] = df.eval('L2 - R2')
        df['diffL3'] = df.eval('L3 - R3')
        df['diffL4'] = df.eval('L4 - R4')
        df['asymL1'] = df.eval('diffL1 / sumL1')
        df['asymL2'] = df.eval('diffL2 / sumL2')
        df['asymL3'] = df.eval('diffL3 / sumL3')
        df['asymL4'] = df.eval('diffL4 / sumL4')
        df["numLHit"] = df.eval(
            'l1hit + l2hit + l3hit + l4hit + r1hit + r2hit + r3hit + r4hit')
        df['theta_x1'] = df.eval("asymL2/asymL1") * (360 / np.pi)
        df['theta_y1'] = df.eval("asymL1/asymL2") * (360 / np.pi)
        df['theta_x2'] = df.eval("asymL4/asymL3") * (360 / np.pi)
        df['theta_y2'] = df.eval("asymL3/asymL4") * (360 / np.pi)
        # process Z
        asymT1 = df['asymL1'].values
        asymT2 = df['asymL2'].values
        zangles = np.arctan(
            np.sqrt(asymT1**2 + asymT2**2) / self.d_asym) * (360 / np.pi)
        df["z_angle"] = zangles
        return df

    def completeDataFrame(self, df):
        df['L1'] = self.getTDC(df['TDC'].to_numpy(), 0)
        df['R1'] = self.getTDC(df['TDC'].values, 1)
        df['L2'] = self.getTDC(df['TDC'].values, 2)
        df['R2'] = self.getTDC(df['TDC'].values, 3)
        df['L3'] = self.getTDC(df['TDC'].values, 6)
        df['R3'] = self.getTDC(df['TDC'].values, 7)
        df['L4'] = self.getTDC(df['TDC'].values, 8)
        df['R4'] = self.getTDC(df['TDC'].values, 9)
        df['TopCounter'] = self.getTDC(df['TDC'].values, 4)
        df['BottomCounter'] = self.getTDC(df['TDC'].values, 10)
        df['sumL1'] = df.eval('L1 + R1')
        df['sumL2'] = df.eval('L2 + R2')
        df['sumL3'] = df.eval('L3 + R3')
        df['sumL4'] = df.eval('L4 + R4')
        df['diffL1'] = df.eval('L1 - R1')
        df['diffL2'] = df.eval('L2 - R2')
        df['diffL3'] = df.eval('L3 - R3')
        df['diffL4'] = df.eval('L4 - R4')
        df['asymL1'] = df.eval('diffL1 / sumL1')
        df['asymL2'] = df.eval('diffL2 / sumL2')
        df['asymL3'] = df.eval('diffL3 / sumL3')
        df['asymL4'] = df.eval('diffL4 / sumL4')
        df['theta_x1'] = self.events_df.eval("asymL2/asymL1") * (360 / np.pi)
        df['theta_y1'] = self.events_df.eval("asymL1/asymL2") * (360 / np.pi)
        df['theta_x2'] = self.events_df.eval("asymL4/asymL3") * (360 / np.pi)
        df['theta_y2'] = self.events_df.eval("asymL3/asymL4") * (360 / np.pi)
        df["numLHit"] = df.eval(
            'l1hit + l2hit + l3hit + l4hit + r1hit + r2hit + r3hit + r4hit')
        # process Z
        asymT1 = df['asymL1'].values
        asymT2 = df['asymL2'].values
        zangles = np.arctan(
            np.sqrt(asymT1**2 + asymT2**2) / self.d_asym) * (360 / np.pi)
        df["z_angle"] = zangles
        return df

    def getTDC(self, event, chNum):
        tdcs = []
        for ev in event:
            tdc = 0
            tdcVals = []
            if ev != None:
                for i in ev:
                    if chNum in i:
                        tdcVals.append(i[1])
                tdc = self.getCorrectTDC(tdcVals)
            else:
                tdc = None
            tdcs.append(tdc)
        return tdcs

    def removeMultiHits(self, event):
        counts = []
        for ev in event:
            if ev != None:
                counts.append(
                    len([
                        next(t)
                        for _, t in itertools.groupby(ev, lambda x: x[0])
                    ]))
            else:
                counts.append(0)
        return counts

    def get(self, term):
        return self.events_df[term].values

    def getCorrectTDC(self, tdcs):
        if len(tdcs) == 1:
            return tdcs[0]
        elif len(tdcs) == 0:
            return None
        else:
            if self.d1 == "last":
                # print("len(tdcs) : {}".format(len(tdcs)))
                return tdcs[-1]
            elif self.d1 == "first":
                return tdcs[0]
            elif self.d1 == "min":
                return min(tdcs)
            elif self.d1 == "max":
                return max(tdcs)

    def show(self):
        return self.events_df
        # print(self.events_df)

    def lookAt(self, query_term):
        return self.events_df[query_term]
        # print(self.events_df[query_term])

    def removeNoTDCEvents(self):
        self.events_df = self.events_df[~self.events_df["TDC"].isnull()]

    def summary(self):
        return self.events_df.info()
        # print(self.events_df.info())

    def generateMultipleTDCHitData(self):
        criteria = self.d1
        num_tdc_read = self.events_df["TDC"].values
        tdc_hits = []
        tdc_event = []
        for event in num_tdc_read:
            if event == None:
                tdc_hits.append([0, 0, 0, 0])
                tdc_event.append(None)
            else:
                tdc_list, ev_list = self.calculateTDCHits(event, criteria)
                tdc_event.append(ev_list)
                tdc_hits.append(tdc_list)
        self.events_df["TDC_hit_num"] = tdc_hits
        self.events_df["TDC_Ana"] = tdc_event
        # self.generateNumChannelsReadData()
        # self.generateTDCAnalyzedData()

    def createTDCValues(self, tdc_hits, event, criteria):
        if criteria == "last":
            ev = list(OrderedDict(event).items())
        elif criteria == "first":
            ev = remove_if_first_index(event)
        elif criteria == "max":
            ev = list(dict(list(event), key=lambda v: int(v[1])).items())
            ev.pop()
        elif criteria == "min":
            d = defaultdict(list)
            for name, num in event:
                d[name].append(num)
            ev = list(zip(d, map(min, d.values())))
        return ev

    def calculateTDCHits(self, event, criteria):
        zero_c = 0
        one_c = 0
        three_c = 0
        four_c = 0
        tdc_event = []
        for i in event:
            if i[0] == 0:
                zero_c += 1
            elif i[0] == 1:
                one_c += 1
            elif i[0] == 3:
                three_c += 1
            elif i[0] == 4:
                four_c += 1
        tdc_hit = [zero_c, one_c, three_c, four_c]
        ev = self.createTDCValues(tdc_hit, event, criteria)
        return tdc_hit, ev

    def getHistogram(self, queryName, title="", nbins=200, pdf=False):
        s = self.events_df[queryName]
        # plt.figure(figsize=(3, 3))
        ax = s.plot.hist(alpha=0.7, bins=nbins)
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)
        ax.text(0.80,
                0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=12,
                verticalalignment='top',
                bbox=props)
        ax.set_title("Histogram of {} {}".format(queryName, title))
        if not pdf:
            plt.show()
        else:
            return ax

    def getKDE(self, queryName, nbins=200):
        s = self.events_df[queryName].to_numpy()
        s = pd.Series(s)
        ax = s.plot.kde()
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.80,
                0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=14,
                verticalalignment='top',
                bbox=props)
        ax.set_title("Probability Density of {}".format(queryName))
        plt.show()

    def getFilteredHistogram(self, queryName, filter, nbins=200, title=""):
        self.events_df.hist(column=queryName, bins=nbins, by=filter)
        plt.suptitle("Histograms of {} grouped by {} {}".format(
            queryName, filter, title))
        plt.ylabel("Frequency")
        plt.show()

    def getComparableHistogram(self, queries, nbins=200, title="", lims=None):
        s = pd.DataFrame(columns=queries)
        s = s.fillna(0)  # with 0s rather than NaNs
        for query in queries:
            s[query] = self.events_df[query]
        ax = s.plot.hist(alpha=0.6, bins=nbins, range=lims)
        plt.title("Histogram of {} {}".format(str(queries), title))
        plt.show()

    def get2DHistogram(self,
                       xvals,
                       yvals,
                       title,
                       xlabel,
                       ylabel,
                       xmin,
                       xmax,
                       ymin,
                       ymax,
                       nbins=150,
                       pdf=False,
                       zLog=True):
        name = title.replace(" ", "") + "_run_" + self.runNum
        self.pdfList.append(name)
        if not pdf:
            Histo2D(name,
                    title,
                    xlabel,
                    nbins,
                    xmin,
                    xmax,
                    xvals,
                    ylabel,
                    nbins,
                    ymin,
                    ymax,
                    yvals,
                    pdf,
                    zIsLog=zLog)
        else:
            return Histo2D(name,
                           title,
                           xlabel,
                           nbins,
                           xmin,
                           xmax,
                           xvals,
                           ylabel,
                           nbins,
                           ymin,
                           ymax,
                           yvals,
                           pdf,
                           zIsLog=zLog)

    def getFilteredEvents(self, conditions):
        df = self.events_df
        numConditions = len(conditions)
        if numConditions == 1:
            return conditionParser_single(self.events_df, conditions)
        else:
            df1 = conditionParser_multiple(self.events_df, conditions[0])
            df2 = conditionParser_multiple(self.events_df, conditions[1])
            main_op = conditions[2]
            if main_op == "&":
                intersection = df1[['event_num'
                                    ]].merge(df2[['event_num'
                                                  ]]).drop_duplicates()
                res = pd.concat(
                    [df1.merge(intersection),
                     df2.merge(intersection)])
                # print(res)
            else:
                res = pd.concat([df1, df2])
                # print(res)
            return res

    def dropna(arr, *args, **kwarg):
        assert isinstance(arr, np.ndarray)
        dropped = pd.DataFrame(arr).dropna(*args, **kwarg).values
        if arr.ndim == 1:
            dropped = dropped.flatten()
        return dropped

    def getFilteredPlot(self, term, value, cond, title=""):
        self.keepEvents(term, value, cond)
        self.getPlot(term, title=title)
        self.reload()

    @dispatch(str)
    def getPlot(self, query):
        self.events_df[query].plot()
        plt.xlabel("Event Number")
        plt.ylabel(str(query))
        plt.title("Plot of {} event series ".format(query))
        plt.show()

    @dispatch(list)
    def getPlot(self, queries, title=""):
        plt.plot(self.events_df[queries[0]].values,
                 self.events_df[queries[1]].values)
        plt.xlabel(str(queries[0]))
        plt.ylabel(str(queries[1]))
        plt.title("Line Plot of {} against {} {}".format(
            queries[0], queries[1], title))
        plt.show()

    def getScatterPlot(self, queries, title=""):
        plt.scatter(self.events_df[queries[0]].values,
                    self.events_df[queries[1]].values)
        plt.xlabel(str(queries[0]))
        plt.ylabel(str(queries[1]))
        plt.title("Scatter Plot of {} against {} {}".format(
            queries[0], queries[1], title))
        plt.show()

    def get3DScatterPlot(self, queries, title=""):
        self.events_df.plot.scatter(x=queries[0],
                                    y=queries[1],
                                    c=queries[2],
                                    colormap='viridis')
        plt.title(title)
        plt.show()

    def getEventInfo(self, eventNum):
        if isinstance(eventNum, int):
            df = self.events_df.loc[self.events_df["event_num"] == eventNum]
        elif isinstance(eventNum, list):
            df = self.events_df[self.events_df['event_num'].between(
                eventNum[0], eventNum[1])]
        return df
        # print(df)

    def getStats(self, queryName):
        s = self.events_df[queryName]
        return s.describe()
        # print(s.describe())

    def removeOutliers(self):
        for queryName in self.quant_query_terms:
            q_low = self.events_df[queryName].quantile(0.01)
            q_hi = self.events_df[queryName].quantile(0.99)
            self.events_df = self.events_df[
                (self.events_df[queryName] < q_hi)
                & (self.events_df[queryName] > q_low)]

    def keepEvents(self, term, value, cond):
        if cond == "<":
            self.events_df = self.events_df[self.events_df[term] < value]
        elif cond == ">":
            self.events_df = self.events_df[self.events_df[term] > value]
        elif cond == "==":
            self.events_df = self.events_df[self.events_df[term] == value]
        elif cond == ">=":
            self.events_df = self.events_df[self.events_df[term] >= value]
        elif cond == "<=":
            self.events_df = self.events_df[self.events_df[term] <= value]
        elif cond == "!=":
            self.events_df = self.events_df[self.events_df[term] != value]

    # @staticmethod

    def keepEventsWithinStdDev(self, queryName, numStd):
        df_filtered = scrubbedDataFrame(self.events_df, queryName, numStd)
        self.events_df = df_filtered

    def getTrimmedHistogram(self, queryName, numStd, nbins=200):
        df_filtered = scrubbedDataFrame(self.events_df, queryName, numStd)
        getHistogram(df_filtered,
                     queryName,
                     title="(Events within {} std dev)".format(numStd),
                     nbins=nbins)

    def getTrimmed2DHistogram(df, queryName, numStd, nbins=200):
        pass

    def getTrimmedFilteredHistogram(self, queryName, numStd, nbins=200):
        df_filtered = scrubbedDataFrame(self.events_df, queryName, numStd)
        getFilteredHistogram(df_filtered,
                             queryName,
                             nbins,
                             title="(Events within {} std dev)".format(numStd))

    def getTrimmedComparableHistogram(self, queries, numStd, nbins=200):
        s = pd.DataFrame(columns=queries)
        s = s.fillna(0)  # with 0s rather than NaNs
        for query in queries:
            s[query] = scrubbedDataFrame(self.events_df, query, numStd)[query]
        ax = s.plot.hist(alpha=0.7, bins=nbins, histtype='step')
        plt.title("Histogram of {} (Events within {} std dev)".format(
            str(queries), numStd))
        plt.show()
