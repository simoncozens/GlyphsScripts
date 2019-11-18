#MenuTitle: Reset Anchors
# -*- coding: utf-8 -*-
__doc__="""
Delete all anchors and add them again
"""

Glyphs.font.selectedLayers[0].parent.beginUndo()
for layer in Glyphs.font.selectedLayers[0].parent.layers:
  layer.anchors = []
  layer.addMissingAnchors()
Glyphs.font.selectedLayers[0].end.beginUndo()