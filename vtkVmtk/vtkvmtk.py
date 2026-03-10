#!/usr/bin/env python
""" This module loads all the classes from the vtkVmtk library into its
namespace.  This is a required module."""

from __future__ import absolute_import  # NEEDS TO STAY AS TOP LEVEL MODULE FOR Py2-3 COMPATIBILITY
import importlib
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


def _import_optional(module_name):
  try:
    module = importlib.import_module(module_name, package=__name__)
  except ModuleNotFoundError:
    return
  for symbol_name in dir(module):
    if symbol_name.startswith("_"):
      continue
    globals()[symbol_name] = getattr(module, symbol_name)

_prefer_system_vtk_python()
import vtk

from .vtkvmtkCommonPython import *
from .vtkvmtkComputationalGeometryPython import *
from .vtkvmtkDifferentialGeometryPython import *
from .vtkvmtkIOPython import *
from .vtkvmtkMiscPython import *

_import_optional(".vtkvmtkRenderingPython")
_import_optional(".vtkvmtkSegmentationPython")
_import_optional(".vtkvmtkITKPython")
_import_optional(".vtkvmtkContribPython")
