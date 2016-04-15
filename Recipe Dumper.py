for l in Glyphs.font.selectedLayers:
	if l.components:
		print("+".join(c.componentName for c in l.components)+'='+l.glyph().name)