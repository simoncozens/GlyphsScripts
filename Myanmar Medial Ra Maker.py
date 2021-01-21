#MenuTitle: Myanmar Medial Ra Maker
# -*- coding: utf-8 -*-
import GlyphsApp
import numpy as np

number_of_glyphs = 5

def mean(it):
    return sum(it)/len(it)

def roundto(x,y):
    return int(x/y)*y

def ssq(j, i, sum_x, sum_x_sq):
    if (j > 0):
        muji = (sum_x[i] - sum_x[j-1]) / (i - j + 1)
        sji = sum_x_sq[i] - sum_x_sq[j-1] - (i - j + 1) * muji ** 2
    else:
        sji = sum_x_sq[i] - sum_x[i] ** 2 / (i+1)

    return 0 if sji < 0 else sji

def fill_row_k(imin, imax, k, S, J, sum_x, sum_x_sq, N):
    if imin > imax: return

    i = (imin+imax) // 2
    S[k][i] = S[k-1][i-1]
    J[k][i] = i

    jlow = k

    if imin > k:
        jlow = int(max(jlow, J[k][imin-1]))
    jlow = int(max(jlow, J[k-1][i]))

    jhigh = i-1
    if imax < N-1:
        jhigh = int(min(jhigh, J[k][imax+1]))

    for j in range(jhigh, jlow-1, -1):
        sji = ssq(j, i, sum_x, sum_x_sq)

        if sji + S[k-1][jlow-1] >= S[k][i]: break

        # Examine the lower bound of the cluster border
        # compute s(jlow, i)
        sjlowi = ssq(jlow, i, sum_x, sum_x_sq)

        SSQ_jlow = sjlowi + S[k-1][jlow-1]

        if SSQ_jlow < S[k][i]:
            S[k][i] = SSQ_jlow
            J[k][i] = jlow

        jlow += 1

        SSQ_j = sji + S[k-1][j-1]
        if SSQ_j < S[k][i]:
            S[k][i] = SSQ_j
            J[k][i] = j

    fill_row_k(imin, i-1, k, S, J, sum_x, sum_x_sq, N)
    fill_row_k(i+1, imax, k, S, J, sum_x, sum_x_sq, N)

def fill_dp_matrix(data, S, J, K, N):
    sum_x = np.zeros(N, dtype=np.float_)
    sum_x_sq = np.zeros(N, dtype=np.float_)

    # median. used to shift the values of x to improve numerical stability
    shift = data[N//2]

    for i in range(N):
        if i == 0:
            sum_x[0] = data[0] - shift
            sum_x_sq[0] = (data[0] - shift) ** 2
        else:
            sum_x[i] = sum_x[i-1] + data[i] - shift
            sum_x_sq[i] = sum_x_sq[i-1] + (data[i] - shift) ** 2

        S[0][i] = ssq(0, i, sum_x, sum_x_sq)
        J[0][i] = 0

    for k in range(1, K):
        if (k < K-1):
            imin = max(1, k)
        else:
            imin = N-1

        fill_row_k(imin, N-1, k, S, J, sum_x, sum_x_sq, N)

def ckmeans(data, n_clusters):
    if n_clusters <= 0:
        raise ValueError("Cannot classify into 0 or less clusters")
    if n_clusters > len(data):
        raise ValueError("Cannot generate more classes than there are data values")

    # if there's only one value, return it; there's no sensible way to split
    # it. This means that len(ckmeans([data], 2)) may not == 2. Is that OK?
    unique = len(set(data))
    if unique == 1:
        return [data]

    data.sort()
    n = len(data)

    S = np.zeros((n_clusters, n), dtype=np.float_)

    J = np.zeros((n_clusters, n), dtype=np.uint64)

    fill_dp_matrix(data, S, J, n_clusters, n)

    clusters = []
    cluster_right = n-1

    for cluster in range(n_clusters-1, -1, -1):
        cluster_left = int(J[cluster][cluster_right])
        clusters.append(data[cluster_left:cluster_right+1])

        if cluster > 0:
            cluster_right = cluster_left - 1

    return list(reversed(clusters))

def stem_width(path):
    segs = [s for s in path.segments if len(s) == 2 and s[0].x == s[1].x]
    segs = sorted(segs, key=lambda s: abs(s[0].y-s[1].y))
    return abs(segs[-1][0].x - segs[-2][0].x)

ra = Glyphs.font.glyphs["103C"].layers[0]
if len(ra.paths) != 5:
	print("Medial ra glyph needs five paths")

stem, top, upper_hook, bottom, lower_hook = ra.paths
ra_enclosure = ra.bounds.size.width - (stem_width(stem) + stem_width(lower_hook)) + 2 * ra.LSB

widths = {}

def copypath(path, translate=0, stretchleft=0, stretchright=0):
    newpath = GSPath()
    for n in path.nodes:
        newnode = GSNode(NSMakePoint(n.position.x+translate,n.position.y), n.type)
        newnode.smooth = n.smooth
        newpath.nodes.append(newnode)
    newpath.closed = True
    if stretchleft:
        nodes = newpath.nodes
        nodes[0].position = NSMakePoint(nodes[0].position.x - stretchleft, nodes[0].position.y)
        nodes[-1].position = NSMakePoint(nodes[-1].position.x - stretchleft, nodes[-1].position.y)
    if stretchright:
        nodes = newpath.nodes
        nodes[0].position = NSMakePoint(nodes[0].position.x + stretchright, nodes[0].position.y)
        nodes[-1].position = NSMakePoint(nodes[-1].position.x + stretchright, nodes[-1].position.y)
    return newpath

print(ra_enclosure)
widths = []
for i in range(0x1000, 0x1021): # Yes I know there are more
	if not Glyphs.font.glyphs["%04X" % i]:
		continue
	widths.append( Glyphs.font.glyphs["%04X" % i].layers[0].width )

target_widths = [roundto(mean(x),10) for x in ckmeans(widths, number_of_glyphs)]

def make_a_ra(basename, width):
    g = Glyphs.font.glyphs[basename]
    if not g:
        g = GSGlyph(basename)
        newLayer = GSLayer()
        newLayer.associatedMasterId = Glyphs.font.masters[-1].id
        Glyphs.font.glyphs[basename] = g
        g.layers.append(newLayer)
    l = g.layers[0]
    extension = width-ra_enclosure
    l.paths.append(stem)
    if not (basename.endswith(".notop")):
        l.paths.append(copypath(top, stretchright=extension/2))
    if not (basename.endswith(".notophook")) and not (basename.endswith(".notop")):
        l.paths.append(copypath(upper_hook, stretchleft=extension/2,translate=extension))
    if not (basename.endswith(".nobottom")):
        l.paths.append(copypath(bottom, stretchright=extension/2))
    if not basename.endswith(".nobottomhook") and not (basename.endswith(".nobottom")):
        l.paths.append(copypath(lower_hook, stretchleft=extension/2,translate=extension))
    l.LSB = ra.LSB
    l.RSB = ra.RSB - extension

for width in target_widths:
    if width <= ra_enclosure:
        continue
    print("Making a ra of width: %i" % width)
    basename = "medial-ra.w%i" % width
    make_a_ra(basename, width)
    make_a_ra(basename+".notop", width)
    make_a_ra(basename+".notophook", width)
    make_a_ra(basename+".nobottom", width)
    make_a_ra(basename+".nobottomhook", width)

make_a_ra("medial-ra.notop", ra_enclosure)
make_a_ra("medial-ra.notophook", ra_enclosure)
make_a_ra("medial-ra.nobottom", ra_enclosure)
make_a_ra("medial-ra.nobottomhook", ra_enclosure)

