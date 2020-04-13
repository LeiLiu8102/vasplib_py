import os
import numpy as np
from vasplib.output.vaspxml import VaspXml
from vasplib.plot.plot_dos import plot_electronic_dos
from vasplib.plot.plot_band import plot_electronic_band_structure

def analyze_electronic_property(args: dict):
    """
    Analyze the electronic properties according to the arguments in args.
    Args:
        args (dict)
    """
    # Get electronic dos
    if args["data_type"] == "dos":
        analyze_electronic_dos(args)

    # Get electronic band structure
    elif args["data_type"] == "band structure":
        analyze_electronic_band_structure(args)

    else:
        raise ValueError("Not supported data type: {}".format(args["data type"]))

def analyze_electronic_dos(args):
    """
    Analyze the electronic density of states according to the arguments in args.
    Args:
        args (dict): parameters
    """
    xml = VaspXml(args["fname"])

    args['ISPIN'] = xml.get_parameter('ISPIN')
    args['NEDOS'] = xml.get_parameter("NEDOS")

    if args.get('total', True):
        dos_total = xml.get_total_dos()

    elements = args.get('elements', [])

    # Only total DOS is requested
    if len(elements) == 0:
        dos = dos_total
    # Partial DOS is requested
    else:
        orbitals = args.get('orbitals', [])
        if len(elements) != len(orbitals):
            raise ValueError("Length of 'elements' and 'orbitals' must equal.")
        dos_partial = _get_partial_electronic_dos(args)
        dos = np.concatenate((dos_total, dos_partial), axis = 0)

    if args.get('out', ''):
        np.savetxt(args['out'], dos) # Write the dos to a txt file

    if args.get('plot', False):
        plot_electronic_dos(dos, args) # Plot the dos figure

def _get_partial_electronic_dos(args):
    """
    Get partial electronic dos for vasprun.xml file.
    """
    xml = VaspXml(args["fname"])
    pdos = np.empty((0, 2), dtype = float)
    for element, orbits in zip(args["elements"], args["orbitals"]):
        if orbits == 'all':
            pdos = np.concatenate((pdos, xml.get_total_dos_element(element)), axis = 0)
        else:
            for orbit in orbits[:]:
                pdos = np.concatenate((pdos, xml.get_dos_element(element, orbit)), axis = 0)
    return pdos

def analyze_electronic_band_structure(args):
    """
    Analyze the electronic band structure according to the arguments in args.
    Args:
        args (dict): parameters
    """
    xml = VaspXml(args["fname"])
    args['ISPIN'] = xml.get_parameter('ISPIN')
    args['NBANDS'] = xml.get_parameter("NBANDS")
    args['NKPTS'] = xml.get_nkpts()

    band = [] # [band_total, band_partial]
    if args.get('total', True):
        band_total = xml.get_electronic_band()
    else:
        band_total = np.empty(0)

    elements = args.get('elements', [])

    # Only total band is required
    if len(elements) == 0:
        band_partial = np.empty(0)
    # Partial band structure is required
    if len(elements) != 0:
        orbitals = args.get('orbitals', [])
        if len(elements) != len(orbitals):
            raise ValueError("Length of 'elements' and 'orbitals' must equal.")
        band_partial = _get_partial_band(args)

    if args.get('out', ''):
        if band_total.size > 0:
            fout_total = os.path.join(args['out'], 'band_total.dat')
            np.savetxt(fout_total, band_total)
        if band_partial.size > 0:
            fout_partial = os.path.join(args['out'], 'band_partial.dat')
            np.savetxt(fout_partial, band_partial)

    # Get high symmetry kpoints
    special_k = xml.get_high_symmetry_kpoints()

    if args.get('plot', False):
        plot_electronic_band_structure(band_total, band_partial, special_k, args) # Plot the band structure figure

def _get_partial_band(args):
    """
    Get partial electronic dos for vasprun.xml file.
    """
    xml = VaspXml(args["fname"])
    pband = np.empty((0, 3), dtype = float)
    for element, orbits in zip(args["elements"], args["orbitals"]):
        if orbits == 'all':
            pband = np.concatenate((pband, xml.get_electronic_band_element(element)), axis = 0)
        else:
            for orbit in orbits[:]:
                pband = np.concatenate((pband, xml.get_electronic_band_element_orbit(element, orbit)), axis = 0)
    return pband
