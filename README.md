# GlyphsScripts

This repository contains some scripts for the Glyphs font editor. Some of them require the `glyphmonkey` library, which is part of this repository, to be installed. Dropping it into your scripts folder should be fine.

## Cadence grid

This sets up guidelines according to the LeMo cadencing method. Ideally it should also autospace your glyphs, but it doesn't at the moment.

## Close But No Cigar

This checks a glyph for: stem widths which are close to but not the stem widths you set in the master info; segments which are close to but not perpendicular; points which are close to but not on the baseline, x height, or cap height. The report turns up in the Macro window. This requires `glyphmonkey`.

## Comb

Drags a "comb" through your glyphs, for a very 70s effect. The glyphs need to be constructed in a *very* particular way. They need to be made up of paths which are topologically equivalent to rectangles. The "comb" will be dragged from the shortest edge to the second shortest edge. Between those two edges, the paths should be equivalent - same number of points, same types of curve/straight. They don't need to be absolutely symmetrical, but they do need to be conformant. So: to draw an O, draw two Us, rotate one and put it on top of the other. You can draw an L in the normal way, but a P should consistent of a straight and a U curve. You can change the "teeth" of the comb by changing the `stripes` array, which is an array of start and stop positions. Requires `glyphmonkey`.

## Delete Close Points

Removes short segments, deleting points which are improbably close to other points. Requires `glyphmonkey`.

## Raise ascender

Raises only the points higher than x height.

## Straighten all curves

Deletes all handles (off-curve points) to turn your curves into lines.
