# coding: utf-8

import os
import json
from vasplib import core
"""
Class representing Element.
"""
core_dir = os.path.dirname(core.__file__)
with open(os.path.join(core_dir, 'periodic_table.json'), 'r') as fp:
    pt_data = json.load(fp)

class Element(object):
    """
    Basic element oobject with all relevant properties.

    Args:
        symbol (str): Element symbol, e.g., 'H', 'Fe'

    Attributes:
        symbol (str): elemental symbol
        elem_data (dict): attributes dictionary

    Methods:
        get_attr(key): get the attribute key
        from_Z(Z): change the element to the one with atomic no. of Z
    """
    def __init__(self, symbol):
        self.symbol = symbol
        try:
            self.elem_data = pt_data[symbol]
        except KeyError:
            print("The element symbol {} is not valid.".format(symbol))

    def get_attr(self, key):
        """
        Args:
            key (str): Attribute of the element.
                Available keys: "Atomic mass", "Atomic no", "Atomic orbitals", etc.
        Returns the attribute key of the element.
        >>> Ag = Element('Ag')
        >>> Ag.get_attr("Atomic mass")
        107.8682
        """
        return self.elem_data[key]

    def from_Z(self, Z):
        """
        Change the object to the element with an atomic no. of Z in place.
        Args:
            Z (int): atomic no. of the element. 103 >= Z >= 1
        Returns:
            Element object
        >>> X = Element('Ag')
        >>> X = X.from_Z(54)
        >>> X.symbol
        "Xe"
        """
        for symbol in pt_data:
            if pt_data[symbol]["Atomic no"] == Z:
                return Element(symbol)
