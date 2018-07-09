"""Report for attr and net.

"""

from . import bnv
from . import heatmap
from . import line
from . import attrprocs
from . import netprocs
from ..util import path

class PlotAttr:
    """Plot an attr."""
    def __init__(self, attrname, attr, title, outfile):
        """Init the plot."""
        self.attrname = attrname
        self.attr = attr
        self.title = title
        self.outfile = outfile
        
    def run_plot_bnv(self):
        """Plot bnv."""
        namenoext, ext = path.splitext(self.outfile)
        curoutfile = namenoext + '_bnv' + ext
        plot = bnv.BNVPlot(None, self.attr, self.title, curoutfile, f_attrproc=attrprocs.get(self.attrname))
        plot.plot_attr()

    def run_plot_line(self):
        """Plot line."""
        plot = line.LinePlot([self.attr], self.title, self.outfile)
        plot.plot()
        
    def run(self):
        """Run the plots."""
        self.run_plot_line()
        self.run_plot_bnv()
    
class PlotNet:
    """Plot a net."""
    def __init__(self, netname, net, title, outfile):
        """Init the plot."""
        self.netname = netname
        self.net = net
        self.title = title
        self.outfile = outfile

    def run_plot_heatmap(self):
        """Plot heatmap."""
        plot = heatmap.HeatmapPlot(self.net, self.title, self.outfile, netprocs.get_valuerange(self.netname))
        plot.plot()
        
    def run(self):
        """Plot heatmap.
        
        TODO:
        Plot proper bnv.
        """
        self.run_plot_heatmap()
        
