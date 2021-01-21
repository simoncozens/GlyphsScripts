#MenuTitle: Copy Myanmar Anchors
# -*- coding: utf-8 -*-
import GlyphsApp

wa = Glyphs.font.glyphs["ဝ"]
ka = Glyphs.font.glyphs["က"]
singlebowl = "ခဂငစဎဒဓပဖဗမဧဋဌဍ"
doublebowl = "ဃဆညတထဘယလသဟအဢ"

def copyanchors(g1, g2):
	for l1, l2 in zip(g1.layers, g2.layers):
		for anchor in l1.anchors:
			copied = GSAnchor(anchor.name, anchor.position)
			l2.anchors[anchor.name] = copied

for g in singlebowl:
	if not Glyphs.font.glyphs[g]:
		continue
	copyanchors(wa, Glyphs.font.glyphs[g])

for g in doublebowl:
	if not Glyphs.font.glyphs[g]:
		continue
	copyanchors(ka, Glyphs.font.glyphs[g])
