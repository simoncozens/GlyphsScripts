#MenuTitle: Determine Optical Center
# -*- coding: utf-8 -*-
__doc__ = """
Reports the optical center of the current layer. If there is a 'top' anchor, aligns it on the horizontal optical center
"""
import glyphmonkey
layer = Glyphs.font.selectedLayers[0]

i = layer.horizontalOpticalCenter()
print("Horizontal optical center:", i)
if layer.anchors['top']:
  layer.anchors['top'].position = [i, layer.anchors['top'].position.y]
