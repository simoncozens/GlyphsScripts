#MenuTitle: Delete Close Points
# -*- coding: utf-8 -*-
__doc__="""
Delete points which are very close to (or on top of) other points
"""
from glyphmonkey import *

arbitraryConstant = 5

for p in Glyphs.font.selectedLayers[0].paths:
  p.segments = [ seg for seg in p.segments if seg.length > arbitraryConstant ]

Glyphs.redraw()
