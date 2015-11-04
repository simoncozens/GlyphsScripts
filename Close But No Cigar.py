#MenuTitle: Close, but no cigar...
# -*- coding: utf-8 -*-
__doc__="""
Report on angles, widths and positions which are nearly, but not quite, right
"""

within = 0.05 # 5% of target
angleTolerance = 2
# Check stems and angles

Glyphs.clearLog()

from glyphmonkey import GSLineSegment

def closeButNotRelative(l1, l2, tolerance):
  return l1 != l2 and (l2 * (1-tolerance) < l1 and l1 < l2 * (1+tolerance))

def closeButNotAbsolute(l1, l2, tolerance):
  return l1 != l2 and (l2-tolerance) < l1 and l1 < l2+tolerance

def checkHorizontal(layer, s, h):
  thisLen = s.length
  thisAng = s.angle
  for stem in h:
    if thisLen == stem: return

  if (-angleTolerance < thisAng and thisAng < angleTolerance) or (180-angleTolerance < thisAng and thisAng < 180+angleTolerance):
    for stem in h:
      if closeButNotRelative(thisLen, stem, within):
        print("\nSegment %s in %s, has length %s, should be horizontal stem length %s?" % (s, layer, thisLen, stem))

def checkVertical(layer, s,v):
  thisAng = s.angle
  thisLen = s.length
  for stem in v:
    if thisLen == stem: return

  if (90-angleTolerance < thisAng and thisAng < 90+angleTolerance) or (-90-angleTolerance < thisAng and thisAng < -90+angleTolerance):
    for stem in v:
      if closeButNotRelative(thisLen, stem, within):
        print("\nSegment %s in %s, has length %s, should be vertical stem length %s?" % (s, layer, thisLen, stem))

def checkAngle(layer, s):
  thisAng = s.angle
  if (thisAng != 0 and (-angleTolerance < thisAng and thisAng < angleTolerance)):
    print("\nNearly-perpendicular %s in %s, angle was %s, should be horizonal?" % (s, layer, thisAng))

  if (thisAng != 180 and (180-angleTolerance < thisAng and thisAng < 180+angleTolerance)):
    print("\nNearly-perpendicular %s in %s, angle was %s, should be horizontal?" % (s, layer, thisAng))

  if (thisAng != 90 and (90-angleTolerance < thisAng and thisAng < 90+angleTolerance)):
    print("\nNearly-perpendicular %s in %s, angle was %s, should be vertical?" % (s, layer, thisAng))

  if (thisAng != -90 and (-90-angleTolerance < thisAng and thisAng < -90+angleTolerance)):
    print("\nNearly-perpendicular %s in %s, angle was %s, should be vertical?" % (s, layer, thisAng))

def checkNodePosition(layer, node, m):
  px, py = node.position.x, node.position.y
  if closeButNotAbsolute(px,0,2):
    print("\nX co-ordinate of %s in %s nearly (but not quite) zero" % (node, layer))
  if closeButNotAbsolute(py,0,2):
    print("\nY co-ordinate of %s in %s nearly (but not quite) zero" % (node, layer))

  if closeButNotAbsolute(py,m.ascender,2):
    print("\nY co-ordinate of %s in %s nearly (but not quite) ascender" % (node, layer))
  if closeButNotAbsolute(py,m.capHeight,2):
    print("\nY co-ordinate of %s in %s nearly (but not quite) cap height" % (node, layer))
  if closeButNotAbsolute(py,m.xHeight,2):
    print("\nY co-ordinate of %s in %s nearly (but not quite) x height" % (node, layer))
  if closeButNotAbsolute(py,m.descender,2):
    print("\nY co-ordinate of %s in %s nearly (but not quite) descender" % (node, layer))

glyph = Glyphs.font.selectedLayers[0].parent
for l in glyph.layers:
  m = Glyphs.font.masters[l.associatedMasterId]
  v = m.verticalStems
  h = m.horizontalStems
  for p in l.paths:
    for s in p.segments:
      thisAng = s.angle
      checkAngle(l, s)
      if h and len(h) > 0:
        checkHorizontal(l, s, h)
      if v and len(v) > 0:
        checkVertical(l, s, v)
    for n in p.nodes:
      checkNodePosition(l,n,m)
