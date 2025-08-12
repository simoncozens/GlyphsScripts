for cl in Glyphs.font.classes:
  glyphs = cl.code.split()
  existing = [g for g in glyphs if Glyphs.font.glyphs[g]]
  if glyphs != existing:
    cl.code = " ".join(existing)
