#MenuTitle: 
# -*- coding: utf-8 -*-
__doc__=""
import GlyphsApp
from GlyphsApp import Proxy
from math import atan2, sqrt

class GSLineSegment(object):
  def __init__(self, tuple = None, owner = None, idx = 0):
    self._seg = tuple
    if not self._seg: self._seg = owner._segments[idx]
    self._owner = owner
    self._owneridx = idx

  def __repr__(self):
    """Return list-lookalike of representation string of objects"""
    return "<GSSegment (%s, %s)--(%s, %s)>" % (self.start().x,self.start().y,self.end().x,self.end().y)

  def _seg(self): return self._seg
  def start(self): return self._seg[0]
  def end(self): return self._seg[-1]

  def area(self):
    xa, ya = self.start().x, self.start().y/20
    xb, yb = xa, ya
    xc, yc = self.end().x, self.end().y/20
    xd, yd = xc, yc
    return (xb-xa)*(10*ya + 6*yb + 3*yc +   yd) + (xc-xb)*( 4*ya + 6*yb + 6*yc +  4*yd) +(xd-xc)*(  ya + 3*yb + 6*yc + 10*yd)

  def length(self):
    l1 = self.start().x - self.end().x
    l2 = self.start().y - self.end().y
    return sqrt(l1 * l1 + l2 * l2)
  def angle(self):
    e = self.end()
    s = self.start()
    return atan2(e.y - s.y, e.x - s.x)

class GSCurveSegment(GSLineSegment):
  def __repr__(self):
    return "<GSSegment (%s, %s)..[%s,%s]..[%s,%s]..(%s, %s)>" % (
      self.start().x, self.start().y,
      self.handle1().x, self.handle1().y,
      self.handle2().x, self.handle2().y,
      self.end().x,self.end().y
    )

  def handle1(self): return self._seg[1]
  def handle2(self): return self._seg[2]

  def area(self):
    xa, ya = self.start().x, self.start().y/20
    xb, yb = self.handle1().x, self.handle1().y/20
    xc, yc = self.handle2().x, self.handle2().y/20
    xd, yd = self.end().x, self.end().y/20
    return (xb-xa)*(10*ya + 6*yb + 3*yc +   yd) + (xc-xb)*( 4*ya + 6*yb + 6*yc +  4*yd) +(xd-xc)*(  ya + 3*yb + 6*yc + 10*yd)

  def angle(self):
    e = self.end()
    s = self.start()
    return atan2(e.y - s.y, e.x - s.x)

  def interpolate_at_fraction(self, t):
    if t < 0 or t > 1:
      raise Exception("interpolate_at_fraction should be called with a number between 0 and 1")
    t1 = 1.0 - t;
    t1_3 = t1*t1*t1
    t1_3a = (3*t)*(t1*t1)
    t1_3b = (3*(t*t))*t1;
    t1_3c = (t * t * t )
    x = (self.start().x * t1_3) + (t1_3a * self.handle1().x) + (t1_3b * self.handle2().x) + (t1_3c * self.end().x)
    y = (self.start().y * t1_3) + (t1_3a * self.handle1().y) + (t1_3b * self.handle2().y) + (t1_3c * self.end().y)
    return (x,y)

  def length(self):
    steps = 50
    t = 0.0
    length = 0
    previous = ()
    while t < 1.0:
      this = self.interpolate_at_fraction(t)
      if t > 0:
        dx = previous[0] - this[0]
        dy = previous[1] - this[1]
        length = length + sqrt(dx*dx+dy*dy)
      t = t + 1.0/steps
      previous = this
    return length

class PathSegmentsProxy (Proxy):
  def __getitem__(self, Key):
    if Key < 0:
      Key = self.__len__() + Key
    if len(self._owner._segments[Key]) == 2:
      return GSLineSegment( owner = self._owner, idx = Key)
    else:
      return GSCurveSegment( owner = self._owner, idx = Key)
  def __setitem__(self, Key, Layer):
    if Key < 0:
      Key = self.__len__() + Key
    # XXX
  def __len__(self):
    return len(self._owner._segments)
  def values(self):
    return map(self.__getitem__, range(0,self.__len__()))

GlyphsApp.GSPath._segments = GlyphsApp.GSPath.segments
GlyphsApp.GSPath.segments =  property( lambda self: PathSegmentsProxy(self),
  lambda self, value: self.setSegments_(map(lambda self: self._seg,value))
)