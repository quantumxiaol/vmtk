from __future__ import absolute_import

import os
import sys


def _prefer_system_vtk_python():
    vtk_python_path = os.environ.get("VMTK_PYTHON_VTK_PATH", "")
    if vtk_python_path:
        if os.path.isfile(os.path.join(vtk_python_path, "vtk.py")) and vtk_python_path not in sys.path:
            sys.path.insert(0, vtk_python_path)
        return

    if sys.platform != "darwin":
        return

    pyver = "python{0}.{1}".format(sys.version_info.major, sys.version_info.minor)
    for prefix in ("/opt/homebrew", "/usr/local"):
        candidate = os.path.join(prefix, "lib", pyver, "site-packages")
        if os.path.isfile(os.path.join(candidate, "vtk.py")) and candidate not in sys.path:
            sys.path.insert(0, candidate)
            return


_prefer_system_vtk_python()
