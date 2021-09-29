#MenuTitle: Recipe dumper
# -*- coding: utf-8 -*-
__doc__="""
Show a recipe for the selected glyphs which can be fed to "Add Glyphs..."
"""

for l in Glyphs.font.selectedLayers:
	if l.components:
		print("+".join(c.componentName for c in l.components)+'='+l.glyph().name)