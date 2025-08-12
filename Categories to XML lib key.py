#MenuTitle: Categories to XML lib key
# -*- coding: utf-8 -*-
print("""
    <key>public.openTypeCategories</key>
    <dict>
""")
for g in Glyphs.font.glyphs:
	print(f"      <key>{g.name}</key>")
	if g.category == "Mark":
		print(f"      <string>mark</string>")
	else:
		print(f"      <string>base</string>")
print("    </dict>")
