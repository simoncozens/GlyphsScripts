#MenuTitle: AutoCursiveAttachment - Add Anchors
# -*- coding: utf-8 -*-
__doc__="""
Automatic attachment generation
"""
import GlyphsApp
from Foundation import NSPoint, NSValue, NSMinY, NSMaxY, NSMinX, NSMaxX
from itertools import tee
import math

def shouldHaveExit(Layer):
    # This is ugly and should use Unicode properties
    n = str(Layer.parent.name)
    return "ini" in n.lower() or "med" in n.lower()

def shouldHaveEntry(Layer):
    n = str(Layer.parent.name)
    return "fin" in n.lower() or "med" in n.lower()

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def calcTangent(t,segment):
    # calculates reference Tangent Point (from its coordinates plugin will be able to get tangent's direction)
    if len(segment) == 4: # for curves
        divided = divideCurve(segment[0], segment[1], segment[2], segment[3], t)
        R2 = divided[4]
    elif len(segment) == 2: # for line
        R2 = segment[1]
    Tangent = NSPoint(R2.x,R2.y)
    return Tangent

def angle( A, B ):
    try:
        """calc angle between AB and Xaxis """
        xDiff = A.x - B.x
        yDiff = A.y - B.y
        if yDiff== 0 or xDiff== 0:
            tangens = 0
        else:
            tangens = yDiff / xDiff

        angle = math.atan( tangens )
        return angle
    except:
        print(traceback.format_exc())

def clonePath(path):
    p2 = path.copy()
    p2.convertToCubic()
    return p2

def calcClosestInfo(layer, pt):
    closestPoint = None
    closestPath = None
    closestPathTime = None
    dist = 100000
    for path in layer.paths:
        path = clonePath(path)
        currClosestPoint, currPathTime = path.nearestPointOnPath_pathTime_(pt, None)
        currDist = distance(currClosestPoint, pt)
        if currDist < dist:
            dist = currDist
            closestPoint = currClosestPoint
            closestPathTime = currPathTime
            closestPath = path
    if closestPathTime is None:
        return None
    n = math.floor(closestPathTime)
    OnNode = closestPath.nodes[n]
    if not OnNode:
        return None
    if OnNode.type == CURVE:
        segment = (closestPath.nodes[n - 3].position, closestPath.nodes[n - 2].position, closestPath.nodes[n - 1].position, OnNode.position)
    else:
        prevPoint = closestPath.nodes[n - 1]
        if prevPoint:
            segment = (prevPoint.position, OnNode.position)
        else:
            return

    TangentDirection = calcTangent(closestPathTime % 1, segment)
    directionAngle = angle(closestPoint,TangentDirection)

    if TangentDirection.x == segment[0].x: # eliminates problem with vertical lines ###UGLY?
        directionAngle = -math.pi/2

    yTanDistance = math.sin(directionAngle)
    xTanDistance = math.cos(directionAngle)
    closestPointTangent = NSPoint(xTanDistance+closestPoint.x,yTanDistance+closestPoint.y)

    return {
        "onCurve": closestPoint,
        "pathTime": closestPathTime,
        "path": closestPath,
        "segment": segment,
        "directionAngle": directionAngle
    }

def mysqdistance(p1,p2):
    return (p1.x-p2.x)*(p1.x-p2.x) + (p1.y-p2.y)*(p1.y-p2.y)
def lerp(t,a,b):
  return NSValue.valueWithPoint_(NSPoint(int((1-t)*a.x + t*b.x), int((1-t)*a.y + t*b.y)))

Layer = Glyphs.font.selectedLayers[0]

if not Layer.master.customParameters["autocursiveattachment_distbelow"]:
    Message("No sample found", "Run 'Get Sample' script first")

# Do entry anchor
distbelow = Layer.master.customParameters["autocursiveattachment_distbelow"]
distabove = Layer.master.customParameters["autocursiveattachment_distabove"]
targetDistance = distbelow + distabove
prop = distbelow / targetDistance

def doTrial(anchor, x):
    startPoint = NSMakePoint(x, NSMinY(Layer.bounds))
    endPoint = NSMakePoint(x, NSMaxY(Layer.bounds))
    result = Layer.calculateIntersectionsStartPoint_endPoint_(startPoint, endPoint)
    if len(result) <= 2:
        return None, None
    result = result[1:3] # Generally speaking it will be the lowest
    # Except jeem. Urgh.
    for r in pairwise(result):
        distance = r[1].y - r[0].y
        if distance < 10 or distance > 500:
            continue
        result = r
        break
    if distance < 10 or distance > 500:
        return None, None
    bottomClosest = calcClosestInfo(Layer, NSMakePoint(result[0].x, result[0].y))
    bt = bottomClosest["directionAngle"]
    tt = calcClosestInfo(Layer, NSMakePoint(result[1].x, result[1].y))["directionAngle"]
    # if anchor == "exit":
    #     bt = bt
    #     tt = - tt
    score = (distance - targetDistance)**2
    print("Square distance diff", score)
    tangentScore = 10
    print("Top tangent was: ", tt)
    print("Expected top tangent was: ", Layer.master.customParameters["autocursiveattachment_topTangent"])
    print("Bottom tangent was: ", bt)
    print("Expected bottom tangent was: ", Layer.master.customParameters["autocursiveattachment_bottomTangent"])

    tangentContribution = ( tangentScore*(bt-Layer.master.customParameters["autocursiveattachment_bottomTangent"])) ** 2 + (tangentScore*(tt-Layer.master.customParameters["autocursiveattachment_topTangent"])) ** 2
    print("Tangent contribution to score", tangentContribution)
    score = score + tangentContribution
    # if anchor == "exit":
    #     score = score + x**2
    # else:
    #     score = score + (Layer.width-x)**2
    placement = NSMakePoint(x, prop * result[0].y + (1-prop) * (result[1].y))
    return score, placement


if shouldHaveExit(Layer) and not "exit" in Layer.anchors:
    bestScore = 99999
    bestPoint = None
    for potX in range(int(NSMinX(Layer.bounds)),100):
        score, placement = doTrial("exit",potX)
        if score:
            print("Score for %i is %f" % (potX, score))
            if score < bestScore:
                bestScore = score
                bestPoint = placement
    Layer.anchors['exit'] = GSAnchor("exit")
    Layer.anchors["exit"].position = bestPoint

if shouldHaveEntry(Layer) and not "entry" in Layer.anchors:
    bestScore = 99999
    bestPoint = None
    for potX in range(int(NSMaxX(Layer.bounds)+100),int(NSMaxX(Layer.bounds))-100, -1):
        score, placement = doTrial("entry",potX)
        if score:
            print("Score for %i is %f" % (potX, score))
            if score < bestScore:
                bestScore = score
                bestPoint = placement
    Layer.anchors['entry'] = GSAnchor("entry")
    Layer.anchors["entry"].position = bestPoint

