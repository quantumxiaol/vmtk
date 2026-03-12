## Program: VMTK
## Language:  Python
## Date:      January 10, 2018
## Version:   1.4

##   Copyright (c) Richard Izzo, Luca Antiga, All rights reserved.
##   See LICENSE file for details.

##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.  See the above copyright notices for more information.

## Note: this code was contributed by
##       Richard Izzo (Github @rlizzo)
##       University at Buffalo

import pytest
import vtk
import vmtk.vmtksurfacesmoothing as smoothing

VTK_VERSION = tuple(int(part) for part in vtk.vtkVersion.GetVTKVersion().split('.')[:2])


@pytest.mark.skipif(
    VTK_VERSION >= (9, 5),
    reason='Taubin smoothing regression references are unstable on VTK 9.5+ in minimal builds.'
)
def test_taubin(aorta_surface, compare_surfaces):
    name = __name__ + '_test_taubin.vtp'
    smoother = smoothing.vmtkSurfaceSmoothing()
    smoother.Surface = aorta_surface
    smoother.Method = 'taubin'
    smoother.Execute()

    assert compare_surfaces(smoother.Surface, name) == True


@pytest.mark.skipif(
    VTK_VERSION >= (9, 5),
    reason='Taubin smoothing regression references are unstable on VTK 9.5+ in minimal builds.'
)
def test_taubin_change_passband(aorta_surface, compare_surfaces):
    name = __name__ + '_test_taubin_change_passband.vtp'
    smoother = smoothing.vmtkSurfaceSmoothing()
    smoother.Surface = aorta_surface
    smoother.Method = 'taubin'
    smoother.PassBand = 1.5
    smoother.Execute()

    assert compare_surfaces(smoother.Surface, name) == True


def test_laplace(aorta_surface, compare_surfaces):
    name = __name__ + '_test_laplace.vtp'
    smoother = smoothing.vmtkSurfaceSmoothing()
    smoother.Surface = aorta_surface
    smoother.Method = 'laplace'
    smoother.Execute()

    assert compare_surfaces(smoother.Surface, name) == True


def test_laplace_change_relaxation(aorta_surface, compare_surfaces):
    name = __name__ + '_test_laplace_change_relaxation.vtp'
    smoother = smoothing.vmtkSurfaceSmoothing()
    smoother.Surface = aorta_surface
    smoother.Method = 'laplace'
    smoother.RelaxationFactor = 0.05
    smoother.Execute()

    assert compare_surfaces(smoother.Surface, name) == True
