#MenuTitle: Rename to Glyphs Default Names
# -*- coding: utf-8 -*-
__doc__="""
Makes the names equal to what you would get when you add them in Glyphs
"""

mapping = {
  "Euro": "euro",
  "arrowup": "upArrow",
  "arrowright": "rightArrow",
  "arrowdown": "downArrow" ,
  "arrowleft":"leftArrow",
  "arrowboth": "leftRightArrow",
  "arrowupdn": "upDownArrow",
  "uni01DD": "schwa",
  "uni0294": "glottalstop",
  "dotlessi": "idotless",
  "uni019B": "lambdastroke",
  "uni026B": "lmiddletilde",
  "uni00B9": "onesuperior",
  "uni00B2": "twosuperior",
  "uni00B3": "threesuperior",
   "guillemotleft": "guillemetleft",
   "guillemotright": "guillemetright",
   "uni0308": "dieresiscomb",
   "uni0307": "dotaccentcomb",
    "uni030B": "hungarumlautcomb",
    "uni0302": "circumflexcomb",
    "uni030C": "caroncomb",
    "uni0306": "brevecomb",
    "uni030A": "ringcomb",
    "uni0304": "macroncomb",
    "uni0312": "commaturnedabovecomb",
    "uni0313": "commaabovecomb",
    "uni0315": "commaaboverightcomb",
    "uni0326": "commaaccentcomb",
    "uni0327": "cedillacomb",
    "uni0328": "ogonekcomb",
    "uni0335": "strokeshortcomb",
    "uni0336": "strokelongcomb",
    "uni0337": "slashshortcomb",
    "uni0338": "slashlongcomb",
    "uni02BC": "apostrophemod",


}

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

def renameGlyph( thisGlyph ):
  oldName = thisGlyph.name
  if oldName in mapping:
    newName = mapping[oldName]
    thisGlyph.name = newName
    print "%s --> %s" % (oldName, newName)

Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
  renameGlyph( thisGlyph )

Font.enableUpdateInterface()
