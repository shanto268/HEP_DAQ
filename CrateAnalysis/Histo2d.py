import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.ndimage.interpolation import rotate
import matplotlib.colors as colors


class Histo2D:
    def __init__(self,
                 name,
                 title,
                 xlabel,
                 nxbins,
                 xmin,
                 xmax,
                 xvals,
                 ylabel,
                 nybins,
                 ymin,
                 ymax,
                 yvals,
                 pdf,
                 wcalculator=None,
                 rotate=False,
                 zIsLog=True):

        self.name = name
        self.defaultValue = -0
        self.title = title
        self.xlabel = xlabel
        self.nxbins = int(nxbins)
        assert self.nxbins > 0, "Number of X bins must be positive"
        self.xmin = xmin * 1.0
        self.xmax = xmax * 1.0
        assert self.xmax > self.xmin, "Invalid X range specification"
        self.xvals = xvals
        self.ylabel = ylabel
        self.nybins = int(nybins)
        assert self.nybins > 0, "Number of Y bins must be positive"
        self.ymin = ymin * 1.0
        self.ymax = ymax * 1.0
        assert self.ymax > self.ymin, "Invalid Y range specification"
        self.yvals = yvals
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
        # print("self._xbinwidth : {}".format(self._xbinwidth))
        # print("self._ybinwidth : {}".format(self._ybinwidth))
        # print("self.xmin : {}".format(self.xmin))
        # print("self.ymin : {}".format(self.ymin))
        # print("self.ymax : {}".format(self.ymax))
        # print("self.xmax : {}".format(self.xmax))
        self.doRotate = rotate
        self.pdf = pdf
        self.zIsLog = zIsLog
        # print(self.pdf)
        self.plot2DHist()
        self.endjob()

    def endjob(self):
        plt.ioff()
        # print(self.data)
        self.data[self.data == self.defaultValue] = np.nan
        #print("in module %s: %s overflow %s" % \
        #      (self.name, self.overflow, self._makeZLabel()))
        if not self.pdf:
            self.redraw()
        else:
            x = self.redraw()
            return x

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
        xbins, ybins, overflow = self.nxbins, self.nybins, self.overflow
        textstr = "XBins: {:0.0f}\nYBins: {:0.0f}\nOverflow: {}".format(
            xbins, ybins, overflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)
        axis.text(0.75,
                  0.95,
                  textstr,
                  transform=axis.transAxes,
                  fontsize=10,
                  verticalalignment='top',
                  bbox=props)
        cbar.ax.set_title(self._makeZLabel())
        if not self.pdf:
            fig.canvas.set_window_title(self.name)
            plt.show()
        else:
            plt.savefig(self.name + ".png")
            return fig

    def plot2DHist(self):
        for i in range(len(self.xvals)):
            self.processEvent([self.xvals[i], self.yvals[i]])

    def processEvent(self, eventRecord):
        if self.wcalculator is None:
            w = 1.0
        else:
            w = 1.0 * self.wcalculator
        if w == 0.0:
            return
        try:
            x = 1.0 * eventRecord[0]
        except:
            return
        if x >= self.xmax or x < self.xmin:
            self.overflow += w
            return
        try:
            y = 1.0 * eventRecord[1]
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
        try:
            ybin = int((y - self.ymin) / self._ybinwidth)
        except:
            return
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
                if self.zIsLog:
                    return ax.pcolormesh(xv,
                                         yv,
                                         np.flip(self.data, 1),
                                         norm=colors.LogNorm(vmin=zmin,
                                                             vmax=zmax),
                                         cmap='RdBu_r',
                                         rasterized=True,
                                         **options)
                else:
                    return ax.pcolormesh(xv,
                                         yv,
                                         np.flip(self.data, 1),
                                         rasterized=True,
                                         **options)

            if zmin is None:
                zmin = -1.0 * sys.float_info.max
            if zmax is None:
                zmax = sys.float_info.max
            clipped = np.clip(self.data, zmin, zmax)
            if self.zIsLog:
                return ax.pcolormesh(xv,
                                     yv,
                                     np.flip(self.data, 1),
                                     norm=colors.LogNorm(vmin=zmin, vmax=zmax),
                                     cmap='RdBu_r',
                                     rasterized=True,
                                     **options)
            else:
                return ax.pcolormesh(xv,
                                     yv,
                                     np.flip(self.data, 1),
                                     rasterized=True,
                                     **options)

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
