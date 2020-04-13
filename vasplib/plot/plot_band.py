import numpy as np
import matplotlib
from matplotlib.lines import Line2D
from matplotlib import ticker
import matplotlib.pyplot as plt

COLORS = ['r', 'lime', 'b', 'm', 'c', 'y']
## TODO: specify colors by user
MARKERS = ('o', 's', 'd', '<', '>', '8', 'v', 'p', '*', 'h', 'H', 'D', '^', 'P', 'X')
FILLED_COLORS = ['r', 'lime', 'b', 'm', 'c', 'y']

def plot_electronic_band_structure(band_total, band_partial, special_k, args):
    """
    Note: band_toal and band_partial must not be empty at the same time
    """
    plot_args = args["plot_parms"]
    NBANDS, ISPIN, NKPTS = args['NBANDS'], args['ISPIN'], args['NKPTS']
    # array of kpoints
    kpt_list = band_total[0:NKPTS, 0] if band_total.size > 0 else band_partial[0:NKPTS, 0]
    # domain of the plot
    xmin, xmax = np.min(kpt_list), np.max(kpt_list)
    ymin = np.min(band_total[:, 1:] if band_total.size > 0 else band_partial[:, 1])
    ymax = np.max(band_total[:, 1:] if band_total.size > 0 else band_partial[:, 1])

    plot_args['xmin'] = xmin
    plot_args['xmax'] = xmax
    plot_args['ymin'] = ymin
    plot_args['ymax'] = ymax

    # Default parameters for plotting
    plt.rcParams['font.family'] = plot_args.get('font family', 'Times New Roman')
    plt.rcParams['font.style'] = 'normal'
    plt.rcParams['font.weight'] = 'ultralight'

    if ISPIN == 2:
        fig = plt.figure(figsize=(15, 5))
        ax0 = fig.add_subplot(121)
        ax1 = fig.add_subplot(122)
    else:
        fig = plt.figure(figsize=(5, 5))
        ax0 = fig.add_subplot(111)

    # line properties
    line_width = plot_args["Set"].get('line_width', 1.5)
    # Draw the line for total band structure
    if args.get('total', True):
        for col in range(1, NBANDS + 1):
            ax0.plot(kpt_list, band_total[0:NKPTS, col], '-k', linewidth = line_width)
            if ISPIN == 2:
                ax1.plot(kpt_list, band_total[NKPTS:2*NKPTS, col], '-k', linewidth = line_width)

    elements = args.get('elements', [])

    # plot partial band structure
    if len(elements) != 0:
        symbol_size = plot_args["Set"].get('symbol_size', 15)
        band_partial[:, 2] = band_partial[:, 2] * symbol_size # Enlarge the symbol size
        legends = _legends(args) # Get the legend texts
        legend_lines = [] # Store the customized lines
        if plot_args["Set"].get('symbol_type', []):
            markers = plot_args["Set"].get('symbol_type')
        else:
            markers = MARKERS
        row = 0 # record current row number
        line_index = 0 # record line set index
        for element, orbits in zip(args["elements"], args["orbitals"]):
            # only one set of lines for this element
            if orbits == 'all':
                for i in range(NBANDS):
                    ax0.scatter(kpt_list, band_partial[row:row+NKPTS, 1], band_partial[row:row+NKPTS, 2],
                                c = COLORS[line_index], marker = markers[line_index])
                    row += NKPTS
                if ISPIN == 2:
                    for i in range(NBANDS):
                        ax1.scatter(kpt_list, band_partial[row:row+NKPTS, 1], band_partial[row:row+NKPTS, 2],
                                c = COLORS[line_index], marker = markers[line_index])

                        row += NKPTS
                legend_lines.append(Line2D([0], [0], marker=markers[line_index], color='none',
                          markerfacecolor=COLORS[line_index], markeredgewidth = 0))
                line_index += 1
            # potentially several sets of lines for this element
            else:
                for orbit in orbits[:]:
                    for i in range(NBANDS):

                        ax0.scatter(kpt_list, band_partial[row:row+NKPTS, 1], band_partial[row:row+NKPTS, 2],
                                    c = COLORS[line_index], marker = markers[line_index])
                        row += NKPTS
                    if ISPIN == 2:
                        for i in range(NBANDS):
                            ax1.scatter(kpt_list, band_partial[row:row+NKPTS, 1], band_partial[row:row+NKPTS, 2],
                                        c = COLORS[line_index], marker = markers[line_index])
                            row += NKPTS
                    legend_lines.append(Line2D([0], [0], marker=markers[line_index], color='none',
                              markerfacecolor=COLORS[line_index], markeredgewidth = 0))
                    line_index += 1

        ax0.legend(legend_lines, legends, frameon=False) # Add the legends

    # Draw the line for special k points
    for k in special_k:
        ax0.plot([k, k], [ymin, ymax], '--k', linewidth = line_width)
        if ISPIN == 2:
            ax1.plot([k, k], [ymin, ymax], '--k', linewidth = line_width)

    if plot_args.get("Axes", {}):
        _set_axes(ax0, plot_args)
        if ISPIN == 2:
            _set_axes(ax1, plot_args)

    if plot_args.get("Print", {}):
        _print(fig, plot_args)

def _set_axes(ax, plot_args):
    """
    Set axis properties.
    """
    axes_args = plot_args['Axes']
    ax.linewidth = axes_args.get("linewidth", 1)
    args_xaxis = axes_args.get("Xaxis", {})
    args_yaxis = axes_args.get("Yaxis", {})

    # X axis limits
    if args_xaxis.get("lim", []):
        ax.set_xlim(args_xaxis["lim"][0], args_xaxis["lim"][1])
    else:
        ax.set_xlim(plot_args['xmin'], plot_args['xmax'])
    # # X axis label
    # ax.set_xlabel(args_xaxis.get("label", "Energy (eV)"),
    #     fontsize = args_xaxis.get("font size", 28))
    # # X axis ticks
    # if args_xaxis.get('ticks', {}):
    #     major_spacing, minor_spacing = args_xaxis['ticks'].values()
    #     ax.xaxis.set_major_locator(ticker.MultipleLocator(major_spacing))
    #     ax.xaxis.set_minor_locator(ticker.MultipleLocator(minor_spacing))
    # ax.tick_params('x', which = 'major', length = args_xaxis['major ticks parameters']['length'],
    #     width = args_xaxis['major ticks parameters']['width'], direction = 'in', right = True, top = True,
    #     labelsize=args_xaxis['major ticks parameters']['fontsize'])
    # ax.tick_params('x', which = 'minor', length = args_xaxis['minor ticks parameters']['length'],
    #     width = args_xaxis['minor ticks parameters']['width'], direction = 'in', right = True, top = True)
    ax.tick_params('x', which = 'both', bottom = False, top = False, labelbottom=False)

    # Y axis limits
    if args_yaxis.get("lim", []):
        ax.set_ylim(args_yaxis["lim"][0], args_yaxis["lim"][1])
    else:
        ax.set_ylim(plot_args['ymin'], plot_args['ymax'])
    # Y axis label
    ax.set_ylabel(args_yaxis.get("label", "Energy (eV)"),
        fontsize = args_yaxis.get("font size", 28))
    # Y axis ticks
    if args_yaxis.get('ticks', {}):
        major_spacing, minor_spacing = args_yaxis['ticks'].values()
        ax.yaxis.set_major_locator(ticker.MultipleLocator(major_spacing))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_spacing))
    ax.tick_params('y', which = 'major', length = args_yaxis['major ticks parameters']['length'],
        width = args_yaxis['major ticks parameters']['width'], direction = 'in', right = True,
        labelsize=args_yaxis['major ticks parameters']['fontsize'])
    ax.tick_params('y', which = 'minor', length = args_yaxis['minor ticks parameters']['length'],
        width = args_yaxis['minor ticks parameters']['width'], direction = 'in', right = True)

def _print(fig, plot_args):
    print_args = plot_args['Print']
    fig.figaspect = print_args.get('figaspect', 2)
    fig.savefig(print_args.get('fname', 'dos.pdf'),
        format = print_args.get('format', 'pdf'),
        dpi = print_args.get('dpi', 1200),
        bbox_inches='tight')

def _legends(args):
    """
    Generate the legends for all the lines.
    e.g., ['Co-px', 'Co-py', 'S']
    """
    # If legends are specified in args
    plot_args = args["plot_parms"]
    if plot_args['Set'].get('legend', []):
        return plot_args['Set']['legend']

    legends = []
    i = 0

    for element, orbits in zip(args["elements"], args["orbitals"]):
        if orbits == 'all':
            legends.append(element)
            i += 1
        else:
            for orbit in orbits[:]:
                legends.append(element + '-' + orbit)
                i += 1

    return legends
