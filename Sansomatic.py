#MenuTitle: Sans-o-Matic
# -*- coding: utf-8 -*-
__doc__="""
This is the stupidest script ever. Stupid, stupid, stupid.
"""

import vanilla
from math import sin,pi,tan,atan

capHeight = None
Dimensions = None

def clearLayer():
  Glyphs.font.selectedLayers[0].paths = []

def getControl(controls, label):
  if controls[label].has_key("value"):
    # print("Value of "+label, controls[label]["value"])
    return controls[label]["value"]
  # print("Using default for "+label, controls[label]["default"])
  return controls[label]["default"]

def lerp(t,a,b):
  return NSValue.valueWithPoint_(NSPoint(int((1-t)*a.x + t*b.x), int((1-t)*a.y + t*b.y)))
import math
def distance( node1, node2 ):
    return math.hypot( node1.x - node2.x, node1.y - node2.y )

def drawRectangle(x,y,w,h):
  bl = GSNode((x,y), type = LINE)
  br = GSNode((x+w,y), type = LINE)
  tr = GSNode((x+w,y+h), type = LINE)
  tl = GSNode((x,y+h), type = LINE)
  p = GSPath()
  p.nodes = [bl,br,tr,tl]
  p.closed = True
  Glyphs.font.selectedLayers[0].paths.append(p)

def stemWidthForTargetWeight(s,angle):
  return s / sin(pi/2-angle)

def drawAngledRectangle(x,y,w,h,angle):
  correctedWidth = stemWidthForTargetWeight(w, angle)
  bottomOffset = tan(angle) * h
  bl = GSNode((x+bottomOffset,y), type = LINE)
  br = GSNode((x+correctedWidth+bottomOffset,y), type = LINE)
  tr = GSNode((x+correctedWidth,y+h), type = LINE)
  tl = GSNode((x,y+h), type = LINE)
  p = GSPath()
  p.nodes = [bl,br,tr,tl]
  p.closed = True
  Glyphs.font.selectedLayers[0].paths.append(p)
  return x+bottomOffset

def getDimension(name):
  Font = Glyphs.font
  masterID = Glyphs.font.selectedLayers[0].associatedMasterId
  Dimensions = Font.userData["GSDimensionPlugin.Dimensions"][masterID]
  if not Dimensions or not Dimensions[name]:
    print("You must declare the "+name+" dimension in the palette")
    raise
  return float(Dimensions[name])

options = {}
sansomatic = {}


# A

def A(controls):
  angle = getControl(controls, "Angle")
  stem = getDimension("HV")
  crossbar = getDimension("HH")
  overlap = getControl(controls, "Overlap") / 100.0 * stem
  xHeight = getControl(controls, "Crossbar Height") / 100.0 * capHeight
  newX = drawAngledRectangle(0, capHeight, stem, -capHeight,angle)
  drawAngledRectangle(newX*2 - overlap, capHeight, stem, -capHeight,-angle)
  xbarOffset = tan(pi-angle)*xHeight
  xbarLen = tan(pi-angle)*(capHeight-(xHeight+crossbar))*2 - overlap
  drawRectangle(xbarOffset, xHeight + crossbar/2, xbarLen, crossbar)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 5
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["A"] = {
  'controls': {
    'Angle': { 'type': "Slider", 'min': 0.1, 'max':0.5, 'default': 0.3 },
    'Overlap': { 'type': "Slider", 'min': 0, 'max':100, 'default': 0 },
    'Crossbar Height': { 'type': "Slider", 'min': 10, 'max':60, 'default': 25 },
  },
  'method': A
}

# E

def E(controls):
  width = getControl(controls, "Leg Length")
  stem = getDimension("HV")
  crossbar = getDimension("HH")
  drawRectangle(stem, 0, width, crossbar)
  F(controls)

sansomatic["E"] = {
  'controls': {
      'Leg Length': { 'type': "Slider", 'min': 100, 'max':700, 'default': 300 },
      'Crossbar Percentage':  { 'type': "Slider", 'min': 20, 'max':100, 'default': 75 }
  },
  'method': E
}

# F

def F(controls):
  width = getControl(controls, "Leg Length")
  ratio = getControl(controls, "Crossbar Percentage") / 100.0
  stem = getDimension("HV")
  crossbar = getDimension("HH")
  drawRectangle(0, 0, stem, capHeight)
  drawRectangle(stem, capHeight-crossbar, width, crossbar)
  drawRectangle(stem, (capHeight/2)-(crossbar/2), width * ratio, crossbar)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 50
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["F"] = {
  'controls': {
      'Leg Length': { 'type': "Slider", 'min': 100, 'max':700, 'default': 300 },
      'Crossbar Percentage':  { 'type': "Slider", 'min': 20, 'max':100, 'default': 75 }
  },
  'method': F
}

# H

def H(controls):
  width = getControl(controls, "Crossbar Width")
  stem = getDimension("HV")
  crossbar = getDimension("HH")
  drawRectangle(0, 0, stem, capHeight)
  drawRectangle(width+stem, 0, stem, capHeight)
  drawRectangle(stem,(capHeight/2)-(crossbar/2), width, crossbar)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 50
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["H"] = {
  'controls':  {
      'Crossbar Width': { 'type': "Slider", 'min': 100, 'max':700, 'default': 300 }
  },
  'method': H
}

# I

def I(controls):
  stem = getDimension("HV")
  crossbarHt = getDimension("HH")
  drawRectangle(0, 0, stem, capHeight)
  if getControl(controls, "Crossbars?"):
    crossbarLen = getControl(controls, "Crossbar Width")
    drawRectangle(-crossbarLen/2 + stem/2, capHeight-crossbarHt, crossbarLen, crossbarHt)
    drawRectangle(-crossbarLen/2 + stem/2, 0, crossbarLen, crossbarHt)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 50
  Glyphs.font.selectedLayers[0].removeOverlap()


sansomatic["I"] = {
  'controls': {
    'Crossbars?': { 'type': "CheckBox", 'default': False },
    'Crossbar Width': { 'type': "Slider", 'min': 0, 'max':700, 'default': 500 }
  },
  'method': I
}

# L

def L(controls):
  width = getControl(controls, "Leg Length")
  stem = getDimension("HV")
  crossbar = getDimension("HH")
  drawRectangle(0, 0, stem, capHeight)
  drawRectangle(stem, 0, width, crossbar)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 50
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["L"] = {
  'controls': {
    'Leg Length': { 'type': "Slider", 'min': 0, 'max':700, 'default': 300 }
  },
  'method': L
}


# N

def N(controls):
  angle = getControl(controls, "Angle")

  stem = getDimension("HV")
  newX = drawAngledRectangle(0, 0, stem, capHeight,angle)
  width = tan(angle)*capHeight + stemWidthForTargetWeight(stem,angle)
  drawRectangle(newX+(stemWidthForTargetWeight(stem,angle)-stem), 0,stem,capHeight)
  drawRectangle(0, 0,stem,capHeight)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 50
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["N"] = {
  'controls': {
    'Angle': { 'type': "Slider", 'min': 0.3, 'max':0.523, 'default': 0.4 },
  },
  'method': N
}

# O

def O(controls):
  width = getControl(controls, "Width")
  stem = getDimension("OV")
  crossbar = getDimension("OH")
  htension = getControl(controls,"H Tension")
  vtension = getControl(controls,"V Tension")
  overshoot = getControl(controls,"Overshoot")

  bc = GSNode((width/2,-overshoot), type = CURVE)
  bc.smooth = True
  bcl = GSNode((width/2-htension*(width/2),-overshoot), type = OFFCURVE)
  bcr = GSNode((width/2+htension*(width/2),-overshoot), type = OFFCURVE)
  l = GSNode((0,capHeight/2), type = CURVE)
  l.smooth = True
  lr = GSNode((0,capHeight/2-vtension*(capHeight/2)), type = OFFCURVE)
  ll = GSNode((0,capHeight/2+vtension*(capHeight/2)), type = OFFCURVE)
  r = GSNode((width,capHeight/2), type = CURVE)
  rr = GSNode((width,capHeight/2-vtension*(capHeight/2)), type = OFFCURVE)
  rl = GSNode((width,capHeight/2+vtension*(capHeight/2)), type = OFFCURVE)
  r.smooth = True
  tc = GSNode((width/2,capHeight+overshoot), type = CURVE)
  tc.smooth = True
  tcl = GSNode((width/2-htension*(width/2),capHeight+overshoot), type = OFFCURVE)
  tcr = GSNode((width/2+htension*(width/2),capHeight+overshoot), type = OFFCURVE)

  p = GSPath()
  p.nodes = [bcr,rr,r,rl,tcr,tc,tcl,ll,l,lr,bcl,bc]
  p.closed = True
  Glyphs.font.selectedLayers[0].paths.append(p)

  htension = htension * (width/capHeight)
  vtension = vtension * (width/capHeight)

  bc = GSNode((width/2,crossbar), type = CURVE)
  bc.smooth = True
  bcl = GSNode((width/2-htension*(width/2),crossbar), type = OFFCURVE)
  bcr = GSNode((width/2+htension*(width/2),crossbar), type = OFFCURVE)
  l = GSNode((stem,capHeight/2), type = CURVE)
  l.smooth = True
  lr = GSNode((stem,capHeight/2-vtension*(capHeight/2)), type = OFFCURVE)
  ll = GSNode((stem,capHeight/2+vtension*(capHeight/2)), type = OFFCURVE)
  r = GSNode((width-stem,capHeight/2), type = CURVE)
  rr = GSNode((width-stem,capHeight/2-vtension*(capHeight/2)), type = OFFCURVE)
  rl = GSNode((width-stem,capHeight/2+vtension*(capHeight/2)), type = OFFCURVE)
  r.smooth = True
  tc = GSNode((width/2,capHeight-crossbar), type = CURVE)
  tc.smooth = True
  tcl = GSNode((width/2-htension*(width/2),capHeight-crossbar), type = OFFCURVE)
  tcr = GSNode((width/2+htension*(width/2),capHeight-crossbar), type = OFFCURVE)

  p = GSPath()
  p.nodes = [bcr,rr,r,rl,tcr,tc,tcl,ll,l,lr,bcl,bc]
  p.closed = True
  Glyphs.font.selectedLayers[0].paths.append(p)

  Glyphs.font.selectedLayers[0].correctPathDirection()


  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 15
  # Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["O"] = {
  'controls': {
    'Width': { 'type': "Slider", 'min': 0, 'max':700, 'default': 450 },
    'Overshoot': { 'type': "Slider", 'min': 0, 'max':20, 'default': 10 },
    'H Tension': { 'type': "Slider", 'min': 0.4, 'max':1, 'default': 0.6 },
    'V Tension': { 'type': "Slider", 'min': 0.4, 'max':1, 'default': 0.75 }
  },
  'method': O
}

def S(controls):
  capHeight = master.capHeight

  topwidth = getControl(controls, "Top Width")
  bottomwidth = getControl(controls, "Bottom Width")

  center = 400
  tau = getControl(controls, "Tension")
  alpha = getControl(controls, "Bar Straightness")
  barHeight = getControl(controls, "Bar Height") * capHeight
  leftThick = 55
  rightThick = 80
  barWidth = getControl(controls, "Bar Thickness")
  slope = getControl(controls, "Bar Slope")
  sign = 1
  overshoot = getControl(controls, "Overshoot")
  hairline = getControl(controls, "Hairline Thickness")

  def doCurve(sign):
    if sign == 1:
      top= capHeight + overshoot
    else:
      top= capHeight + overshoot - hairline
    t = GSNode((center,top), type = LINE)
    t.smooth = True
    
    xleft = center - topwidth - sign * leftThick/2
    c = GSNode((center, barHeight - sign * barWidth/2), type = LINE)
    
    i2 = NSPoint(xleft, top)
    i = NSPoint(xleft, barHeight - sign * barWidth/2 + slope * (topwidth + sign * leftThick/2))
    t1 = GSNode(lerp(tau, t.position, i2).pointValue(), type = OFFCURVE)
    x = GSNode(lerp(alpha, c.position, i).pointValue(), type = CURVE)
    x1 = GSNode(lerp(tau, x.position, i).pointValue(), type = OFFCURVE)

    xright = center + bottomwidth - sign * rightThick/2
    
    i_lower = NSPoint(xright, barHeight - sign * barWidth/2 - slope * (bottomwidth-sign * rightThick/2))
    x_lower = GSNode(lerp(alpha, c.position, i_lower).pointValue(), type = LINE)
    x1_lower = GSNode(lerp(tau, x_lower.position, i_lower).pointValue(), type = OFFCURVE)
    
    
    # yc-y=s * xc-x
    
    d_i2_t1 = distance(i2,t1)
    d_x1_i = distance(x1,i)
    
    yl_num = d_i2_t1 * i.y  - d_x1_i * t.y + math.sqrt(d_i2_t1 * d_x1_i * i.y * i.y - 2 * d_i2_t1 * d_x1_i * i.y * t.y + d_i2_t1 * d_x1_i * t.y * t.y)
    yl_den = d_i2_t1 - d_x1_i
    yl = yl_num / yl_den
    
    
    l = GSNode(( xleft, yl), type = CURVE)
    l.smooth = True
    l1 = GSNode(lerp(tau, l.position, i2).pointValue(), type = OFFCURVE)
    l2 = GSNode(lerp(tau, l.position, i).pointValue(), type = OFFCURVE)
    

    if sign == -1:
      base = -overshoot
    else:
      base = -overshoot + hairline

    b = GSNode((center,base), type = CURVE)
  #   b.smooth = True
    
    i2_lower = NSPoint(xright, b.y)
    
    b1 = GSNode(lerp(tau, b.position, i2_lower).pointValue(), type = OFFCURVE)
    
    l1 = GSNode(lerp(tau, l.position, i2).pointValue(), type = OFFCURVE)
    l2 = GSNode(lerp(tau, l.position, i).pointValue(), type = OFFCURVE)
    
    d_i2_lower_b1 = distance(i2_lower,b1)
    d_x1_lower_i_lower = distance(i_lower,x1_lower)
    yr_num = d_i2_lower_b1 * i_lower.y  - d_x1_lower_i_lower * b.y - math.sqrt(d_i2_lower_b1 * d_x1_lower_i_lower * i_lower.y * i_lower.y - 2 * d_i2_lower_b1 * d_x1_lower_i_lower * i_lower.y * b.y + d_i2_lower_b1 * d_x1_lower_i_lower * b.y * b.y)
    yr_den = d_i2_lower_b1 - d_x1_lower_i_lower
    yr = yr_num / yr_den
    r = GSNode(( xright, yr), type = CURVE)
    r1 = GSNode(lerp(tau, r.position, i2_lower).pointValue(), type = OFFCURVE)
    r2 = GSNode(lerp(tau, r.position, i_lower).pointValue(), type = OFFCURVE)
    r.smooth = True
    if sign == 1:
      return [t,t1,l1,l, l2, x1,x, x_lower,x1_lower,r2,r,r1,b1,b]
    b.type = LINE
    x_lower.type = CURVE
    x.type = LINE
    t.type = CURVE

    return [b, b1, r1, r, r2, x1_lower, x_lower, x, x1, l2, l, l1, t1, t]

  p = GSPath()
  n = []
  n.extend(doCurve(1))
  nodes2 = doCurve(-1)
  n.extend(nodes2)
  p.nodes = n
  p.closed = True
  Glyphs.font.selectedLayers[0].paths.append(p)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 50

sansomatic["S"] = {
  'controls': {
    'Overshoot': { 'type': "Slider", 'min': 0, 'max':20, 'default': 10 },
    'Tension': { 'type': "Slider", 'min': 0.5, 'max':0.9, 'default': 0.6 },
    'Top Width': { 'type': "Slider", 'min': 0, 'max':700, 'default': 200 },
    'Bottom Width': { 'type': "Slider", 'min': 0, 'max':700, 'default': 225 },
    'Bar Straightness': { 'type': "Slider", 'min': 0, 'max':0.5, 'default': 0.2 },
    'Bar Slope': { 'type': "Slider", 'min': 0, 'max':0.5, 'default': 0.2 },
    'Bar Height': { 'type': "Slider", 'min': 0.5, 'max':0.7, 'default': 0.55 },
    'Bar Thickness': { 'type': "Slider", 'min': 0, 'max':300, 'default': 120 },
    'Hairline Thickness': { 'type': "Slider", 'min': 0, 'max':100, 'default': 20 }

  },
  'method': S
}

# T

def T(controls):
  width = getControl(controls, "Crossbar Width")
  stem = getDimension("HV")
  crossbar = getDimension("HH")
  width = width + stem
  drawRectangle(0, capHeight-crossbar, width, crossbar)
  drawRectangle(width/2 - stem/2, 0, stem, capHeight)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 50
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["T"] = {
  'controls': {
    'Crossbar Width': { 'type': "Slider", 'min': 0, 'max':700, 'default': 300 }
  },
  'method': T
}

# V

def V(controls):
  angle = getControl(controls, "Angle")
  stem = getDimension("HV")
  overlap = getControl(controls, "Overlap") / 100 * stem
  newX = drawAngledRectangle(0, 0, stem, capHeight,angle)
  drawAngledRectangle(newX*2 + overlap, 0, stem, capHeight,-angle)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 5
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["V"] = {
  'controls': {
    'Angle': { 'type': "Slider", 'min': 0.1, 'max':0.5, 'default': 0.3 },
    'Overlap': { 'type': "Slider", 'min': 0, 'max':100, 'default': 0 },
  },
  'method': V
}


# X

def X(controls):
  angle = getControl(controls, "Angle")
  stem = getDimension("HV")
  newX = drawAngledRectangle(0, 0, stem, capHeight,angle)
  drawAngledRectangle(newX, 0, stem, capHeight,-angle)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 5
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["X"] = {
  'controls': {
    'Angle': { 'type': "Slider", 'min': 0.3, 'max':0.8, 'default': 0.523 },
  },
  'method': X
}

# Y

def Y(controls):
  angle = getControl(controls, "Angle")
  stem = getDimension("HV")
  joinHeight = (capHeight-stem) * getControl(controls, "Join Height") / 100.0
  newX = drawAngledRectangle(0, joinHeight, stem, capHeight-joinHeight,angle)
  drawAngledRectangle(newX*2, joinHeight, stem, capHeight-joinHeight,-angle)
  drawRectangle(newX,0,stemWidthForTargetWeight(stem,angle),joinHeight)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 5
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["Y"] = {
  'controls': {
    'Angle': { 'type': "Slider", 'min': 0.3, 'max':0.8, 'default': 0.4 },
    'Join Height': { 'type': "Slider", 'min': 25, 'max':75, 'default': 50 },

  },
  'method': Y
}

# Z

def Z(controls):
  angle = getControl(controls, "Angle")

  stem = getDimension("HV")
  crossbar = getDimension("HH")
  newX = drawAngledRectangle(0, 0, stem, capHeight,-angle)
  offset = tan(angle)*crossbar
  width = tan(angle)*capHeight + stemWidthForTargetWeight(stem,angle)
  drawRectangle(newX+offset, 0,width-offset,crossbar)
  drawRectangle(newX, capHeight-crossbar,width-offset,crossbar)
  Glyphs.font.selectedLayers[0].LSB = Glyphs.font.selectedLayers[0].RSB = 5
  Glyphs.font.selectedLayers[0].removeOverlap()

sansomatic["Z"] = {
  'controls': {
    'Angle': { 'type': "Slider", 'min': 0.3, 'max':0.523, 'default': 0.4 },
  },
  'method': Z
}

myWindow = None

def createWindow(controls, fn):
  winWidth = 300
  winHeight = 40 * (1+len(controls)) + 20
  myWindow = vanilla.FloatingWindow((winWidth, winHeight), "Sans-o-Matic")
  x = 10
  y = 10
  for k in controls:
    v = controls[k]
    label = vanilla.TextBox((x,y,150,30), k)
    x = x + 120
    def controlCallback (s):
      for k2 in controls:
        v2 = controls[k2]
        controls[k2]["value"] = getattr(myWindow,k2).get()
      clearLayer()
      fn(controls)

    if v['type'] == "Slider":
      control = vanilla.Slider((x,y,-10,30),
        minValue = v['min'],
        maxValue = v['max'],
        value=v['default'],
        callback = controlCallback
      )
    elif v['type'] == "CheckBox":
      control = vanilla.CheckBox((x,y,10,10),"",
        callback = controlCallback
      )
    setattr(myWindow,k,control)
    setattr(myWindow,k+"label",label)

    y = y + 40
    x = 10
  def dismiss(s):
    myWindow.close()
    myWindow = None
  myWindow.dismiss   = vanilla.Button((-75, y, -15, -15), "OK", sizeStyle='regular', callback=dismiss )
  fn(controls)
  myWindow.open()

def rebuild():
  masterID = Glyphs.font.selectedLayers[0].associatedMasterId
  master = Glyphs.font.masters[masterID]
  global capHeight
  capHeight = master.capHeight

  Font = Glyphs.font
  glyph = Glyphs.font.selectedLayers[0].parent
  Dimensions = Font.userData["GSDimensionPlugin.Dimensions"]
  if not Dimensions:
    print("You must set your stem widths in the dimension palette")
  Dimensions = Dimensions[masterID]

  print(sansomatic.keys())
  if sansomatic.has_key(glyph.string):
    clearLayer()
    controls = sansomatic[glyph.string]["controls"]
    if len(controls) > 0:
      createWindow(controls, sansomatic[glyph.string]["method"])
  else:
    print("Don't know how to draw a "+glyph.string)

rebuild()
NSNotificationCenter.defaultCenter.addObserver_selector_name_object(None, rebuild, "GSUpdateInterface", None)
