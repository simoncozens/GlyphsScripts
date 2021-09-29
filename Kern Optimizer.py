font = Glyphs.font
LSBs = {}
RSBs = {}
lkgs = {}
rkgs = {}
glyphs = [x.name for x in font.glyphs]

def _kp(l,r):
  v = font.kerningForPair(font.selectedFontMaster.id, l, r)
  if v > 1000: return 0
  return v

def kp(l,r):
  lkg = lkgs[l]
  rkg = rkgs[l]
  if _kp(l,r): return _kp(l,r)
  if lkg and _kp(lkg, r): return _kp(lkg, r)
  if rkg and _kp(l, rkg): return _kp(l, rkg)
  if lkg and rkg and _kp(lkg, rkg): return _kp(lkg, rkg)
  return 0

matrix = {}
glyphset = []
for l in glyphs:
  # It's backwards
  lkgs[l] = font.glyphs[l].rightKerningGroup and "@MMK_L_"+font.glyphs[l].rightKerningGroup
  rkgs[l] = font.glyphs[l].leftKerningGroup and "@MMK_R_"+font.glyphs[l].leftKerningGroup

  matrix[l] = {}
  LSBs[l] = 0 # XX
  RSBs[l] = 0 # XX
  some = False

  for r in glyphs:
    matrix[l][r] = kp(l,r)
    if matrix[l][r]: some = True
  if some:
    glyphset.append(l)

# For debugging
def displayMatrix():
  print(" [   ] "),
  for r in sorted(glyphset):
    print( " [ "+r+" ]"),
  print("")
  for l in sorted(glyphset):
    print( " [ "+l+" ]"),
    for r in sorted(glyphset):
      print("%6g" % matrix[l][r]),
    print(" ")
  print("Score: %g" % scoreMatrix())

def scoreMatrix():
  score = 0
  for l in glyphset:
    for r in glyphset:
      score += matrix[l][r]**2*10
  return int(score)

def pivotL(l, pivotValue):
  LSBs[l] = LSBs[l] + pivotValue
  for g in glyphset:
    matrix[l][g] -= pivotValue

def pivotR(r, pivotValue):
  RSBs[r] = RSBs[r] + pivotValue
  for g in glyphset:
    matrix[g][r] -= pivotValue

def tryOptimize(l,r):
  pivotValue = matrix[l][r]
  if pivotValue == 0: return False
  s1 = scoreMatrix()
  pivotL(l,pivotValue)
  if scoreMatrix() < s1: return True
  pivotL(l,-pivotValue)
  pivotR(r,pivotValue)
  if scoreMatrix() < s1: return True
  pivotR(r,-pivotValue)
  return False

keepGoing = True

print("Base score was: %g", scoreMatrix())
# print("OPTIMIZING...")
# while keepGoing:
#   s = scoreMatrix()
#   # BRUTE FORCE FOR THE WIN!
#   for l in glyphset:
#     for r in glyphset:
#       tryOptimize(l,r)
#   if s == scoreMatrix():
#     keepGoing = False
# print("Final score was: %g", scoreMatrix())
