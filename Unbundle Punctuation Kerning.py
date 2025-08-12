#MenuTitle: Unbundle Punctuation Kerning
# -*- coding: utf-8 -*-

groups = {}
glyphs = {}
for g in Glyphs.font.glyphs:
	glyphs[g.name] = {}
	if g.rightKerningGroup:
		groups.setdefault("@MMK_L_"+g.rightKerningGroup, []).append(g)
		glyphs[g.name]["left"] = "@MMK_L_"+g.rightKerningGroup
	if g.leftKerningGroup:
		groups.setdefault("@MMK_R_"+g.leftKerningGroup, []).append(g)
		glyphs[g.name]["right"] = "@MMK_R_"+g.leftKerningGroup

glyphs_to_unbundle = [
"parenleft",
"parenright",
"asterisk",
"comma",
"hyphen",
"period",
"slash",
"colon",
"semicolon",
"question",
"bracketleft",
"backslash",
"bracketright",
"underscore",
"braceleft",
"braceright",
"uni2010",
"uni00AD",
"endash",
"emdash",
"quoteleft",
"quoteright",
"quotedblleft",
"quotedblright",
"ellipsis",
"guillemetleft",
"guillemetright",
"guilsinglleft",
"guilsinglright"
"quotedbl",
"quotesingle",
"omega",
"sigmafinal",
"sigma",
"alpha",
"pi",
"Alpha",
"Beta",
"Gamma",
"Delta",
"Epsilon",
"Zeta",
"Eta",
"Theta",
"Iota",
"Kappa",
"Lambda",
"Mu",
"Nu",
"Xi",
"Omicron",
"Pi",
"Rho",
"Sigma",
"Tau",
"Upsilon",
"Phi",
"Chi",
"Psi",
"Omega",
"Digamma",
"ThetaSymbol",
"Alpha.ssty1",
"Beta.ssty1",
"Gamma.ssty1",
"Delta.ssty1",
"Epsilon.ssty1",
"Zeta.ssty1",
"Eta.ssty1",
"Theta.ssty1",
"Iota.ssty1",
"Kappa.ssty1",
"Lambda.ssty1",
"Mu.ssty1",
"Nu.ssty1",
"Xi.ssty1",
"Omicron.ssty1",
"Pi.ssty1",
"Rho.ssty1",
"Sigma.ssty1",
"Tau.ssty1",
"Upsilon.ssty1",
"Phi.ssty1",
"Chi.ssty1",
"Psi.ssty1",
"Omega.ssty1",
"Alpha.ssty2",
"Beta.ssty2",
"Gamma.ssty2",
"Delta.ssty2",
"Epsilon.ssty2",
"Zeta.ssty2",
"Eta.ssty2",
"Theta.ssty2",
"Iota.ssty2",
"Kappa.ssty2",
"Lambda.ssty2",
"Mu.ssty2",
"Nu.ssty2",
"Xi.ssty2",
"Omicron.ssty2",
"Pi.ssty2",
"Rho.ssty2",
"Sigma.ssty2",
"Tau.ssty2",
"Upsilon.ssty2",
"Phi.ssty2",
"Chi.ssty2",
"Psi.ssty2",
"Omega.ssty2",
"alpha",
"beta",
"gamma",
"delta",
"epsilon",
"zeta",
"eta",
"theta",
"iota",
"kappa",
"lambda",
"mu",
"nu",
"xi",
"omicron",
"pi",
"rho",
"sigmafinal",
"sigma",
"tau",
"upsilon",
"phi",
"chi",
"psi",
"omega",
"digamma",
"thetaSymbol",
"phiSymbol",
"piSymbol",
"kappaSymbol",
"rhoSymbol",
"epsilonLunateSymbol",
"alpha.ssty1",
"beta.ssty1",
"gamma.ssty1",
"delta.ssty1",
"epsilon.ssty1",
"zeta.ssty1",
"eta.ssty1",
"theta.ssty1",
"iota.ssty1",
"kappa.ssty1",
"lambda.ssty1",
"mu.ssty1",
"nu.ssty1",
"xi.ssty1",
"omicron.ssty1",
"pi.ssty1",
"rho.ssty1",
"sigmafinal.ssty1",
"sigma.ssty1",
"tau.ssty1",
"upsilon.ssty1",
"phi.ssty1",
"chi.ssty1",
"psi.ssty1",
"omega.ssty1",
"alpha.ssty2",
"beta.ssty2",
"gamma.ssty2",
"delta.ssty2",
"epsilon.ssty2",
"eta.ssty2",
"theta.ssty2",
"iota.ssty2",
"kappa.ssty2",
"lambda.ssty2",
"mu.ssty2",
"nu.ssty2",
"xi.ssty2",
"omicron.ssty2",
"pi.ssty2",
"rho.ssty2",
"sigmafinal.ssty2",
"sigma.ssty2",
"tau.ssty2",
"upsilon.ssty2",
"phi.ssty2",
"chi.ssty2",
"psi.ssty2",
"omega.ssty2",

]
to_delete = []
to_add = []

for glyph_to_unbundle in glyphs_to_unbundle:
	if not Glyphs.font.glyphs[glyph_to_unbundle]:
		continue
	targets = glyphs[glyph_to_unbundle]
	
	for master, kerns in Glyphs.font.kerning.items():
		for left, pairs in kerns.items():
			for right, kern in pairs.items():
				if ("left" in targets and targets["left"] == left) :
					to_delete.append( (master, left, right) )
					for g in groups[left]:
						to_add.append( (master, g.id, right, kern ) )
				if ("right" in targets and targets["right"] == right) :
					to_delete.append( (master, left, right) )
					for g in groups[right]:
						to_add.append( (master, left, g.id, kern ) )
	
	Glyphs.font.glyphs[glyph_to_unbundle].leftKerningGroup = None
	Glyphs.font.glyphs[glyph_to_unbundle].rightKerningGroup = None
	assert Glyphs.font.glyphs[glyph_to_unbundle].leftKerningGroup is None

print(glyph_to_unbundle, Glyphs.font.glyphs[glyph_to_unbundle].leftKerningGroup)

for (master, left, right) in to_delete:
	del Glyphs.font.kerning[master][left][right]

for (master, left, right, kern) in to_add:
	Glyphs.font.kerning[master].setdefault(left, {})[right] = kern
