#MenuTitle: Why You Not Compatible?
# -*- coding: utf-8 -*-
__doc__="""
Finds compatibility issues in the selected glyphs
"""

Font = Glyphs.font

def checkALayer(aLayer):
  differences = []
  pathCounts = []
  anchors = []
  paths = []
  for idx, thisLayer in enumerate(aLayer.parent.layers):
    pcount = len(thisLayer.paths)
    if idx > 0:
      if pcount != pathCounts[-1]:
        differences.append({"type": "path counts",
          "prevLayer": Font.selectedLayers[0].parent.layers[idx-1].name,
          "thisLayer": thisLayer.name,
          "prevItem": pathCounts[-1],
          "thisItem": pcount
        })
    pathCounts.append(pcount)

    if len(differences) == 0: # If path counts differ all bets are off
      for pathIdx, path in enumerate(thisLayer.paths):
        if idx >0:
          if len(path.nodes) != len(paths[idx-1][pathIdx].nodes):
            differences.append({"type": "path "+str(1+pathIdx)+", node count",
              "prevLayer": Font.selectedLayers[0].parent.layers[idx-1].name,
              "thisLayer": thisLayer.name,
              "prevItem": len(paths[idx-1][pathIdx].nodes),
              "thisItem": len(path.nodes)
            })
          else:
            for nodeIdx, node in enumerate(path.nodes):
              prevNode = paths[idx-1][pathIdx].nodes[nodeIdx]
              if node.type != prevNode.type:
                differences.append({"type": "path "+str(1+pathIdx)+", node "+str(1+nodeIdx)+ " node types",
                  "prevLayer": Font.selectedLayers[0].parent.layers[idx-1].name,
                  "thisLayer": thisLayer.name,
                  "prevItem": prevNode.type,
                  "thisItem": node.type
                  })
      paths.append(thisLayer.paths)

    thisAnchors = set(thisLayer.anchors.keys())
    if len(anchors) > 0:
      diff = thisAnchors.symmetric_difference(anchors[-1])
      if len(diff) > 0:
        differences.append({"type": "anchors",
          "prevLayer": Font.selectedLayers[0].parent.layers[idx-1].name,
          "thisLayer": thisLayer.name,
          "thisItem": ", ".join(thisAnchors),
          "prevItem": ", ".join(anchors[-1])
        })
    anchors.append(thisAnchors)

  if len(differences) == 0:
    print(thisLayer.parent.name + " is compatible")
  else:
    print(thisLayer.parent.name + " is not compatible")
    for diff in differences:
      print(diff["type"]+" differ:")
      print("  "+diff["prevLayer"] + " has "+str(diff["prevItem"]))
      print("  "+diff["thisLayer"] + " has "+str(diff["thisItem"]))

for aLayer in Font.selectedLayers:
  checkALayer(aLayer)
  print("\n")