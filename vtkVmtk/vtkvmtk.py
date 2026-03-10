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


def _load_vtk_runtime():
  vendored_vtk_dir = os.path.join(os.path.dirname(__file__), ".vtk")
  vendored_vtk_py = os.path.join(vendored_vtk_dir, "vtk.py")
  flag = os.environ.get("VMTK_IMPORT_SYSTEM_VTK", "").strip().lower()
  use_system = flag in ("1", "true", "yes", "on")

  if not use_system and os.path.isfile(vendored_vtk_py):
    if vendored_vtk_dir not in sys.path:
      sys.path.insert(0, vendored_vtk_dir)
    existing_vtk = sys.modules.get("vtk")
    if existing_vtk is not None:
      existing_file = os.path.realpath(getattr(existing_vtk, "__file__", ""))
      vendored_prefix = os.path.realpath(vendored_vtk_dir) + os.sep
      if existing_file and not existing_file.startswith(vendored_prefix):
        raise ImportError(
          "External vtk is already loaded; start a fresh process and import vmtk first, "
          "or set VMTK_IMPORT_SYSTEM_VTK=1 explicitly."
        )
    import vtk  # noqa: F401
    loaded_file = os.path.realpath(getattr(vtk, "__file__", ""))
    vendored_prefix = os.path.realpath(vendored_vtk_dir) + os.sep
    if loaded_file and not loaded_file.startswith(vendored_prefix):
      raise ImportError(
        "Failed to load vendored vtk runtime; loaded external vtk instead. "
        "Set VMTK_IMPORT_SYSTEM_VTK=1 only if you intentionally want system vtk."
      )
    return

  _prefer_system_vtk_python()
  import vtk  # noqa: F401


_load_vtk_runtime()

from .vtkvmtkCommonPython import *
from .vtkvmtkComputationalGeometryPython import *
from .vtkvmtkDifferentialGeometryPython import *
from .vtkvmtkIOPython import *
from .vtkvmtkMiscPython import *

_import_optional(".vtkvmtkRenderingPython")
_import_optional(".vtkvmtkSegmentationPython")
_import_optional(".vtkvmtkITKPython")
_import_optional(".vtkvmtkContribPython")
