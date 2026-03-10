## Program: VMTK
## Language: Python

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path):
    return (REPO_ROOT / path).read_text()


def test_dependency_minimized_defaults_are_set():
    root_cmake = _read('CMakeLists.txt')

    assert 'set(VMTK_ENABLE_SEGMENTATION OFF CACHE BOOL' in root_cmake
    assert 'set(VMTK_USE_RENDERING OFF CACHE BOOL' in root_cmake
    assert 'set(VMTK_BUILD_TETGEN OFF CACHE BOOL' in root_cmake
    assert 'option ( VMTK_CONTRIB_SCRIPTS "Install modules from the vmtkScripts/contrib directory." OFF )' in root_cmake
    assert 'option ( VTK_VMTK_CONTRIB "Build and install classes in the vtkVmtk/Contrib directory." OFF )' in root_cmake


def test_itk_is_not_required_when_segmentation_is_disabled():
    root_cmake = _read('CMakeLists.txt')
    options_cmake = _read('CMake/CMakeOptions.cmake')

    assert 'VMTK_ENABLE_SEGMENTATION AND NOT ITK_FOUND' in root_cmake
    assert 'VMTK_ENABLE_SEGMENTATION AND NOT ITK_FOUND' in options_cmake


def test_vtkvmtk_subdirectories_follow_feature_gates():
    vtkvmtk_cmake = _read('vtkVmtk/CMakeLists.txt')
    utilities_cmake = _read('vtkVmtk/Utilities/CMakeLists.txt')

    assert 'if (VMTK_ENABLE_SEGMENTATION)' in vtkvmtk_cmake
    assert 'list(APPEND dirs Segmentation)' in vtkvmtk_cmake
    assert 'if (VMTK_ENABLE_SEGMENTATION)' in utilities_cmake
    assert 'add_subdirectory(vtkvmtkITK)' in utilities_cmake


def test_superbuild_does_not_require_itk_unless_segmentation_is_enabled():
    superbuild_cmake = _read('SuperBuild.cmake')

    assert 'if( VMTK_ENABLE_SEGMENTATION AND NOT USE_SYSTEM_ITK )' in superbuild_cmake
    assert 'if (VMTK_ENABLE_SEGMENTATION)' in superbuild_cmake
    assert '${VMTK_OPTIONAL_EXTERNALPROJECT_ARGS}' in superbuild_cmake


def test_tetgen_build_path_is_fully_gated():
    root_cmake = _read('CMakeLists.txt')
    vtkvmtk_cmake = _read('vtkVmtk/CMakeLists.txt')
    utilities_cmake = _read('vtkVmtk/Utilities/CMakeLists.txt')
    misc_cmake = _read('vtkVmtk/Misc/CMakeLists.txt')

    assert 'option ( VMTK_BUILD_TETGEN "Build TetGen and TetGen wrapper. Check TetGen license before you activate this." OFF )' in root_cmake
    assert 'option(VTK_VMTK_BUILD_TETGEN "Build TetGen and TetGen wrapper. Check TetGen license before you activate this." OFF)' in vtkvmtk_cmake
    assert 'if (VMTK_BUILD_TETGEN AND VTK_VMTK_BUILD_TETGEN)' in utilities_cmake
    assert 'if (VMTK_BUILD_TETGEN AND VTK_VMTK_BUILD_TETGEN)' in misc_cmake


def test_io_dicom_include_is_guarded_without_itk():
    io_cmake = _read('vtkVmtk/IO/CMakeLists.txt')
    assert 'if(DEFINED vtkDICOMParser_INCLUDE_DIRS AND vtkDICOMParser_INCLUDE_DIRS)' in io_cmake
