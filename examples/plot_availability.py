"""Plot of the results of the Data Availability Test for EIDA.

.. moduleauthor:: Javier Quinteros <javier@gfz-potsdam.de>, GFZ Potsdam, Germany
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def main():
    desc = 'Generate an availability plot from the text file written by eida_test.py.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-s', '--subplots', default=3, type=int,
                        help='Number of subplots in which networks should be split (default: 3).')
    parser.add_argument('-i', '--input', default='results.txt',
                        help=('File from which results should be read. Tipically this is '
                              'the file generated by eida_test.py (default: results.txt).'))

    args = parser.parse_args()

    fin = open(args.input)
    networks = set()
    netyearavail = dict()
    netyearwfc = dict()
    years = set()

    for line in fin.readlines():
        year, net, sta, cha, percavailable, minutes, wfc, inventory = line.split(' ')
        year = int(year)
        percavailable = float(percavailable)
        wfc = float(wfc)
        minutes = float(minutes)

        yn = '%s.%s' % (year, net)
        # Check in which case of coherency are we considering WFCatalog and data
        if yn not in netyearwfc:
            # Default value
            netyearwfc[yn] = 2

        if percavailable == wfc:
            # Perfect situation. We have data and WFC information
            netyearwfc[yn] = min(netyearwfc[yn], 2)
        if percavailable < wfc:
            # print('1', year, net, sta, cha, percavailable, minutes, wfc)
            # We have less data than WFC information. Potentially meaning gaps
            netyearwfc[yn] = min(netyearwfc[yn], 1)
        if percavailable > wfc:
            # print('0', year, net, sta, cha, percavailable, minutes, wfc)
            # WFCatalog information missing!
            netyearwfc[yn] = min(netyearwfc[yn], 0)

        # Calculate % data received
        try:
            netyearavail[yn] = (netyearavail[yn][0] + percavailable, netyearavail[yn][1] + 1)
        except KeyError:
            netyearavail[yn] = (percavailable, 1)

        networks.add(net)
        years.add(year)

    # print(netyearwfc)

    # Create values for the axes
    labelnets = list(networks)
    labelnets.sort()
    listyears = list(years)
    listyears.sort()

    # Create a matrix to store the values to show in the availability plot
    values = np.empty((len(labelnets), len(listyears)))
    values[:] = np.nan

    for net in netyearavail:
        y, n = net.split('.')
        y = int(y)
        values[labelnets.index(n), listyears.index(y)] = min(100.0,
                                                             netyearavail[net][0]/netyearavail[net][1])

    makeavailabilityplot(labelnets, listyears, values, args.subplots)

    # Create a matrix to store the values to show in wfc plot
    values = np.empty((len(labelnets), len(listyears)))
    values[:] = np.nan

    for net in netyearwfc:
        y, n = net.split('.')
        y = int(y)
        values[labelnets.index(n), listyears.index(y)] = netyearwfc[net]

    makeavailabilityplot(labelnets, listyears, values, args.subplots, ticks=[0, 1, 2])


def makeavailabilityplot(labelnets, listyears, values, subplots, ticks=None):
    # Generate the plot based on the axes and the values
    if ticks is None:
        ticks = range(0, 101, 10)
    cmap = LinearSegmentedColormap.from_list('rg', ["r", "y", "g"], N=len(ticks))

    # Split the matrix and labels in subplots
    fig, axs = plt.subplots(1, subplots)

    axs[0].set_ylabel('Network')
    axs[int(subplots/2)].set_xlabel('Years')

    # fig.suptitle("Data availability test using Obspy.RoutingClient")

    for i in range(subplots):
        step = len(labelnets)/subplots
        idxfrom = int(step * i)
        idxto = int(step * (i+1)) - 1

        if i == subplots-1:
            idxto = len(labelnets)

        # print(idxfrom, idxto)
        ax = axs[i]
        im = ax.imshow(values[idxfrom:idxto+1, :], cmap=cmap, vmin=0, vmax=max(ticks))

        # We want to show all ticks...
        ax.set_xticks(np.arange(len(listyears)))
        ax.set_yticks(np.arange(idxto-idxfrom+1))

        # ... and label them with the respective list entries
        ax.set_xticklabels(listyears)
        ax.set_yticklabels(labelnets[idxfrom:idxto+1])

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        # # Loop over data dimensions and create text annotations.
        # for idxn in range(idxfrom, idxto+1):
        #     for j in range(len(years)):
        #         try:
        #             if np.isnan(values[idxn, j]):
        #                 text = ax.text(j, idxn-idxfrom, 'NA',
        #                                ha="center", va="center", color="black")
        #         except Exception:
        #             pass

    # ax = axs[args.subplots]
    # set the limits of the plot to the limits of the data
    fig.colorbar(im, ticks=ticks)

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
