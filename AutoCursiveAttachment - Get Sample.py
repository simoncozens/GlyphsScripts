#MenuTitle: AutoCursiveAttachment - Get Sample
# -*- coding: utf-8 -*-
__doc__="""
Get information from a sample anchor for automatic attachment generation
"""
import GlyphsApp
from Foundation import NSPoint, NSValue, NSMinY, NSMaxY
from itertools import tee
import math

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
inout = list(filter(lambda x: x.name == "entry" or x.name=="exit", Layer.anchors))
if not inout:
  Message("No anchors found", "Create an entry or exit anchor to use this script")

distabove = 0
distbelow = 0
bottomTangent = 0
topTangent = 0

for anchor in inout:
  startPoint = NSMakePoint(anchor.x, NSMinY(Layer.bounds))
  endPoint = NSMakePoint(anchor.x, NSMaxY(Layer.bounds))
  result = Layer.calculateIntersectionsStartPoint_endPoint_(startPoint, endPoint)
  if len(result) <= 2:
    Message("No paths found", "Anchor needs to be within a path")
  result = sorted(list(set(result[1:-1])), key= lambda p:p.y)
  # Remove repeated results
  print("Result was", result)
  selected = min(pairwise(result), key=lambda x: mysqdistance(anchor.position, x[0])+mysqdistance(anchor.position, x[1]))
  print("Selected" , selected)
  distabove = distabove + abs(max([p.y - anchor.y for p in selected]))
  distbelow = distbelow + abs(max([anchor.y - p.y for p in selected]))
  bottomClosest = calcClosestInfo(Layer, NSMakePoint(selected[0].x, selected[0].y))
  print(bottomClosest)
  bt = bottomClosest["directionAngle"]
  tt = calcClosestInfo(Layer, NSMakePoint(selected[1].x, selected[1].y))["directionAngle"]
  # if anchor.name == "exit":
    # bt = -bt
    # tt = - tt
  print("TT %s angle = %f" %(anchor.name, tt))
  print("BT %s angle = %f" %(anchor.name, bt))
  bottomTangent = bottomTangent + bt
  topTangent = topTangent + tt

topTangent = topTangent / len(inout)

Layer.master.customParameters["autocursiveattachment_distbelow"] = distbelow / len(inout)
Layer.master.customParameters["autocursiveattachment_distabove"] = distabove / len(inout)
Layer.master.customParameters["autocursiveattachment_bottomTangent"] = bottomTangent / len(inout)
Layer.master.customParameters["autocursiveattachment_topTangent"] = topTangent / len(inout)
Message("Sample taken", "Now use 'add anchors'")
