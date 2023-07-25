from glyphsLib import GSFont, GSGlyph, GSComponent, load, GSLayer, GSPath
from glyphsLib.types import Transform
import sys
from statistics import mean

import argparse

parser = argparse.ArgumentParser(description="Componentize a Glyphs file")
parser.add_argument(
    "--full-matrix",
    choices=["identity", "translation", "uniform-scale", "free"],
    dest="full_matrix",
    default="uniform-scale",
    help="Allowable matrices for replacing a full glyph",
)
parser.add_argument(
    "--partial-matrix",
    choices=["identity", "translation", "uniform-scale", "free"],
    dest="partial_matrix",
    default="uniform-scale",
    help="Allowable matrices for replacing a set of paths",
)
parser.add_argument("--output", metavar="GLYPHS", help="Output glyphs file")
parser.add_argument("input", metavar="GLYPHS", help="Glyphs file to componentize")
args = parser.parse_args()
if not args.output:
    args.output = args.input.replace(".glyphs", "-componentized.glyphs")

try:
    import tqdm

    progress = tqdm.tqdm
except ModuleNotFoundError:

    def progress(iterator, **kwargs):
        return iterator


def square_error(a, b):
    return (a - b) ** 2


def linear_regression(xs, ys):
    mean_x = mean(xs)
    mean_y = mean(ys)
    numer = 0
    denom = 0
    for x, y in zip(xs, ys):
        numer += (x - mean_x) * (y - mean_y)
        denom += (x - mean_x) ** 2
    m = numer / denom
    c = mean_y - (m * mean_x)

    # Check residuals
    def y_pred(x):
        return x * m + c

    t_x = mean(square_error(y_pred(x), y_true) for x, y_true in zip(xs, ys))

    return m, c, t_x


try:
    import numpy as np

    def linear_regression(xs, ys):
        x = np.array(xs)
        y = np.array(ys)
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        y_pred = x * m + c
        return m, c, np.mean((y_pred - y) ** 2)

except ModuleNotFoundError:
    pass


def matrix_ok(matrix, compatibility):
    if compatibility == "identity":
        return matrix == (1, 0, 0, 1, 0, 0)
    if compatibility == "translation":
        return tuple(matrix[0:4]) == (1, 0, 0, 1)
    if compatibility == "uniform-scale":
        return matrix[0] == matrix[3]
    return True


def GSLayer_is_fully_compatible(self, other):
    if self.components or other.components:
        return None
    if len(self.paths) != len(other.paths):
        return None
    if sum(len(x.nodes) for x in self.paths) < 8:
        # Don't bother merging
        return None

    # First check for equality
    my_compatible_paths = {}
    their_compatible_paths = {}
    for p1i, p1 in enumerate(self.paths):
        for p2i, p2 in enumerate(other.paths):
            matrix = p1.is_equal(p2)
            if matrix:
                my_compatible_paths[p1i] = (p2i, matrix)
                their_compatible_paths[p2i] = (p1i, matrix)

    if len(my_compatible_paths) == len(self.paths) and len(
        their_compatible_paths
    ) == len(other.paths):
        return (1, 0, 0, 1, 0, 0)

    my_compatible_paths = {}
    their_compatible_paths = {}
    last_matrix = None
    for p1i, p1 in enumerate(self.paths):
        for p2i, p2 in enumerate(other.paths):
            matrix = p1.is_compatible(p2)
            if matrix:
                my_compatible_paths[p1i] = (p2i, matrix)
                their_compatible_paths[p2i] = (p1i, matrix)
                if last_matrix and last_matrix != matrix:
                    return None
                last_matrix = matrix
                break
    if len(my_compatible_paths) != len(self.paths):
        return None
    if len(their_compatible_paths) != len(other.paths):
        return None
    return last_matrix


GSLayer.is_fully_compatible = GSLayer_is_fully_compatible


def GSLayer_replace_with(self, other, matrix):
    self.paths = []
    self.components = [GSComponent(other.name, transform=Transform(*matrix))]


GSLayer.replace_with = GSLayer_replace_with


def GSGlyph_replace_subset(self, other, matrices, shape_indices, reverse):
    masters = self.parent.masters
    for master, matrix in zip(masters, matrices):
        if reverse:
            matrix = (1 / matrix[0], 0, 0, 1 / matrix[3], -matrix[4], -matrix[5])
            if any(abs(matrix[0]) >= 2 or abs(matrix[3]) >= 2 for matrix in matrices):
                return
        for p in shape_indices:
            if reverse:
                his_shape, my_shape = p
            else:
                my_shape, his_shape = p
            layer = self.layers[master.id]
            layer.shapes[my_shape] = GSComponent(
                other.name, transform=Transform(*matrix)
            )


GSGlyph.replace_subset = GSGlyph_replace_subset

# @dataclass
# class Path:
#     coords: GlyphCoordinates
#     signature: bytearray
#     parent: Glyph
#     index: int

#     def __post_init__(self):
#         x1, y1 = zip(*self.coords)
#         self.x_coords = np.array(x1)
#         self.y_coords = np.array(y1)


def GSPath_is_equal(self, other):
    if len(self.nodes) != len(other.nodes):
        return None
    coords = [n.position for n in self.nodes]
    other_coords = [n.position for n in other.nodes]
    for i in range(len(self.nodes)):
        if (other_coords[i:] + other_coords[:i]) == coords:
            return (1, 0, 0, 1, 0, 0)
    return False


GSPath.is_equal = GSPath_is_equal

GSPath.signature = lambda self: [n.type for n in self.nodes]
GSPath.index = lambda self: self.parent.paths.index(self)
GSPath.shape_index = lambda self: self.parent.shapes.index(self)


def GSPath_is_compatible(self, other):
    if self.signature() != other.signature():
        return None
    self_x_coords = [n.position.x for n in self.nodes]
    self_y_coords = [n.position.y for n in self.nodes]
    other_x_coords = [n.position.x for n in other.nodes]
    other_y_coords = [n.position.y for n in other.nodes]

    if other_x_coords == self_x_coords and other_y_coords == self_y_coords:
        return (1, 0, 0, 1, 0, 0)

    diffs = sum(
        [square_error(my, their) for my, their in zip(self_x_coords, other_x_coords)]
    )
    diffs += sum(
        [square_error(my, their) for my, their in zip(self_y_coords, other_y_coords)]
    )
    if diffs / len(self.nodes) < 50:
        # It's a pure translation
        mean_x = mean(my - their for my, their in zip(self_x_coords, other_x_coords))
        mean_y = mean(my - their for my, their in zip(self_y_coords, other_y_coords))
        return (1, 0, 0, 1, -mean_x, -mean_y)

    slope1, intercept1, residual_x = linear_regression(self_x_coords, other_x_coords)
    if residual_x > 10:
        return None
    slope2, intercept2, residual_y = linear_regression(self_y_coords, other_y_coords)
    if residual_y > 10:
        return None

    return (
        round(slope1 * 1000) / 1000,
        0,
        0,
        round(slope2 * 1000) / 1000,
        int(intercept1),
        int(intercept2),
    )


GSPath.is_compatible = GSPath_is_compatible


def GSPath_is_compatible_in_all_masters(self, other, compatibility):
    font = self.parent.parent.parent
    matrices = []
    g1 = self.parent.parent
    g2 = other.parent.parent
    for master in font.masters:
        l1 = g1.layers[master.id]
        l2 = g2.layers[master.id]
        p1 = l1.paths[self.index()]
        p2 = l2.paths[other.index()]
        matrix = p1.is_compatible(p2)
        if not matrix or not matrix_ok(matrix, compatibility):
            return None
        matrices.append(matrix)
    return matrices


GSPath.is_compatible_in_all_masters = GSPath_is_compatible_in_all_masters


def build_paths_by_sig(glyphs):
    paths_by_sig = {}
    for glyph in glyphs.values():
        layer = glyph.layers[0]
        for p in layer.paths:
            paths_by_sig.setdefault(tuple(p.signature()), []).append(p)

    to_strip = []
    for sig, paths in paths_by_sig.items():
        if len(paths) < 2 or len(sig) <= 4:
            to_strip.append(sig)
    for sig in to_strip:
        del paths_by_sig[sig]
    return paths_by_sig


font = load(args.input)
masters = [x.id for x in font.masters]

edited = set()

sharable_paths = {}

print("Searching for exact componentable glyphs")
glyphlist: list[GSGlyph] = list(font.glyphs)
for ix, g1 in progress(enumerate(glyphlist), total=len(glyphlist)):
    for g2 in glyphlist[ix + 1 :]:
        matrices = []
        for master in masters:
            l1 = g1.layers[master]
            if not l1.paths:
                continue
            l2 = g2.layers[master]
            if not l2.paths:
                continue
            matrix = l2.is_fully_compatible(l1)
            if matrix and matrix_ok(matrix, args.full_matrix):
                matrices.append((l2, l1, matrix))
            else:
                break
        if len(matrices) == len(masters):
            print(
                "Replacing %s with %s"
                % (matrices[0][0].parent.name, matrices[0][1].parent.name)
            )
            for l1, l2, matrix in matrices:
                l2.replace_with(l1, matrix)
                edited.add(l2)
        elif len(matrices) > len(masters) / 2:
            print(
                "%s was compatible with %s in %i masters; not replacing, check manually"
                % (
                    matrices[0][0].parent.name,
                    matrices[0][1].parent.name,
                    len(matrices),
                )
            )

paths_by_sig = build_paths_by_sig(font.glyphs)
print("Searching for partially componentable glyphs")
mergelist = {}

for pathlists in progress(paths_by_sig.values()):
    for i, path1 in enumerate(pathlists):
        for path2 in pathlists[i + 1 :]:
            if path1.parent == path2.parent:
                continue
            matrices = path1.is_compatible_in_all_masters(path2, args.partial_matrix)
            if matrices:
                mergelist.setdefault(
                    (path1.parent.parent.name, path2.parent.parent.name), []
                ).append([path1.shape_index(), path2.shape_index(), matrices])

for g1, g2 in mergelist.keys():
    if g1 in edited or g2 in edited:
        continue
    paths = mergelist[(g1, g2)]
    marked_left = set()
    marked_right = set()
    # Find the largest subset of identical matrix
    by_matrix = {}
    for p1, p2, matrix in paths:
        by_matrix.setdefault(tuple(matrix), []).append((p1, p2))
    for matrices, path_indices in sorted(by_matrix.items(), key=lambda k: -len(k[1])):
        if len(path_indices) == len(font.glyphs[g1].layers[0].shapes):
            print(f"{g2} contains {g1}")
            font.glyphs[g2].replace_subset(
                font.glyphs[g1], matrices, path_indices, True
            )
        elif len(path_indices) == len(font.glyphs[g2].layers[0].shapes):
            print(f"{g1} contains {g2}")
            font.glyphs[g1].replace_subset(
                font.glyphs[g2], matrices, path_indices, False
            )

font.save(args.output)
