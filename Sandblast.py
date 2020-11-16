#MenuTitle: Sandblast
# -*- coding: utf-8 -*-
__doc__="""
Drill randomly-sized holes in the glyph
"""

import random
import math
from Foundation import NSMakePoint

layer = Glyphs.font.selectedLayers[0] # current layer
left, bottom = layer.bounds.origin.x, layer.bounds.origin.y
width, height = layer.bounds.size.width, layer.bounds.size.height

dust = []
f = layer.completeBezierPath

points = 1000
while points:
	x = random.randrange(left, left+width)
	y = random.randrange(bottom, bottom+height)
	if not f.containsPoint_(NSMakePoint(x,y)):
		continue
	sides = random.randrange(15,30)
	p = GSPath()
	angle = math.radians(360/sides)
	
	for i in range(sides):
		p.nodes.append(GSNode( (x, y), LINE))
		delta = abs(random.gauss(5,20) / float(sides))
			
		x = x + math.cos(i * angle) * (random.random() + delta)
		y = y + math.sin(i * angle) * (random.random() + delta)
	points = points - 1
	p.closed = True
	if p.direction == layer.paths[0].direction:
		p.reverse()
	dust.append(p)

GSPathOperator = objc.lookUpClass("GSPathOperator")

pathOp = GSPathOperator.alloc().init()

inpaths = list(layer.paths)
pathOp.subtractPaths_from_error_( dust, inpaths, None )

layer.paths.extend(inpaths)


# layer.paths.extend(dust)

layer.correctPathDirection()
