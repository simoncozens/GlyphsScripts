#MenuTitle: Add Anchors From File
# -*- coding: utf-8 -*-
import GlyphsApp
from Foundation import NSPoint, NSValue, NSMinY, NSMaxY, NSMinX, NSMaxX
import csv


with open('anchors.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if "name" in row:
            glyph = row["name"]
        elif "glyph" in row:
            glyph = row["glyph"]
        else:
            raise ValueError("Glyph name column not found")
        if not glyph in Glyphs.font.glyphs:
            print("Could not find glyph %s" % glyph)
            continue
        anchornames = [ x.replace("_x","") for x in row.keys() if "_x" in x]
        Layer = Glyphs.font.glyphs[glyph].layers[0]
        print(glyph)
        for a in anchornames:
            if not row[a+"_x"] or not row[a+"_y"]:
                continue
            x = int(row[a+"_x"])
            y = int(row[a+"_y"])
            print(a, x, y)
            Layer.anchors[a] = GSAnchor(a)
            Layer.anchors[a].position = NSPoint(x,y)
