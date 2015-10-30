#MenuTitle: 
# -*- coding: utf-8 -*-
__doc__=""
import GlyphsApp
from GlyphsApp import Proxy
from math import atan2, sqrt, cos, sin, radians

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

# Unfortunately working with segments doesn't always *work*. So we
# map a segment list to a node list
GSNode = GlyphsApp.GSNode

def toNodeList(segments):
  nodelist = []
  for i in range(0,len(segments)):
    s = segments[i]
    t = GlyphsApp.GSCURVE
    c = GlyphsApp.GSSMOOTH
    if type(s) is GSLineSegment:
      t = GlyphsApp.GSLINE
    else:
      s1 = s.handle1()
      nodelist.append(GSNode((s1.x,s1.y), GlyphsApp.GSOFFCURVE))
      s2 = s.handle2()
      nodelist.append(GSNode((s2.x,s2.y), GlyphsApp.GSOFFCURVE))

    ns = i+1
    if ns >= len(segments): ns = 0
    if type(segments[ns]) is GSLineSegment:
      c = GlyphsApp.GSSHARP
    e = s.end()
    node = GSNode((e.x, e.y), t)
    node.connection = c
    nodelist.append(node)
  return nodelist

GlyphsApp.GSPath.segments =  property( lambda self: PathSegmentsProxy(self),
  lambda self, value: self.setNodes_(toNodeList(value))
)

def nodeRotate(self, ox, oy, angle):
  angle = radians(angle)
  newX = ox + (self.position.x-ox)*cos(angle) - (self.position.y-oy)*sin(angle)
  newY = oy + (self.position.x-ox)*sin(angle) + (self.position.y-oy)*cos(angle)
  self.position = (round(newX,2), round(newY,2))

GlyphsApp.GSNode.rotate = nodeRotate

### additional GSPath methods

def layerCenter(self):
  bounds = self.parent.bounds
  ox = bounds.origin.x + bounds.size.width / 2
  oy = bounds.origin.y + bounds.size.height / 2
  return (ox, oy)

def pathCenter(self):
  bounds = self.bounds
  ox = bounds.origin.x + bounds.size.width / 2
  oy = bounds.origin.y + bounds.size.height / 2
  return (ox, oy)

def pathRotate(self, angle=-1, ox=-1, oy=-1):
  if angle == -1: angle = 180
  if ox == -1 and oy == -1:
    if self.parent: # Almost always
      ox, oy = self.layerCenter()
    else:
      ox, oy = self.center()

  for n in self.nodes:
    n.rotate(ox, oy, angle)
  return self

def pathDiff(p1, p2):
  nodes1 = set((n.position.x,n.position.y) for n in p1.nodes)
  nodes2 = set((n.position.x,n.position.y) for n in p2.nodes)
  return nodes1 - nodes2

def pathEqual(p1, p2):
  pd = pathDiff(p1, p2)
  return len(pd) == 0

GlyphsApp.GSPath.layerCenter = layerCenter
GlyphsApp.GSPath.center = pathCenter
GlyphsApp.GSPath.rotate = pathRotate
GlyphsApp.GSPath.equal = pathEqual
GlyphsApp.GSPath.diff = pathDiff

# Does p have rotational symmetry?
#   ox, oy = p.layerCenter()
#   p.equal(p.copy().rotate(angle=180, ox=ox, oy=oy))
