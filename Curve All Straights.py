#MenuTitle: Curve All Straights
# -*- coding: utf-8 -*-
__doc__="""
Turn corners into smooths (useful when tracing)
"""
import GlyphsApp
from Foundation import NSPoint, NSValue

def lerp(t,a,b):
  return NSValue.valueWithPoint_(NSPoint(int((1-t)*a.x + t*b.x), int((1-t)*a.y + t*b.y)))

for p in Glyphs.font.selectedLayers[0].paths:
  news = []
  for idx,segment in enumerate(p.segments):
    if len(segment) == 4:
      news.append(segment)
    else:
      s,e = segment[0], segment[-1]
      news.append((s,lerp(0.33,s,e),lerp(0.66,s,e),e))
  print(news)
  p.segments = news
  for i,n in enumerate(p.nodes):
#     n.type = GlyphsApp.GSCURVE
    n.connection = GlyphsApp.GSSMOOTH
