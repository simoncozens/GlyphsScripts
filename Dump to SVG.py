#MenuTitle: Dump to SVG
# -*- coding: utf-8 -*-
for path in Glyphs.font.selectedLayers[0].paths:
    for ix, seg in enumerate(path.segments):
        if ix == 0:
            print(f"M {seg[0].x} {seg[0].y}")
        if len(seg) == 2:
            print(f"L {seg[1].x} {seg[1].y}")
        else:
            print(f"C {seg[1].x} {seg[1].y} {seg[2].x} {seg[2].y} {seg[3].x} {seg[3].y}")
    print("Z\n")
