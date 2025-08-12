#MenuTitle: Remove Extraneous Mark Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Remove anchors from marks which don't belong
"""

def process(thisGlyph):
  for thisLayer in thisGlyph.layers:
    if thisLayer.anchors["_top"]:
      del thisLayer.anchors["bottom"]
    if thisLayer.anchors["_bottom"]:
      del thisLayer.anchors["top"]

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears log in Macro window

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
  for thisLayer in selectedLayers:
    thisGlyph = thisLayer.parent
    print("🔠 %s" % thisGlyph.name)
    thisGlyph.beginUndo() # begin undo grouping
    process(thisGlyph)
    thisGlyph.endUndo() # end undo grouping
except Exception as e:
  Glyphs.showMacroWindow()
  print("\n⚠️ Error in script: Shine Through Anchors\n")
  import traceback
  print(traceback.format_exc())
  print()
  raise e
finally:
  thisFont.enableUpdateInterface() # re-enables UI updates in Font View
