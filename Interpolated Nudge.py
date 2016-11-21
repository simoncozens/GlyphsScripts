#MenuTitle: Interpolated nudge
# -*- coding: utf-8 -*-
__doc__="""
Nudge points while keeping tension
"""

import vanilla
windowHeight = 100
windowWidth = 120

class InterpolatedNudgeWindow( object ):
  def __init__( self ):
    try:
      self.w = vanilla.FloatingWindow( (windowWidth, windowHeight), "Interpolated Nudge")
      self.w.text_anchor = vanilla.TextBox( (15, 12, 130, 17), "Amount", sizeStyle='small')
      self.w.amount = vanilla.EditText( (65, 9, 50, 20), "10", sizeStyle = 'small')
      self.w.up = vanilla.Button(((windowWidth-20)/2, 20, 30, 40), "^", sizeStyle='small', callback=self.up)
      self.w.down = vanilla.Button(((windowWidth-20)/2, (windowHeight-40), 30, 40), "v", sizeStyle='small', callback=self.down)
      self.w.left = vanilla.Button((10, (windowHeight-20)/2, 30, 40), "<", sizeStyle='small', callback=self.left)
      self.w.right = vanilla.Button((-30, (windowHeight-20)/2, 30, 40), ">", sizeStyle='small', callback=self.right)
      self.w.open()
      self.w.amount.selectAll()
    except Exception, e:
      print(e)

  def nextOnCurve(self, n):
    n = n.nextNode
    while n.type == OFFCURVE: n = n.nextNode
    return n

  def prevOnCurve(self, n):
    n = n.prevNode
    while n.type == OFFCURVE: n = n.prevNode
    return n

  def adjust(self, handle, node, diffX, diffY, dx, dy):
    adjX, adjY = 0, 0
    if diffX != 0:
      adjX = ((node.position.x-handle.position.x)/diffX) * dx
    if diffY != 0:
      adjY = ((node.position.y-handle.position.y)/diffY) * dy

    handle.position = (handle.position.x + adjX, handle.position.y + adjY)

  def nudge(self, n, deltax, deltay):
    nn = self.nextOnCurve(n)
    pn = self.prevOnCurve(n)

    if nn.type == CURVE:
      diffX, diffY = nn.position.x - n.position.x, nn.position.y - n.position.y
      self.adjust(nn.prevNode, nn, diffX, diffY, deltax, deltay)
      self.adjust(nn.nextNode, nn, diffX, diffY, deltax, deltay)

    if pn.type == CURVE:
      diffX, diffY = pn.position.x - n.position.x, pn.position.y - n.position.y
      self.adjust(pn.prevNode, pn, diffX, diffY, deltax, deltay)
      self.adjust(pn.nextNode, pn, diffX, diffY, deltax, deltay)

    n.position = (n.position.x + deltax, n.position.y + deltay)
    n.prevNode.position = (n.prevNode.position.x + deltax, n.prevNode.position.y + deltay)
    n.nextNode.position = (n.nextNode.position.x + deltax, n.nextNode.position.y + deltay)

  def up(self,sender):
    try:
      val = float(self.w.amount.get())
      self.doIt(0,val)
    except Exception, e:
      print(e)

  def down(self,sender):
    val = float(self.w.amount.get())
    self.doIt(0,-val)

  def left(self,sender):
    val = float(self.w.amount.get())
    self.doIt(-val,0)

  def right(self,sender):
    val = float(self.w.amount.get())
    self.doIt(val,0)

  def doIt(self, dx, dy):
    for n in Glyphs.font.selectedLayers[0].selection:
      if n.type == CURVE and n.smooth:
        self.nudge(n,dx,dy)
    Glyphs.redraw()

InterpolatedNudgeWindow()