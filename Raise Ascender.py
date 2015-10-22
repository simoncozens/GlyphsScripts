#MenuTitle: Raise ascender
# -*- coding: utf-8 -*-
__doc__="""
Raise points above the X-height by the given amount
"""

import vanilla
windowHeight = 100

Font = Glyphs.font

class RaiseAscender( object ):
  def __init__( self ):
    try:
      self.w = vanilla.FloatingWindow( (200, windowHeight), "Raise ascender")
      self.w.text_anchor = vanilla.TextBox( (15, 12, 130, 17), "Amount", sizeStyle='small')
      self.w.amount = vanilla.EditText( (100, 10, 50, 20), "10", sizeStyle = 'small')
      self.w.goThis = vanilla.Button((10, 15, 150, 57), "Raise this master", sizeStyle='small', callback=self.goThis)
      self.w.goAll = vanilla.Button((10, 50, 150, 57), "Raise all masters", sizeStyle='small', callback=self.goAll)
      self.w.setDefaultButton( self.w.goThis )
      self.w.open()
    except Exception, e:
      print(e)

  def goAll(self,sender):
    try:
      for thisLayer in Font.selectedLayers[0].parent.layers:
        thisLayer.setDisableUpdates()
        thisGlyph = thisLayer.parent
        self.raiseGlyph(thisGlyph, thisLayer)
        thisLayer.setEnableUpdates()
    except Exception, e:
      print(e)

  def goThis(self, sender):
    try:
      for thisLayer in Font.selectedLayers:
        thisLayer.setDisableUpdates()
        thisGlyph = thisLayer.parent
        self.raiseGlyph(thisGlyph,thisLayer)
        thisLayer.setEnableUpdates()
    except Exception, e:
      print(e)

  def raiseGlyph(self, thisGlyph, thisLayer):
    try:
      raiseAmount = float(self.w.amount.get())
      thisGlyph.beginUndo()
      for thisPath in thisLayer.paths:
          for thisNode in thisPath.nodes:
            if thisNode.y > (Font.masters[thisLayer.associatedMasterId].xHeight + 10):
              thisNode.y += raiseAmount
      thisGlyph.endUndo()

    except Exception, e:
      print(e)

RaiseAscender()