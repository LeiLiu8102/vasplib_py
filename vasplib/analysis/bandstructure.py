import numpy as np
import math
import scipy.constants as constants

class Bandstructure(object):
    """
    isotropic effective mass, no spin
    """
    def __init__(self, kpoints, eigenvalues, efermi = 0):
        """
        Create a band structure object.
        Args:
            kpoints (np.array): nkpts * 1
            eigenvalues (np.array): nkpts * nbands
        """
        self.kpoints, self.eigenvalues = self.unique(kpoints, eigenvalues)
        self.efermi = efermi

    def unique(self, kpoints, eigenvalues):
        """
        Erase repeated kpoints in the band structure.
        """
        nkpts, nbands = np.shape(eigenvalues)
        flag = [True]
        for i in range(1, nkpts):
            if math.isclose(kpoints[i], kpoints[i - 1]):
                flag.append(False)
            else:
                flag.append(True)

        return kpoints[flag], eigenvalues[flag, :]

    def is_metal(self):
        """
        Check if the band structure indicates a metal 
        by looking if the fermi level crosses a band.
        Args:
            efermi (float): fermi level
        Returns:
            True if a metal, False if not
        """
        nkpts, nbands = np.shape(self.eigenvalues)
        for i in range(nbands):
            e_min = min(self.eigenvalues[:, i])
            e_max = max(self.eigenvalues[:, i])
            if e_min < self.efermi < e_max:
                return True
        return False

    def get_vbm(self):
        """
        Get the valence band maximum.
        Returns:
            (kpoint_idx, band_idx, energy)
        """
        if self.is_metal():
            raise ValueError("The object is metal.")

        max_energies = np.amax(self.eigenvalues, axis = 0)
        band_idx = np.argmax(max_energies[max_energies < self.efermi])
        kpoint_idx = np.argmax(self.eigenvalues[:, band_idx])
        energy = self.eigenvalues[kpoint_idx, band_idx]

        return (kpoint_idx, band_idx, energy)

    def get_cbm(self):
        """
        Get the conduction band minimum.
        Returns:
            (kpoint_idx, band_idx, energy)
        """
        if self.is_metal():
            raise ValueError("The object is metal.")

        min_energies = np.amin(self.eigenvalues, axis = 0)

        head = len(min_energies[min_energies < self.efermi])
        band_idx = np.argmin(min_energies[min_energies > self.efermi])
        band_idx += head

        kpoint_idx = np.argmin(self.eigenvalues[:, band_idx])
        energy = self.eigenvalues[kpoint_idx, band_idx]

        return (kpoint_idx, band_idx, energy)

    def get_band_gap(self):
        """
        Get the band gap.
        Returns:
            {"energy": band gap energy, 
            "direct": a boolean value tells if the gap is direct or indirect, 
            "from": kpoint_idx and band_idx of vbm,
            "to": kpoint_idx and band_idx of cbm}
        """
        if self.is_metal():
            return {"energy": 0}

        else:
            k_vbm, band_vbm, e_vbm = self.get_vbm()
            k_cbm, band_cbm, e_cbm = self.get_cbm()
            return {"energy": e_cbm - e_vbm,
                    "direct": k_vbm == k_cbm,
                    "from": (k_vbm, band_vbm),
                    "to": (k_cbm, band_cbm)}

    def get_elec_eff_mass(self, N = 1):
        """
        Get electron effective mass at cbm.
        Args:
            N (int): number of kpoints for parabolic fitting
        Return:
            mass (float): unit: m0
        """
        kpoint_idx, band_idx, energy = self.get_cbm()

        X = self.kpoints[kpoint_idx - N: kpoint_idx + N + 1]
        Y = self.eigenvalues[kpoint_idx - N: kpoint_idx + N + 1, band_idx]
        p = np.polyfit(X, Y, deg = 2)

        h_bar = 6.582119E-16;  # reduced planck constant in eV * s
        eV_J = constants.eV; # electron volt in Jouel
        m_e = constants.m_e; # electron mass in Kg
        mass = h_bar**2 / (p[0] * 2) * eV_J / 1.0E-20 / m_e * (2*np.pi)**2;
        
        return mass

    def get_hole_eff_mass(self, N = 1):
        """
        Get hole effective mass at vbm.
        Args:
            N (int): number of kpoints for parabolic fitting
        Return:
            mass (float): unit: m0
        """
        kpoint_idx, band_idx, energy = self.get_vbm()

        X = self.kpoints[kpoint_idx - N : kpoint_idx + N + 1]
        Y = self.eigenvalues[kpoint_idx - N: kpoint_idx + N + 1, band_idx]
        p = np.polyfit(X, Y, deg = 2)

        h_bar = constants.physical_constants['Planck constant in eV s'][0] / (2 * np.pi);  # reduced planck constant in eV * s
        eV_J = constants.eV; # electron volt in Jouel
        m_e = constants.m_e; # electron mass in Kg
        mass = h_bar**2 / (p[0] * 2) * eV_J / 1.0E-20 / m_e * (2*np.pi)**2;
        
        return mass


        










