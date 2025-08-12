# MenuTitle: Derive Anchors From Components
# -*- coding: utf-8 -*-
__doc__ = """
Use the position of mark components in base/mark composite glyphs to derive anchors
in the base glyph.
"""
marks_with_anchors = {}


def isBase(g):
    if isinstance(g, str):
        g = Glyphs.font.glyphs[g]
    return not (g.category == "Mark" and g.subCategory == "Nonspacing")


def hasAnchor(layer, name):
    return layer.anchors[name]


for g in Glyphs.font.glyphs:
    if isBase(g):
        continue
    markanchors = [anchor for anchor in g.layers[0].anchors if anchor.name[0] == "_"]
    if not markanchors:
        continue
    if len(markanchors) > 1:
        print(f"{g.name} is ambiguously attached")
    else:
        marks_with_anchors[g.name] = markanchors[0].name[1:]


def derive_anchor(base, marks, source):
    baseglyph = Glyphs.font.glyphs[base]
    needed_anchors = set(marks_with_anchors[m] for m in marks)
    for ix, (baselayer, sourcelayer) in enumerate(zip(baseglyph.layers, source.layers)):
        for m in marks:
            anchor = marks_with_anchors[m]
            if hasAnchor(baselayer, anchor):
                continue
            marklayer = Glyphs.font.glyphs[m].layers[ix]
            anchorpos = marklayer.anchors["_" + anchor].position
            basecomp = [c for c in sourcelayer.components if c.name == m]
            basecomp = basecomp[0]
            print(baselayer, sourcelayer)
            newpos = (
                anchorpos.x + basecomp.position.x,
                anchorpos.y + basecomp.position.y,
            )
            baselayer.anchors.append(GSAnchor(anchor, newpos))


#
# 			print(baselayer, " needs: ", anchor, " at ", newpos, " because of ",source.name)


for g in Glyphs.font.glyphs:
    if not isBase(g):
        continue
    mark_components = set([])
    base_components = []
    for c in g.layers[0].components:
        if c.name in marks_with_anchors:
            mark_components.add(c.name)
        if isBase(c.name):
            base_components.append(c)
    if mark_components and len(base_components) == 1:
        derive_anchor(base_components[0].name, mark_components, g)
