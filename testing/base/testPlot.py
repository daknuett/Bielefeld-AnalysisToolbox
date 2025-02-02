# 
# testPlot.py
# 
# H. Sandmeyer
# 
# Test several of the methods in the plotting.py module. This script is a good example script to see what kind of
# fanciful things you can do with plots.
#

import numpy as np
import matplotlib.pyplot as plt
from latqcdtools.base.plotting import latexify, plot_file, plot_bar, set_params
from latqcdtools.statistics.statistics import plot_func
import latqcdtools.base.logger as logger

logger.set_log_level('INFO')

latexify()


def testPlot():

    plot_file("data1.txt", 0, 1, 2, 3, label="gauss noise", xlabel="$\\frac{1}{z}$", capsize = 2)
    plot_file("wurf.dat" , 0, 2, 3, 1, style="lines", label="quadratic", marker = 'o')
    plot_file("data2.txt", 0, 1, 2, 3, style="fill", alpha=0.3, label="linear")
    plot_file("data3.txt", 0, 1, 2, 3, style="fill", alpha=0.9, label="linear 2", legendpos = "best", capsize = 2)
    plot_bar([-6,-5],[1,2])
    plot_func(np.sin,xmin=-5,xmax=10)
    set_params(legendpos=9)
    plt.show()
    plt.close()


if __name__ == '__main__':
    testPlot()