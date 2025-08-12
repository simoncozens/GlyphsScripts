#MenuTitle: Copy Anchor Context To All Masters
# -*- coding: utf-8 -*-
l = Glyphs.font.selectedLayers[0]
for a in l.anchors:
  context = a.userData["GPOS_Context"]
  print(a.name, context)
  for other_layer in l.parent.layers:
    other_layer.anchors[a.name].userData["GPOS_Context"] = context
    print(" ", other_layer.anchors[a.name].userData)
