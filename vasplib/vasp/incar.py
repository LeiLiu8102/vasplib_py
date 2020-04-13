# coding: utf-8

import os
import json
import vasplib
"""
Class for reading/manuoulating/writing INCAR file and parameters.
"""

# Load tags name from incarTags.json
tag_file = os.path.join(os.path.dirname(vasplib.__file__),'vasp/incarTags.json')
with open(tag_file, 'r') as fp:
    tag_data = json.load(fp)
    valid_tags = [tag["tag"] for tag in tag_data]

class Incar(object):
    """
    INCAR object for reading and writing INCAR files.
    Construction:
        myIncar = Incar()
        myIncar = Incar({"ENCUT": 600, "ISIF": '3'})
    Methods:
        get_attr("ENCUT")
    """
    def __init__(self, params = None):
        """
        Create an Incar object.
        Args:
        params (dict): A set of input parameters as a dictionary.
            dict: {key(str), value(str)}
        """
        self.pairs = {} # Storing the key-value pairs in Incar object
        if params:
            self.update(params)

    def get_attr(self, tag):
        """
        Return the value of the tag in the INCAR object.
        Args:
            tag (str): name of the tag (key), e.g., "ENCUT"
        """
        return self.pairs.get(tag, None)

    def from_file(self, filename):
        """
        Reads an Incar object from a file.
        Args:
        filename (str): Filename of the file.
        """
        with open(filename, 'r') as fp:
            lines = fp.readlines()

        # Remove comments starting with '!' or '#', and remove leading/tailing
        # spaces, EOL
        def beautify(string):
            string = string.rstrip('\n')
            if '!' in string:
                string = string.split('!', 1)[0]
            if '#' in string:
                string = string.split('#', 1)[0]
            string = string.strip()
            return string

        # Remove the empty lines and lines with only comments
        for i, line in enumerate(lines):
            lines[i] = beautify(line)
        for line in lines[:]:
            if not line:
                lines.remove(line)

        for line in lines:
            key = line.split('=', 1)[0].strip()
            value = line.split('=', 1)[1].strip()
            self.update({key: value})

    def update(self, params):
        """
        Update the parameters into the Incar project.
        Args:
        params (dict): A set of input parameters as a dictionary.
        """
        for tag, value in params.items():
            if tag in valid_tags:
                self.pairs[tag] = value

    def remove(self, tag):
        """
        Remove the tag from the Incar object
        """
        del self.pairs[tag]

    def write_file(self, filename):
        """
        Write Incar to a file.
        Args:
        filename (str): the filename to write to.
        """
        with open(filename, 'w') as fp:
            for tag, value in self.pairs.items():
                fp.write(tag + ' = ' + value + '\n')
