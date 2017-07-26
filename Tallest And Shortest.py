#MenuTitle: Tallest and Shortest
# -*- coding: utf-8 -*-
__doc__="""
Open a tab with glyphs with the highest ascender and lowest descender
"""
from PyObjCTools.AppHelper import callAfter
import GlyphsApp

tallest = ""
lowest = ""
minBottom = 9999
maxTop = -9999
for glyph in Glyphs.font.glyphs:
  layer = glyph.layers[font.selectedFontMaster.id]
  top = layer.bounds.origin.y + layer.bounds.size.height
  bottom = layer.bounds.origin.y
  if bottom < minBottom:
    lowest = "/"+glyph.name
    minBottom = bottom
  if top > maxTop:
    maxTop = top
    tallest = "/"+glyph.name

callAfter(Glyphs.currentDocument.windowController().addTabWithString_, tallest + lowest)