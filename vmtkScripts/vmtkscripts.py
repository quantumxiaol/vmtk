from __future__ import absolute_import #NEEDS TO STAY AS TOP LEVEL MODULE FOR Py2-3 COMPATIBILITY
import importlib

__all__ = [
    'vmtk.vmtkactivetubes',
    'vmtk.vmtkbifurcationprofiles',
    'vmtk.vmtkbifurcationreferencesystems',
    'vmtk.vmtkbifurcationsections',
    'vmtk.vmtkbifurcationvectors',
    'vmtk.vmtkboundarylayer',
    'vmtk.vmtkboundaryreferencesystems',
    'vmtk.vmtkbranchclipper',
    'vmtk.vmtkbranchextractor',
    'vmtk.vmtkbranchgeometry',
    'vmtk.vmtkcenterlineimage',
    'vmtk.vmtkbranchmapping',
    'vmtk.vmtkbranchmetrics',
    'vmtk.vmtkbranchpatching',
    'vmtk.vmtkbranchsections',
    'vmtk.vmtkcenterlineattributes',
    'vmtk.vmtkcenterlinegeometry',
    'vmtk.vmtkcenterlineinterpolation',
    'vmtk.vmtkcenterlinelabeler',
    'vmtk.vmtkcenterlinemerge',
    'vmtk.vmtkcenterlinemodeller',
    'vmtk.vmtkcenterlineoffsetattributes',
    'vmtk.vmtkcenterlineresampling',
    'vmtk.vmtkcenterlines',
    'vmtk.vmtkcenterlinestonumpy',
    'vmtk.vmtkcenterlinesections',
    'vmtk.vmtkcenterlinesmoothing',
    'vmtk.vmtkcenterlinesnetwork',
    'vmtk.vmtkcenterlineviewer',
    'vmtk.vmtkdelaunayvoronoi',
    'vmtk.vmtkdistancetocenterlines',
    'vmtk.vmtkendpointextractor',
    'vmtk.vmtkflowextensions',
    'vmtk.vmtkicpregistration',
    'vmtk.vmtkimagebinarize',
    'vmtk.vmtkimagecast',
    'vmtk.vmtkimagecompose',
    'vmtk.vmtkimagecurvedmpr',
    'vmtk.vmtkimagefeaturecorrection',
    'vmtk.vmtkimagefeatures',
    'vmtk.vmtkimageinitialization',
    'vmtk.vmtkimagemipviewer',
    'vmtk.vmtkimagemorphology',
    'vmtk.vmtkimagenormalize',
    'vmtk.vmtkimageobjectenhancement',
    'vmtk.vmtkimageotsuthresholds',
    'vmtk.vmtkimagereader',
    'vmtk.vmtkimagereslice',
    'vmtk.vmtkimageseeder',
    'vmtk.vmtkimageshiftscale',
    'vmtk.vmtkimagesmoothing',
    'vmtk.vmtkimagetonumpy',
    'vmtk.vmtkimageviewer',
    'vmtk.vmtkimagevesselenhancement',
    'vmtk.vmtkimagevoipainter',
    'vmtk.vmtkimagevoiselector',
    'vmtk.vmtkimagevolumeviewer',
    'vmtk.vmtkimagewriter',
    'vmtk.vmtklevelsetsegmentation',
    'vmtk.vmtklineartoquadratic',
    'vmtk.vmtklineresampling',
    'vmtk.vmtklocalgeometry',
    'vmtk.vmtkmarchingcubes',
    'vmtk.vmtkmesharrayoperation',
    'vmtk.vmtkmeshboundaryinspector',
    'vmtk.vmtkmeshbranchclipper',
    'vmtk.vmtkmeshclipper',
    'vmtk.vmtkmeshconnectivity',
    'vmtk.vmtkmeshcutter',
    'vmtk.vmtkmeshdatareader',
    'vmtk.vmtkmeshextractpointdata',
    'vmtk.vmtkmeshlambda2',
    'vmtk.vmtkmeshlinearize',
    'vmtk.vmtkmeshgenerator',
    'vmtk.vmtkmeshmergetimesteps',
    'vmtk.vmtkmeshpolyballevaluation',
    'vmtk.vmtkmeshprojection',
    'vmtk.vmtkmeshreader',
    'vmtk.vmtkmeshscaling',
    'vmtk.vmtkmeshtetrahedralize',
    'vmtk.vmtkmeshtonumpy',
    'vmtk.vmtkmeshtosurface',
    'vmtk.vmtkmeshtransform',
    'vmtk.vmtkmeshtransformtoras',
    'vmtk.vmtkmeshvectorfromcomponents',
    'vmtk.vmtkmeshviewer',
    'vmtk.vmtkmeshvolume',
    'vmtk.vmtkmeshvorticityhelicity',
    'vmtk.vmtkmeshwallshearrate',
    'vmtk.vmtkmeshwriter',
    'vmtk.vmtknetworkeditor',
    'vmtk.vmtknetworkextraction',
    'vmtk.vmtknetworkwriter',
    'vmtk.vmtknumpyreader',
    'vmtk.vmtknumpytocenterlines',
    'vmtk.vmtknumpytoimage',
    'vmtk.vmtknumpytomesh',
    'vmtk.vmtknumpytosurface',
    'vmtk.vmtknumpywriter',
    'vmtk.vmtkparticletracer',
    'vmtk.vmtkpathlineanimator',
    'vmtk.vmtkpointsplitextractor',
    'vmtk.vmtkpointtransform',
    'vmtk.vmtkpolyballmodeller',
    'vmtk.vmtkpotentialfit',
    'vmtk.vmtkpythonscript',
    'vmtk.vmtkrenderer',
    'vmtk.vmtkrendertoimage',
    'vmtk.vmtkrbfinterpolation',
    'vmtk.vmtksurfaceappend',
    'vmtk.vmtksurfacearraysmoothing',
    'vmtk.vmtksurfacearrayoperation',
    'vmtk.vmtksurfacebooleanoperation',
    'vmtk.vmtksurfacecapper',
    'vmtk.vmtksurfacecelldatatopointdata',
    'vmtk.vmtksurfacecenterlineprojection',
    'vmtk.vmtksurfaceclipper',
    'vmtk.vmtksurfacecliploop',
    'vmtk.vmtksurfaceconnectivity',
    'vmtk.vmtksurfaceconnectivityselector',
    'vmtk.vmtksurfacecurvature',
    'vmtk.vmtksurfacedecimation',
    'vmtk.vmtksurfacedistance',
    'vmtk.vmtksurfaceendclipper',
    'vmtk.vmtksurfacekiteremoval',
    'vmtk.vmtksurfaceloopextraction',
    'vmtk.vmtksurfacemassproperties',
    'vmtk.vmtksurfacemodeller',
    'vmtk.vmtksurfacenormals',
    'vmtk.vmtksurfacepointdatatocelldata',
    'vmtk.vmtksurfacepolyballevaluation',
    'vmtk.vmtksurfaceprojection',
    'vmtk.vmtksurfacereader',
    'vmtk.vmtksurfacereferencesystemtransform',
    'vmtk.vmtksurfaceregiondrawing',
    'vmtk.vmtksurfaceremeshing',
    'vmtk.vmtksurfacescaling',
    'vmtk.vmtksurfacesmoothing',
    'vmtk.vmtksurfacesubdivision',
    'vmtk.vmtksurfacetobinaryimage',
    'vmtk.vmtksurfacetonumpy',
    'vmtk.vmtksurfacetransform',
    'vmtk.vmtksurfacetransforminteractive',
    'vmtk.vmtksurfacetransformtoras',
    'vmtk.vmtksurfacetriangle',
    'vmtk.vmtksurfacetomesh',
    'vmtk.vmtksurfaceviewer',
    'vmtk.vmtksurfacewriter',
    'vmtk.vmtksurfmesh',
    'vmtk.vmtktetgen',
    'vmtk.vmtktetringenerator'
    ]

_loaded_modules = {}
_failed_modules = {}


def _module_short_name(module_name):
    return module_name.rsplit('.', 1)[-1]


def _load_module(module_name):
    if module_name in _loaded_modules:
        return _loaded_modules[module_name]
    if module_name in _failed_modules:
        raise _failed_modules[module_name]

    module = importlib.import_module(module_name)
    _loaded_modules[module_name] = module
    globals()[_module_short_name(module_name)] = module
    return module


def _iter_script_modules():
    for module_name in __all__:
        yield module_name


def __getattr__(name):
    for module_name in _iter_script_modules():
        if _module_short_name(module_name) == name:
            try:
                return _load_module(module_name)
            except Exception as exc:
                _failed_modules[module_name] = exc
                raise

    for module_name in _iter_script_modules():
        if module_name in _failed_modules:
            continue
        try:
            module = _load_module(module_name)
        except Exception as exc:
            _failed_modules[module_name] = exc
            continue
        if hasattr(module, name):
            value = getattr(module, name)
            globals()[name] = value
            return value

    raise AttributeError("module '%s' has no attribute '%s'" % (__name__, name))


def __dir__():
    module_names = [_module_short_name(module_name) for module_name in __all__]
    return sorted(set(list(globals().keys()) + module_names))
