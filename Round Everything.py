#MenuTitle: Round Everything
# -*- coding: utf-8 -*-
__doc__="""
Round all coordinates of everything to integers
"""

from Foundation import NSPoint


def roundattrs(thing, attrs):
	for attr in attrs:
		if isinstance(getattr(thing, attr), float):
			setattr(thing, attr, round(getattr(thing, attr)))

for g in Glyphs.font.glyphs:
	g.beginUndo()
	for l in g.layers:
		roundattrs(l, ["LSB", "RSB", "TSB", "BSB", "width", "vertWidth"])
		for guide in l.guides:
			guide.position = NSPoint(round(guide.position.x), round(guide.position.y))
		for anchor in l.anchors:
			anchor.position = NSPoint(round(anchor.position.x), round(anchor.position.y))
		l.roundCoordinates()
	g.endUndo()
