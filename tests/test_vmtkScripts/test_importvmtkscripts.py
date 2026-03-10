## Program: VMTK
## Language:  Python

import importlib


def test_import_vmtk_scripts_registry():
    registry = importlib.import_module('vmtk.vmtkscripts')

    assert isinstance(registry.__all__, list)
    assert 'vmtk.vmtkcenterlines' in registry.__all__
    assert 'vmtk.vmtknetworkextraction' in registry.__all__
    # Keep disabled-dependency script names discoverable in the registry.
    assert 'vmtk.vmtklevelsetsegmentation' in registry.__all__
    assert 'vmtk.vmtkrenderer' in registry.__all__


def test_vmtk_scripts_registry_loads_script_module_lazily():
    registry = importlib.import_module('vmtk.vmtkscripts')

    centerlines_module = registry.vmtkcenterlines
    assert centerlines_module.__name__ == 'vmtk.vmtkcenterlines'
