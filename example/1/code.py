import os
import vasplib
from vasplib.output.vaspxml import VaspXml
from vasplib.plot.plot_band import plot_electronic_band_structure
from vasplib.analysis.electronic import analyze_electronic_property as AEP
import numpy as np
import json

#with open(os.path.join(os.path.dirname(vasplib.__file__),'../test/plot/parm_electronic_band_structure_plot.json'), 'r') as fp:
with open('parm_electronic_band_structure_plot.json', 'r') as fp: 
   args = json.load(fp)

AEP(args)
