## Program: VMTK
## Language:  Python

import vmtk.vmtknetworkextraction as vmtknetworkextraction


def test_network_extraction_outputs_network_and_graphlayout(aorta_surface_openends):
    extractor = vmtknetworkextraction.vmtkNetworkExtraction()
    extractor.Surface = aorta_surface_openends
    extractor.Execute()

    assert extractor.Network is not None
    assert extractor.GraphLayout is not None
    assert extractor.Network.GetNumberOfPoints() > 0
    assert extractor.Network.GetNumberOfCells() > 0

    radius_array = extractor.Network.GetPointData().GetArray(extractor.RadiusArrayName)
    topology_array = extractor.Network.GetCellData().GetArray(extractor.TopologyArrayName)
    graph_radius_array = extractor.GraphLayout.GetCellData().GetArray(extractor.RadiusArrayName)

    assert radius_array is not None
    assert topology_array is not None
    assert graph_radius_array is not None
