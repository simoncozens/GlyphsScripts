# MenuTitle: Make compatible
# -*- coding: utf-8 -*-

layers = Glyphs.font.selectedLayers[0].glyph().layers
paths = [l.paths for l in layers]


def lerp(p1, p2, t):
    return NSMakePoint(p1.x + t * (p2.x - p1.x), p1.y + t * (p2.y - p1.y))


for per_paths in zip(*paths):
    segs = [p.segments for p in per_paths]
    to_fix = []
    for seg_set in zip(*segs):
        lengths = [len(seg) for seg in seg_set]
        if all(l == lengths[0] for l in lengths):
            continue
        # Find the ones which are lines
        for ix, seg in enumerate(seg_set):
            if len(seg) == 2:
                fix_object = {"master": ix, "line": [seg[0], seg[1]]}
                # Locate this line by point index
                path_points = per_paths[ix].nodes
                for pt_ix, pt in enumerate(path_points):
                    next_pt = path_points[(pt_ix + 1) % len(path_points)]
                    if (
                        pt.position.x == seg[0].x
                        and pt.position.y == seg[0].y
                        and next_pt.position.x == seg[1].x
                        and next_pt.position.y == seg[1].y
                    ):
                        fix_object["point_index"] = pt_ix
                to_fix.append(fix_object)

    # Sort by line and index, highest index first
    for line in sorted(
        to_fix, key=lambda fix_obj: (fix_obj["master"], -fix_obj["point_index"])
    ):
        nodes = per_paths[line["master"]].nodes
        start_of_line = nodes[line["point_index"]]
        end_of_line = nodes[(line["point_index"] + 1) % len(nodes)]
        new_offcurve_1 = GSNode(lerp(start_of_line, end_of_line, 1 / 3.0), GSOFFCURVE)
        new_offcurve_2 = GSNode(lerp(start_of_line, end_of_line, 2 / 3.0), GSOFFCURVE)
        nodelist = list(nodes)
        nodelist[line["point_index"] + 1 : line["point_index"] + 1] = [
            new_offcurve_1,
            new_offcurve_2,
        ]
        per_paths[line["master"]].nodes = nodelist
        end_of_line.type = GSCURVE
