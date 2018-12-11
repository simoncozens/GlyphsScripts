#MenuTitle: Autokern
# -*- coding: utf-8 -*-
__doc__="""
Autokerner!
"""

import vanilla
import math
import os
import itertools

failed = []
try:
    from sklearn.cluster import DBSCAN
    from sklearn.metrics.pairwise import euclidean_distances
except Exception, e:
    failed.append("sklearn")

try:
    import numpy as np
except Exception, e:
    failed.append("numpy")

try:
    import requests
except Exception, e:
    failed.append("requests")

try:
    import keras
    from keras import backend as K
except Exception, e:
    failed.append("keras")

testLetters = []

# Uncomment this to limit to a subset
# testLetters = ["H","T", "Tcedilla", "o", "a", "period","A","V"]

batch_size = 1024

windowHeight = 450
windowWidth = 720
samples = 100
url = "http://www.simon-cozens.org/downloads/kernmodel.hdf5"
filename = "kernmodel.hdf5"

# Helper class needed to load model
class WeightedCategoricalCrossEntropy(object):
  def __init__(self, matrix):
    self.weights = matrix
    self.__name__ = 'w_categorical_crossentropy'

  def __call__(self, y_true, y_pred):
    return self.w_categorical_crossentropy(y_true, y_pred)

  def w_categorical_crossentropy(self, y_true, y_pred):
    nb_cl = len(self.weights)
    final_mask = K.zeros_like(y_pred[..., 0])
    y_pred_max = K.max(y_pred, axis=-1)
    y_pred_max = K.expand_dims(y_pred_max, axis=-1)
    y_pred_max_mat = K.equal(y_pred, y_pred_max)
    for c_p, c_t in itertools.product(range(nb_cl), range(nb_cl)):
        w = K.cast(self.weights[c_t, c_p], K.floatx())
        y_p = K.cast(y_pred_max_mat[..., c_p], K.floatx())
        y_t = K.cast(y_true[..., c_t], K.floatx())
        final_mask += w * y_p * y_t
    return K.categorical_crossentropy(y_pred, y_true) * final_mask


class Autokern():
  def __init__(self,lgroups, rgroups, sideBearings):
    self.lgroups = lgroups
    self.rgroups = rgroups
    self.sideBearings = sideBearings
    self.w = vanilla.FloatingWindow( (windowWidth, 130), "Autokerning")
    self.w.text_anchorL = vanilla.TextBox( (10, 10, windowWidth - 10, 25), "", "center")
    self.w.progressBar = vanilla.ProgressBar( (10, 50, windowWidth-20, 10))
    self.w.proceed = vanilla.Button( (windowWidth/2 -50, -50, 100,20), "Kern!", callback = self.kern)
    self.w.open()

  def kern(self,sender):
    self.w.text_anchorL.set("Gathering input tensors...")
    input_tensors = { "pair": [], "rightofl": [], "leftofr": [], "leftofl": [], "rightofr": [], "rightofo": [], "leftofH": [] }

    masterID = Glyphs.font.selectedLayers[0].associatedMasterId
    mwidth = Glyphs.font.glyphs["m"].layers[masterID].width

    def rightcontour(g):
      return np.array(self.sideBearings[g]["right"])/mwidth
    def leftcontour(g):
      return np.array(self.sideBearings[g]["left"])/mwidth
    def bin_to_label(value, mwidth):
      rw = 800
      scale = mwidth/rw
      if value == 0:
        low = int(-150 * scale); high = int(-100 * scale)
      if value == 1:
        low = int(-100 * scale); high = int(-70 * scale)
      if value == 2:
        low = int(-70 * scale); high = int(-50 * scale)
      if value == 3:
        low = int(-50 * scale); high = int(-45 * scale)
      if value == 4:
        low = int(-45 * scale); high = int(-40 * scale)
      if value == 5:
        low = int(-40 * scale); high = int(-35 * scale)
      if value == 6:
        low = int(-35 * scale); high = int(-30 * scale)
      if value == 7:
        low = int(-30 * scale); high = int(-25 * scale)
      if value == 8:
        low = int(-25 * scale); high = int(-20 * scale)
      if value == 9:
        low = int(-20 * scale); high = int(-15 * scale)
      if value == 10:
        low = int(-15 * scale); high = int(-10 * scale)
      if value == 11:
        low = int(-11 * scale); high = int(-5 * scale)
      if value == 12:
        low = int(-5 * scale); high = int(-0 * scale)
      if value == 13:
        return 0
      if value == 14:
        low = int(0 * scale); high = int(5 * scale)
      if value == 15:
        low = int(5 * scale); high = int(10 * scale)
      if value == 16:
        low = int(10 * scale); high = int(15 * scale)
      if value == 17:
        low = int(15 * scale); high = int(20 * scale)
      if value == 18:
        low = int(20 * scale); high = int(25 * scale)
      if value == 19:
        low = int(25 * scale); high = int(30 * scale)
      if value == 20:
        low = int(30 * scale); high = int(50 * scale)
      return int((low+high)/10)*5
    count = 0

    if len(testLetters) > 0:
      self.rgroups = []
      self.lgroups = []
      for l in testLetters:
        self.rgroups.append([l])
        self.lgroups.append([l])

    total = len(self.rgroups)*len(self.lgroups)
    for r in self.rgroups:
      for l in self.lgroups:
        # The first in a group is the exemplar.
        # The last in the group is the group name.
        right = r[0]
        left = l[0]
        input_tensors["pair"].append([ l[-1], r[-1] ])
        input_tensors["rightofl"].append(rightcontour(left))
        input_tensors["leftofr"].append(leftcontour(right))
        input_tensors["rightofr"].append(rightcontour(right))
        input_tensors["leftofl"].append(leftcontour(left))
        input_tensors["rightofo"].append(rightcontour("o"))
        input_tensors["leftofH"].append(leftcontour("H"))
        count = count + 1
        self.w.progressBar.set( 100 * count / total )
    self.w.text_anchorL.set("Enumerating kern pairs (this will take a while)...")
    count = 0
    # Split into batches...
    indices = np.arange(total)
    batches = total / batch_size
    self.w.progressBar.set( 100 * count / total )
    total_pairs = 0

    while count < total:
      bLow = count
      bHigh = count + batch_size
      batch_tensors = {}
      for k in input_tensors.keys():
        batch_tensors[k] = np.array(input_tensors[k][bLow:bHigh])
      predictions = np.array(self.model.predict(batch_tensors))
      classes = np.argmax(predictions, axis=1)
      for pair, prediction in zip(batch_tensors["pair"],classes):
        units = bin_to_label(prediction,mwidth)
        if len(testLetters) > 0:
          print(pair[0],pair[1],units)
        if units != 0:
          total_pairs = total_pairs + 1
          Glyphs.font.setKerningForPair(masterID, pair[0], pair[1], units)
        else:
          Glyphs.font.removeKerningForPair(masterID, pair[0], pair[1])
      count += batch_size
      self.w.progressBar.set( 100 * count / total )
    self.w.text_anchorL.set("We're done. Created %i kern pairs." % total_pairs)
    self.w.proceed.enable(False)

  def go(self):
    print("Loading model")
    self.w.text_anchorL.set("Loading model...")
    weight_matrix = []
    self.model = keras.models.load_model(filename, custom_objects={'w_categorical_crossentropy': WeightedCategoricalCrossEntropy(weight_matrix)}, compile=False)
    self.w.text_anchorL.set("Model loaded. Let's do this. (Close the Kerning window before hitting the button.)")

class ModelDownloader():
  def __init__(self, next):
    self.w = vanilla.FloatingWindow( (windowWidth, 100), "Model Downloader")
    self.w.text_anchorL = vanilla.TextBox( (10, 10, windowWidth - 10, 15), "Downloading latest kerning model", "center")
    self.w.progressBar = vanilla.ProgressBar( (10, windowHeight-30, windowWidth-20, 10))
    self.next = next

  def go(self):
    self.w.open()
    with open(filename, 'wb') as f:
      response = requests.get(url, stream=True)
      total = response.headers.get('content-length')

      if total is None:
          f.write(response.content)
      else:
          downloaded = 0
          total = int(total)
          for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
              downloaded += len(data)
              f.write(data)
              done = 100*downloaded/total
              self.w.progressBar.set( done )
    if done < total:
      self.w.text_anchorL.set("Download failed :(")
      os.remove(filename)
    else:
      self.w.close()
      self.next.go()

def getMargins(layer, y):
  startPoint = NSMakePoint(NSMinX(layer.bounds), y)
  endPoint = NSMakePoint(NSMaxX(layer.bounds), y)

  result = layer.calculateIntersectionsStartPoint_endPoint_(startPoint, endPoint)
  count = len(result)
  if (count <= 2):
    return (None, None)

  left = 1
  right = count - 2
  return (result[left].pointValue().x, result[right].pointValue().x)

# a list of margins

def marginList(layer, steps):
  listL, listR = [], []
  # works over glyph copy
  cleanLayer = layer.copyDecomposedLayer()
  for y in reversed(steps):
    lpos, rpos = getMargins(cleanLayer, y)
    if lpos is not None:
      listL.append(lpos)
    else:
      listL.append(0)
    if rpos is not None:
      listR.append(layer.width-rpos)
    else:
      listR.append(0)

  return listL, listR

class ClusterKernWindow( object ):
  def __init__( self ):
    try:
      self.w = vanilla.FloatingWindow( (windowWidth, windowHeight), "Cluster Kern Groups")
      instructions = "To prepare for kerning, we need to automatically set the kern groups. First we will group your glyphs by their left and right edges. Adjust the sliders to change the grouping tolerance. When the groups look reasonable, press 'Proceed'. Alternatively, you can load your existing kern groups."
      self.w.instr = vanilla.TextBox( (10, 10, windowWidth - 10, 45), instructions, "left", sizeStyle='small')

      self.w.text_anchorL = vanilla.TextBox( (10, 50, windowWidth/2 - 10, 15), "Left Tolerance", "center", sizeStyle='small')
      self.w.lSlider = vanilla.Slider( (10, 60,-(10+windowWidth/2),15),0.01,500, callback = self.buttonPressed)
      self.w.text_anchorR = vanilla.TextBox( (windowWidth/2, 50, windowWidth/2 - 10, 15), "Right Tolerance", "center", sizeStyle='small')
      self.w.rSlider = vanilla.Slider( (10+windowWidth/2,60,-10,15), 0.01, 500, callback = self.buttonPressed)
      self.w.useMine = vanilla.Button( (windowWidth/2 -200, -50, 100,20), "Just Use Mine", callback = self.useMine)
      self.w.calculate = vanilla.Button( (windowWidth/2 -50, -50, 100,20), "Calculate", callback = self.buttonPressed)

      self.w.proceed = vanilla.Button( (-120, -50, 100,20), "Proceed", callback = self.checkModelAndApply)
      self.w.proceed.enable(False)
      self.w.progressBar = vanilla.ProgressBar( (10, windowHeight-20, windowWidth-20, 10))
      self.w.progressBar.set(0)
      self.w.resultsL = vanilla.TextEditor( (10,80, windowWidth/2 - 10, -60) )
      self.w.resultsR = vanilla.TextEditor( (windowWidth/2,80, windowWidth/2 - 10, -60) )
      self.w.open()
      self.lefts = []
      self.rights = []
      self.loadSidebearings()
      self.mineUsed = False
    except Exception, e:
      print(e)

  def loadSidebearings(self):
    if len(self.lefts) == 0:
      if not Glyphs.font.selectedLayers:
        raise "Oops, you need to select a layer!"

      glyphcount = len(Glyphs.font.glyphs)
      masterID = Glyphs.font.selectedLayers[0].associatedMasterId
      master = Glyphs.font.masters[masterID]
      minY = master.descender
      maxY = master.capHeight
      allSteps = list(range(int(minY),int(maxY),1))
      steps = []
      for i in range(samples):
        steps.append(allSteps[int(math.floor(i*len(allSteps) / samples))])
      c = 0
      self.w.progressBar.set(0)
      lefts = []
      rights = []
      self.sideBearings = {}
      self.glyphOrder = []
      glyphSet = Glyphs.font.glyphs
      for a in glyphSet:
        if len(testLetters) > 0:
          if not a.name in testLetters:
            continue
        self.glyphOrder.append(a)
        l = a.layers[masterID]
        c = c + 1
        listL, listR = marginList(l, steps)
        self.lefts.append(listL)
        self.sideBearings[a.name] = { "left": listL, "right": listR }
        self.rights.append(listR)
        self.w.progressBar.set( 100 * c / float(len(glyphSet)) )

  def buttonPressed(self, sender):
    db1 = DBSCAN(eps=self.w.lSlider.get(), min_samples=1).fit(self.lefts)
    db2 = DBSCAN(eps=self.w.rSlider.get(), min_samples=1).fit(self.rights)

    labels = db1.labels_
    groups = []
    for i in range(0,len(set(labels))):
      groups.append([])

    for i in range(0,len(labels)):
      groups[labels[i]].append(self.glyphOrder[i].name)

    lText = ""
    for g in groups:
      if len(g) > 1:
        lText += ", ".join(g) + "\n\n"
        g.append(g[0])
    lText += "Total groups and ungrouped characters: %i" % len(groups)
    self.lgroups = groups
    self.w.resultsL.set(lText)

    labels = db2.labels_
    groups = []
    for i in range(0,len(set(labels))):
      groups.append([])

    for i in range(0,len(labels)):
      groups[labels[i]].append(self.glyphOrder[i].name)

    rText = ""
    for g in groups:
      if len(g) > 1:
        rText += ", ".join(g) + "\n\n"
        g.append(g[0])

    rText += "Total groups and ungrouped characters: %i" % len(groups)
    self.w.resultsR.set(rText)
    self.mineUsed = False
    self.w.proceed.enable(True)
    self.rgroups = groups

    # print(self.lgroups)
    # print(self.rgroups)

  def useMine(self, sender):
    glyphSet = Glyphs.font.glyphs
    lgroupsHash = {}
    rgroupsHash = {}
    for a in glyphSet:
      lk = a.rightKerningKey # *Right* side of glyph when it is on the left of the pair....
      rk = a.leftKerningKey # *Left* side of glyph when it is on the right of the pair....
      if not lk in lgroupsHash:
        lgroupsHash[lk] = []
      if not rk in rgroupsHash:
        rgroupsHash[rk] = []
      lgroupsHash[lk].append(a.name)
      rgroupsHash[rk].append(a.name)
    lText = ""
    rText = ""
    self.lgroups = []
    self.rgroups = []
    for k,v in lgroupsHash.items():
      if len(v) > 1:
        lText += ", ".join(v) + "\n\n"
      v.append(k)
      self.lgroups.append(v)
    for k,v in rgroupsHash.items():
      if len(v) > 1:
        rText += ", ".join(v) + "\n\n"
      v.append(k)
      self.rgroups.append(v)
    lText += "Total groups and ungrouped characters: %i" % len(self.lgroups)
    rText += "Total groups and ungrouped characters: %i" % len(self.rgroups)
    self.w.resultsR.set(rText)
    self.w.resultsL.set(lText)
    # print(self.lgroups)
    # print(self.rgroups)
    self.mineUsed = True
    self.w.proceed.enable(True)

  def checkModelAndApply(self, sender):
    print("Closing window")
    self.w.close()
    if not self.mineUsed:
      # Now we apply the groups given
      for l in self.lgroups:
        glyphs = l[:-1]
        key = l[-1]
        for g in glyphs:
          Glyphs.font.glyphs[g].leftKerningGroup = key
      for r in self.rgroups:
        glyphs = r[:-1]
        key = r[-1]
        for g in glyphs:
          Glyphs.font.glyphs[g].rightKerningGroup = key

    autokern = Autokern(self.lgroups, self.rgroups, self.sideBearings)
    if not os.path.isfile(filename):
      todo = ModelDownloader(next = autokern)
    else:
      todo = autokern
    todo.go()


if len(failed)>0:
    w = vanilla.FloatingWindow( (windowWidth, windowHeight), "Install Required Modules")
    w.text_anchorL = vanilla.TextBox( (10, 10, windowWidth - 10, 15), "The following Python modules need to be installed before this script can run:", "center", sizeStyle='small')
    w.text_anchorR = vanilla.TextBox( (10, 30, windowWidth - 10, 15), ", ".join(failed))
    def closeW(_):
      w.close()
    w.button = vanilla.Button( (windowWidth/2 - 50, -50, 100,20), "OK", callback = closeW)
    w.open()
else:
    ClusterKernWindow()
