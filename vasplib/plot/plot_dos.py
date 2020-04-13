import numpy as np
import matplotlib
from matplotlib.lines import Line2D
from matplotlib import ticker
import matplotlib.pyplot as plt

COLORS = ['r', 'b', 'g', 'm', 'c', 'y']
MARKERS = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
FILLED_COLORS = ['r', 'b', 'g', 'm', 'c', 'y']

def plot_electronic_dos(dos, args):
    plot_args = args["plot_parms"]
    NEDOS, ISPIN = args['NEDOS'], args['ISPIN']
    # domain of density of states
    xmin, ymin = np.amin(dos, axis = 0)
    xmax, ymax = np.amax(dos, axis = 0)
    plot_args['xmin'] = xmin
    plot_args['xmax'] = xmax
    plot_args['ymin'] = ymin
    plot_args['ymax'] = ymax

    # Default parameters for plotting
    plt.rcParams['font.family'] = plot_args.get('font family', 'Times New Roman')
    plt.rcParams['font.style'] = 'normal'
    plt.rcParams['font.weight'] = 'ultralight'

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)

    # line properties
    line_width = plot_args["Set"].get('line_width', 1.5)

    # Draw the line for total density of states
    row = 0
    if args.get('total', True):
        ax.plot(dos[row:row+NEDOS, 0], dos[row:row+NEDOS, 1], '-k', line_width)
        row += NEDOS
        if ISPIN == 2:
            ax.plot(dos[row:row+NEDOS, 0], dos[row:row+NEDOS, 1], '-k', line_width)
            row += NEDOS

    elements = args.get('elements', [])

    # plot partial DOS
    if len(elements) != 0:
        _, legends = _linetypes_legends_dos(args)
        legend_lines = [] # Store the customized lines
        for i in range(len(legends)):
            ax.plot(dos[row:row+NEDOS, 0], dos[row:row+NEDOS, 1], '-'+COLORS[i], line_width)
            legend_lines.append(Line2D([0], [0], color=COLORS[i], lw=line_width))
            row += NEDOS
            if ISPIN == 2:
                ax.plot(dos[row:row+NEDOS, 0], dos[row:row+NEDOS, 1], '-'+COLORS[i], line_width)
                row += NEDOS
        ax.legend(legend_lines, legends, frameon=False) # Add the legends


    if plot_args.get("Axes", {}):
        _set_axes(ax, plot_args)

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
    # X axis label
    ax.set_xlabel(args_xaxis.get("label", "Energy (eV)"),
        fontsize = args_xaxis.get("font size", 28))
    # X axis ticks
    if args_xaxis.get('ticks', {}):
        major_spacing, minor_spacing = args_xaxis['ticks'].values()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(major_spacing))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(minor_spacing))
    ax.tick_params('x', which = 'major', length = args_xaxis['major ticks parameters']['length'],
        width = args_xaxis['major ticks parameters']['width'], direction = 'in', right = True, top = True,
        labelsize=args_xaxis['major ticks parameters']['fontsize'])
    ax.tick_params('x', which = 'minor', length = args_xaxis['minor ticks parameters']['length'],
        width = args_xaxis['minor ticks parameters']['width'], direction = 'in', right = True, top = True)

    # Y axis limits
    if args_yaxis.get("lim", []):
        ax.set_ylim(args_yaxis["lim"][0], args_yaxis["lim"][1])
    else:
        ax.set_ylim(plot_args['ymin'], plot_args['ymax'])
    # Y axis label
    ax.set_ylabel(args_yaxis.get("label", "DOS (states/eV)"),
        fontsize = args_yaxis.get("font size", 28))
    # Y axis ticks
    if args_yaxis.get('ticks', {}):
        major_spacing, minor_spacing = args_yaxis['ticks'].values()
        ax.yaxis.set_major_locator(ticker.MultipleLocator(major_spacing))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_spacing))
    ax.tick_params('y', which = 'major', length = args_yaxis['major ticks parameters']['length'],
        width = args_yaxis['major ticks parameters']['width'], direction = 'in', right = True, top = True,
        labelsize=args_yaxis['major ticks parameters']['fontsize'])
    ax.tick_params('y', which = 'minor', length = args_yaxis['minor ticks parameters']['length'],
        width = args_yaxis['minor ticks parameters']['width'], direction = 'in', right = True, top = True)

def _print(fig, plot_args):
    print_args = plot_args['Print']
    fig.figaspect = print_args.get('figaspect', 2)
    fig.savefig(print_args.get('fname', 'dos.pdf'),
        format = print_args.get('format', 'pdf'),
        dpi = print_args.get('dpi', 1200),
        bbox_inches='tight')

def _linetypes_legends_dos(args):
    """
    Generate the line types and legends for all the lines.
    e.g., (['-r', '-b', '-g'], ['Co-px', 'Co-py', 'S']
    """
    line_types = []
    legends = []
    i = 0

    for element, orbits in zip(args["elements"], args["orbitals"]):
        if orbits == 'all':
            line_types.append('-' + COLORS[i])
            legends.append(element)
            i += 1
        else:
            for orbit in orbits[:]:
                line_types.append('-' + COLORS[i])
                legends.append(element + '-' + orbit)
                i += 1

    return line_types, legends
