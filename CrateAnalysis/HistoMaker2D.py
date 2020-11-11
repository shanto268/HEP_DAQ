#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A module for plotting 2-d histograms of various numeric quantities
"""

__author__ = "Igor Volobouev (i.volobouev@ttu.edu)"
__version__ = "0.2"
__date__ = "June 25 2020"

import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.ndimage.interpolation import rotate
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
    def __init__(self,
                 name,
                 title,
                 xlabel,
                 nxbins,
                 xmin,
                 xmax,
                 xcalculator,
                 ylabel,
                 nybins,
                 ymin,
                 ymax,
                 ycalculator,
                 wcalculator=None,
                 rotate=False):

        AbsAnalysisModule.__init__(self, name)
        self.name = name
        self.defaultValue = -0
        self.title = title
        self.xlabel = xlabel
        self.nxbins = int(nxbins)
        assert self.nxbins > 0, "Number of X bins must be positive"
        self.xmin = xmin * 1.0
        self.xmax = xmax * 1.0
        assert self.xmax > self.xmin, "Invalid X range specification"
        self.xcalculator = xcalculator
        self.ylabel = ylabel
        self.nybins = int(nybins)
        assert self.nybins > 0, "Number of Y bins must be positive"
        self.ymin = ymin * 1.0
        self.ymax = ymax * 1.0
        assert self.ymax > self.ymin, "Invalid Y range specification"
        self.ycalculator = ycalculator
        self.wcalculator = wcalculator
        #self.data = np.zeros((self.nxbins, self.nybins), dtype=np.double)
        #   self.data = np.empty((self.nxbins, self.nybins))
        self.data = np.full((self.nxbins, self.nybins),
                            self.defaultValue,
                            dtype=np.double)
        #self.data = np.empty((self.nxbins, self.nybins), dtype=np.double)
        self.overflow = 0.0
        self._xbinwidth = (self.xmax - self.xmin) / self.nxbins
        self._ybinwidth = (self.ymax - self.ymin) / self.nybins
        self.doRotate = rotate

    def beginJob(self, allModuleNames):
        pass

    def endjob(self):
        plt.ioff()
        self.data[self.data == self.defaultvalue] = np.nan
        self.redraw()
        print("in module %s: %s overflow %s" % \
              (self.modulename, self.overflow, self._makezlabel()))

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
        # plt.savefig("{}_{}.png".format(self.name, self.runNumber))
        plt.show()

    def beginRun(self, runNumber, runInfo):
        self.runNumber = runNumber
        self.title = self.title + " | Run Number: " + str(
            self.runNumber) + " | " + self.title_string
        pass

    def endRun(self, runNumber, runInfo):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        if self.wcalculator is None:
            w = 1.0
        else:
            w = 1.0 * self.wcalculator(eventRecord)
        if w == 0.0:
            return
        try:
            x = 1.0 * self.xcalculator(eventRecord)
        except:
            return
        if x >= self.xmax or x < self.xmin:
            self.overflow += w
            return
        try:
            y = 1.0 * self.ycalculator(eventRecord)
        except:
            return
        if y >= self.ymax or y < self.ymin:
            self.overflow += w
            return
        try:
            xbin = int((x - self.xmin) / self._xbinwidth)
        except:
            return
        if xbin >= self.nxbins:
            xbin = self.nxbins - 1
        ybin = int((y - self.ymin) / self._ybinwidth)
        if ybin >= self.nybins:
            ybin = self.nybins - 1
        self.data[xbin, ybin] += w

    def _colormeshData(self, ax, zmin, zmax, **options):
        if not self.doRotate:
            shape = self.data.shape
            xedges = np.linspace(self.xmin, self.xmax, num=shape[0] + 1)
            yedges = np.linspace(self.ymax, self.ymin, num=shape[1] + 1)
            xv, yv = np.meshgrid(xedges, yedges, indexing='ij')
            # print("len of xv: {}".format(len(xv)))
            # print("xv: {}".format(xv))
            # print("yv[0]: {}".format(yv[0]))
            # print("len of yv[0]: {}".format(len(yv[0])))
            if zmin is None and zmax is None:
                return ax.pcolormesh(xv, yv, np.flip(self.data, 1), **options)
            if zmin is None:
                zmin = -1.0 * sys.float_info.max
            if zmax is None:
                zmax = sys.float_info.max
            clipped = np.clip(self.data, zmin, zmax)
            return ax.pcolormesh(xv, yv, np.flip(clipped, 1), **options)
        elif self.doRotate:
            shape = self.data.shape
            xedges = np.linspace(self.xmin, self.xmax, num=shape[0] + 1)
            yedges = np.linspace(self.ymax, self.ymin, num=shape[1] + 1)
            # xv, yv = np.meshgrid(xedges, yedges, indexing='ij')
            xv, yv = self.DoRotation(xedges, yedges, RotRad=-44.75)
            #print(xv, yv)
            if zmin is None and zmax is None:
                return ax.pcolormesh(xv, yv, np.flip(self.data, 1), **options)
            if zmin is None:
                zmin = -1.0 * sys.float_info.max
            if zmax is None:
                zmax = sys.float_info.max
            clipped = np.clip(self.data, zmin, zmax)
            return ax.pcolormesh(xv, yv, np.flip(clipped, 1), **options)

    def DoRotation(self, xspan, yspan, RotRad=0):
        """Generate a meshgrid and rotate it by RotRad radians."""
        # Clockwise, 2D rotation matrix
        RotMatrix = np.array([[np.cos(RotRad), np.sin(RotRad)],
                              [-np.sin(RotRad),
                               np.cos(RotRad)]])
        x, y = np.meshgrid(xspan, yspan)
        return np.einsum('ji, mni -> jmn', RotMatrix, np.dstack([x, y]))


# def rotate(self, p, origin=(0, 0), degrees=0):
# angle = np.deg2rad(degrees)
# R = np.array([[np.cos(angle), -np.sin(angle)],
# [np.sin(angle), np.cos(angle)]])
# o = np.atleast_2d(origin)
# p = np.atleast_2d(p)
# return np.squeeze((R @ (p.T - o.T) + o.T).T)
