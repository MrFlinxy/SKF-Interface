"""
from : https://mattermodeling.stackexchange.com/a/10607
"""
from openbabel import pybel as pb
import sys


def smi_xyz(smiles, folder_name, jsme_nama):
    mol = pb.readstring("smiles", smiles)

    mol.make3D()

    ff = pb._forcefields["mmff94"]
    success = ff.Setup(mol.OBMol)
    if not success:
        ff = pb._forcefields["uff"]
        success = ff.Setup(mol.OBMol)
        if not success:
            sys.exit("Cannot set up forcefield")

    ff.ConjugateGradients(100, 1.0e-3)
    ff.FastRotorSearch(True)
    ff.WeightedRotorSearch(100, 25)
    ff.ConjugateGradients(250, 1.0e-4)
    ff.GetCoordinates(mol.OBMol)

    mol.write(
        "xyz",
        f"user_data/{folder_name}/{jsme_nama}/{jsme_nama}_smi.xyz",
        overwrite=True,
    )
