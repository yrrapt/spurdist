#!/usr/bin/python2

from PyQt4.Qt import *
from PyQt4.Qwt5 import *

from core.helper import styles

class chart(QwtPlot):
    colours = {'red'    : Qt.red,
               'green'  : Qt.green,
               'blue'   : Qt.blue,
               'yellow' : Qt.yellow,
               'magenta': Qt.magenta}
    styles = {'-' : Qt.SolidLine,
              '--': Qt.DashLine,
              ':' : Qt.DotLine,
              '-.': Qt.DashDotLine}

    @staticmethod
    def getPen(colour, style):
        return QPen(chart.colours[colour], 2, chart.styles[style])

    def __init__(self, spurset, fef, parent):
        QwtPlot.__init__(self, parent)
        self.spurset, self.mx, self.fef = spurset, spurset.mixer, fef
        self.spurstyles = styles()
        self.spurlines = {}
        self.feflines = []

        self.setCanvasBackground(Qt.white)
        self.setAxisScale(QwtPlot.xBottom, self.spurset.RFmin,
                          self.spurset.RFmax)
        self.setAxisScale(QwtPlot.yLeft, -self.spurset.dspan/2,
                          self.spurset.dspan/2)

        grid = QwtPlotGrid()
        grid.setMajPen(QPen(Qt.black, 1, Qt.DashLine))
        grid.attach(self)

    def redraw(self, obj):
        if obj is self.spurset or obj is self.mx:
            lines = self.spurset.spurset()
            legend_flag = (set(lines) != set(self.spurlines))
            remove = set(self.spurlines) - set(lines)
            new = set(lines) - set(self.spurlines)

            # remove invalid lines
            for key in set(self.spurlines) & set(lines):
                for line in self.spurlines[key]:
                    if line['xys'] not in lines[key]:
                        remove.add(key)
                        new.add(key)
            for key in remove:
                for line in self.spurlines[key]:
                    line['mpl'].detach()
                del self.spurlines[key]

            # draw new ones
            for m,n in new:
                xys  = lines[(m,n)]
                c,s = self.spurstyles[(m,n)]
                self.spurlines[(m,n)] = []
                for (li, leg) in zip(xys, (fmt_mn(m,n), '')):
                    chline = QwtPlotCurve(leg)
                    chline.setPen(chart.getPen(c,s))
                    chline.setRenderHint(QwtPlotItem.RenderAntialiased)
                    chline.attach(self)
                    chline.setData((li[0][0], li[1][0]),
                                   (li[0][1], li[1][1]))
                    self.spurlines[(m,n)].append({'xys': li, 'mpl': chline})

            #if legend_flag:
            #    self.ax.legend(loc=(1.03,0))
            #self.ax.set_ylim(-0.5*self.spurset.dspan, 0.5*self.spurset.dspan)
            #self.ax.set_xlim(self.spurset.RFmin, self.spurset.RFmax)

        elif obj is self.fef:
            #remove old fef lines
            for line in self.feflines:
                line.detach()
            self.feflines = []
            # draw new ones
            def mkline(xys, pick=None):
                line = QwtPlotCurve('')
                line.setPen(QPen(Qt.black, 2))
                line.setRenderHint(QwtPlotItem.RenderAntialiased)
                line.setData(xys[0], xys[1])
                self.feflines.append(line)
                line.attach(self)
                return line
            self.fef.startline = mkline(self.fef.minf, 10)
            self.fef.stopline = mkline(self.fef.maxf, 10)
            mkline(self.fef.top)
            mkline(self.fef.bot)

        self.replot()

def fmt_mn(m, n):
    rf = (str(abs(m)) if abs(m) > 1 else '') + 'RF'
    lo = (str(abs(n)) if abs(n) > 1 else '') + 'LO'
    if m * n > 0:
        return rf + ' + ' + lo
    elif m == 0:
        return lo
    elif n == 0:
        return rf
    elif m > 0:
        return rf + ' - ' + lo
    else:
        return lo + ' - ' + rf
