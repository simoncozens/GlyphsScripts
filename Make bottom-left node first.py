#MenuTitle: Make bottom left node first
# -*- coding: utf-8 -*-
__doc__="""
Makes the bottom left node in each path the first node in all masters
"""

def left(x):
  return  x.position.x
def bottom(x):
  return  x.position.y


layers = Glyphs.font.selectedLayers
for aLayer in layers:
  for idx, thisLayer in enumerate(aLayer.parent.layers):
    for p in thisLayer.paths:
      n = sorted(sorted(list(p.nodes), key = bottom),key=left)[0]
      n.makeNodeFirst()