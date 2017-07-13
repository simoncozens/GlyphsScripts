#MenuTitle: LightSpace
# -*- coding: utf-8 -*-
__doc__="""
Experimental spacer based on Hochuli's "light from above and below"
"""

layer = Glyphs.font.selectedLayers[0] # current layer
layerId = layer.layerId

def light(layer, spectralFactor):
  x = layer.bounds.origin.x
  end = layer.bounds.origin.x + layer.bounds.size.width
  delta = 5
  toptotal = 0
  bottomtotal =0
  # Lazy way to get ascender, descender, avoids grubbing in master objects
  bottom = layer.bounds.origin.y - layer.BSB
  top = layer.bounds.origin.y + layer.bounds.size.height + layer.TSB

  while x < end:
    startPoint = NSMakePoint(x, bottom)
    endPoint = NSMakePoint(x, top)
    result = layer.calculateIntersectionsStartPoint_endPoint_(startPoint, endPoint)
    if (len(result) > 2):
      t = result[1]
      b = result[-2]
      toptotal += top-t.y * delta
      bottomtotal += b.y-bottom * delta
    x += delta
  return toptotal*spectralFactor + bottomtotal, toptotal, bottomtotal

def sideLight(layer):
  bottom = layer.bounds.origin.y - layer.BSB
  top = layer.bounds.origin.y + layer.bounds.size.height + layer.TSB
  return (top-bottom) * (layer.RSB + layer.LSB)

# Find a spectralFactor which equalizes u and n
ewe = Glyphs.font.glyphs['u'].layers[layerId]
enn = Glyphs.font.glyphs['n'].layers[layerId]
_,uTop,uBottom = light(ewe,1)
_,nTop,nBottom = light(enn,1)
num = sideLight(ewe) - sideLight(enn) + uBottom - nBottom
denom = sideLight(enn) - sideLight(ewe) + nTop - uTop
spectralFactor = num / denom
print(spectralFactor)

goal = (light(enn,spectralFactor)[0] + sideLight(enn)) # / (enn.LSB+enn.RSB + enn.bounds.size.width)


# I can't be bothered to do the math. Brute force it.
iterations = 0
layer.beginChanges()
balance = layer.RSB / layer.LSB
totalLight = light(layer,spectralFactor)[0]
while True:
  if iterations > 100: break
  iterations = iterations + 1
  current = (totalLight + sideLight(layer)) # / (layer.LSB+layer.RSB + layer.bounds.size.width)
  print(current,goal)
  if abs(current - goal) < 1.0: break
  factor = current / goal
  if current < goal:
    layer.LSB = layer.LSB + factor
    layer.RSB = layer.LSB * balance
  if current > goal:
    layer.LSB = layer.LSB - factor
    layer.RSB = layer.LSB * balance

layer.endChanges()