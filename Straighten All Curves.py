#MenuTitle: Straighten All Curves
# -*- coding: utf-8 -*-
__doc__="""
Turn curve shapes into straight lines
"""

for p in Glyphs.font.selectedLayers[0].paths:
	news = []
	for idx,segment in enumerate(p.segments):
		news.append((segment[0],segment[-1]))
	p.segments = news
