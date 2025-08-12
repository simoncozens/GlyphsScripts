# MenuTitle: SuperAligner
# -*- coding: utf-8 -*-

def align_path(reference, target_path):
    # Try to align the paths by type
    test = [n.type for n in target_path.nodes]
    if reference == test:
        return True
    shifts = 0
    while shifts < len(test) and reference != test:
        test = test[-1:] + test[:-1]
        shifts += 1
        if reference == test:
            target_path.nodes = target_path.nodes[-shifts:] + target_path.nodes[:-shifts]
            return True
    return False


layers = [ l for l in Glyphs.font.selectedLayers[0].parent.layers if l.associatedMasterId == l.layerId ]
for path_index in range(len(layers[0].paths)):
    reference = [n.type for n in layers[0].paths[path_index].nodes]
    for target_layer in layers[1:]:
        target_path = target_layer.paths[path_index]
        if len(target_path.nodes) != len(reference):
            print('Different number of nodes in path %d' % path_index)
            continue
        if not align_path(reference, target_path):
            print('Could not align path %d, reversing' % path_index)
            target_path.reverse()
            if not align_path(reference, target_path):
                print('Could not align path %d' % path_index)
                continue
