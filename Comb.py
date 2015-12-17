#MenuTitle: Comb
# -*- coding: utf-8 -*-
__doc__="""
Drag a comb through a path
"""
from math import cos, sin
from glyphmonkey import *

pathset = []
for a in Glyphs.font.selectedLayers[0].paths:

  # Find the two smallest "ends"
  l1, s1, l2, s2 = None, None, None, None

  for i in range(0,len(a.segments)):
    s = a.segments[i]
    if type(s) is GSLineSegment and (not l1 or s.length < l1):
      s1 = i
      l1 = s.length

  for i in range(0,len(a.segments)):
    s = a.segments[i]
    if type(s) is GSLineSegment and (s.length >= l1 and (not l2 or s.length < l2) and i != s1):
      s2 = i
      l2 = s.length

  if s1 > s2: s1, s2 = s2, s1
  print("Identified path end segments:")
  print(a.segments[s1], a.segments[s2])
  # Find two edges between segments
  edge1 = [ a.segments[i] for i in range(s1+1, s2) ]
  edge2 = [ a.segments[i] for i in range(s2+1, len(a.segments))]
  edge2.extend([a.segments[i] for i in range(0, s1)])
  for i in range(0, len(edge2)): edge2[i].reverse()
  edge2.reverse()
  print("\nIdentified edges")
  print("Edge 1:", edge1)
  print("Edge 2:", edge2)
  if len(edge1) != len(edge2):
    print("Edges not compatible - differing number of points")
    raise TypeError
  stripes = [ [0, 0.05], [0.1,0.15], [0.2,0.3], [0.35,0.6], [0.65,0.75],[0.8,0.85],[0.95, 1] ]
  for i in stripes:
    start, end = i[0],i[1]

    segs1 = []
    segs2 = []
    for i in range(0, len(edge1)):
      segs1.append(edge1[i].interpolate(edge2[i],start))
      segs2.append(edge1[i].interpolate(edge2[i],end))
    for i in range(0, len(segs2)): segs2[i].reverse()
    segs2.reverse()
    segs1.append(GSLineSegment(tuple = (segs1[-1]._seg[-1],segs2[0]._seg[0])))
    segs1.extend(segs2)
    segs1.append(GSLineSegment(tuple = (segs2[-1]._seg[-1],segs1[0]._seg[0])))

    segs = segs1

    path = GSPath()
    path.parent = a.parent
    path.segments = segs
    pathset.append(path)
    path.closed = True
Glyphs.font.selectedLayers[0].paths = pathset