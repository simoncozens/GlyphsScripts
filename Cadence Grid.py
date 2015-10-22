#MenuTitle: Cadence grid
# -*- coding: utf-8 -*-
__doc__="""
Add regular guidelines according to LeMo cadencing method.
"""

import vanilla
windowHeight = 70

class CadenceGrid( object ):
  def __init__( self ):
    try:
      self.w = vanilla.FloatingWindow( (200, windowHeight), "Cadence grid")
      self.w.text_anchor = vanilla.TextBox( (15, 12, 130, 17), "Stem width", sizeStyle='small')
      self.w.stemWidth = vanilla.EditText( (100, 10, 50, 20), "70", sizeStyle = 'small')
      self.w.go = vanilla.Button((-80, -32, -15, 17), "Cadence", sizeStyle='small', callback=self.addGrid)
      self.w.setDefaultButton( self.w.go )
      self.w.open()
    except Exception, e:
      print(e)

  def addGrid(self,sender):
    try:
      stem = self.w.stemWidth.get()
      cadence = float(stem) / 5 # Assuming I understand LeMo correctly...
      self.w.close()
      Font = Glyphs.font
      FontMaster = Font.selectedFontMaster
      x = 0
      while FontMaster.guides:
        del(FontMaster.guides[0])

      while x < 1000:
        g = GSGuideLine()
        g.position = NSPoint(x,0)
        g.angle = 90.0
        FontMaster.guides.append(g)
        x = x + cadence

    except Exception, e:
      print(e)

CadenceGrid()