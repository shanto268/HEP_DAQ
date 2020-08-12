#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A module for plotting 2-d histograms of various numeric quantities
"""

__author__="Igor Volobouev (i.volobouev@ttu.edu)"
__version__="0.2"
__date__ ="June 25 2020"

import matplotlib.pyplot as plt
import numpy as np
import sys
from AbsAnalysisModule import AbsAnalysisModule

class HistoMaker2D(AbsAnalysisModule):
    """
    This class can be used to build various simple 2-d histograms,
    one entry per event. Module constructor arguments are:

    name          Name for the module
    title         Title for the plot
    xlabel        Label for the X axis
    nxbins        Number of bins for the X axis
    xmin, xmax    Limits for the X axis
    xcalculator   A functor which takes the event record as the argument
                  and calculates the quantity to histogram on the X axis
    ylabel        Label for the Y axis
    nybins        Number of bins for the Y axis
    ymin, ymax    Limits for the Y axis
    ycalculator   A functor which takes the event record as the argument
                  and calculates the quantity to histogram on the Y axis
    wcalculator   A functor which takes the event record as the argument
                  and calculates the weight for the histogram entry. If
                  not provided, all weights are set to 1. If provided and
                  the returned weight is 0, the event will be ignored.
    """
    def __init__(self, name, title,
                 xlabel, nxbins, xmin, xmax, xcalculator,
                 ylabel, nybins, ymin, ymax, ycalculator,
                 wcalculator = None):
        AbsAnalysisModule.__init__(self, name)
        self.title = title
        self.xlabel = xlabel
        self.nxbins = int(nxbins)
        assert self.nxbins > 0, "Number of X bins must be positive"
        self.xmin = xmin*1.0
        self.xmax = xmax*1.0
        assert self.xmax > self.xmin, "Invalid X range specification"
        self.xcalculator = xcalculator
        self.ylabel = ylabel
        self.nybins = int(nybins)
        assert self.nybins > 0, "Number of Y bins must be positive"
        self.ymin = ymin*1.0
        self.ymax = ymax*1.0
        assert self.ymax > self.ymin, "Invalid Y range specification"
        self.ycalculator = ycalculator
        self.wcalculator = wcalculator
        self.data = np.zeros((self.nxbins, self.nybins), dtype=np.double)
        self.overflow = 0.0
        self._xbinwidth = (self.xmax - self.xmin)/self.nxbins
        self._ybinwidth = (self.ymax - self.ymin)/self.nybins

    def beginJob(self, allModuleNames):
        pass

    def endJob(self):
        plt.ioff()
        self.redraw()
        print("In module %s: %s overflow %s" % \
              (self.moduleName, self.overflow, self._makeZLabel()))

    def _makePlotTitle(self, zmin, zmax):
        if zmin is None and zmax is None:
            t = self.title
        elif zmin is None:
            t = "%s, zmax=%s" % (self.title, zmax)
        elif zmax is None:
            t = "%s, zmin=%s" % (self.title, zmin)
        else:
            t = "%s, zmin=%s, zmax=%s" % (self.title, zmin, zmax)
        return t

    def _makeZLabel(self):
        if self.wcalculator is None:
            zlabel = "Events"
        else:
            zlabel = "Weight"
        return zlabel

    def redraw(self, zmin=None, zmax=None):
        fig = plt.figure()
        axis = fig.add_subplot(111)
        mesh = self._colormeshData(axis, zmin, zmax)
        cbar = fig.colorbar(mesh, ax=axis)
        axis.set_xlabel(self.xlabel)
        axis.set_ylabel(self.ylabel)
        axis.set_title(self._makePlotTitle(zmin, zmax))
        cbar.ax.set_title(self._makeZLabel())
        fig.canvas.set_window_title(self.moduleName)
        plt.show()

    def beginRun(self, runNumber, runInfo):
        pass

    def endRun(self, runNumber, runInfo):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        if self.wcalculator is None:
            w = 1.0
        else:
            w = 1.0*self.wcalculator(eventRecord)
        if w == 0.0:
            return
        x = 1.0*self.xcalculator(eventRecord)
        if x >= self.xmax or x < self.xmin:
            self.overflow += w
            return
        y = 1.0*self.ycalculator(eventRecord)
        if y >= self.ymax or y < self.ymin:
            self.overflow += w
            return
        xbin = int((x - self.xmin)/self._xbinwidth)
        if xbin >= self.nxbins:
            xbin = self.nxbins - 1
        ybin = int((y - self.ymin)/self._ybinwidth)
        if ybin >= self.nybins:
            ybin = self.nybins - 1
        self.data[xbin, ybin] += w

    def _colormeshData(self, ax, zmin, zmax, **options):
        shape = self.data.shape
        xedges = np.linspace(self.xmin, self.xmax, num=shape[0]+1)
        yedges = np.linspace(self.ymax, self.ymin, num=shape[1]+1)
        xv, yv = np.meshgrid(xedges, yedges, indexing='ij')
        if zmin is None and zmax is None:
            return ax.pcolormesh(xv, yv, np.flip(self.data, 1), **options)
        if zmin is None:
            zmin = -1.0*sys.float_info.max
        if zmax is None:
            zmax = sys.float_info.max
        clipped = np.clip(self.data, zmin, zmax)
        return ax.pcolormesh(xv, yv, np.flip(clipped, 1), **options)
