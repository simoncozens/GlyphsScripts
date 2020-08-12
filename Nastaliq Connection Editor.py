# MenuTitle: Nastaliq Connection Editor
# -*- coding: utf-8 -*-
__doc__ = """
Edit Nastaliq connections in a font that conforms to Qalmi glyph naming
convention
"""
import sys
from AppKit import NSObject
from PyObjCTools import AppHelper
import vanilla
import csv
from io import StringIO
import re
from AppKit import NSView, NSColor, NSRectFill
from vanilla.vanillaBase import VanillaBaseObject, VanillaCallbackWrapper
import traceback


def glyphsort(x):
    x = re.sub(r"(\D)([0-9])$", r"\g<1>0\2", x)
    x = re.sub(r"^GAF", "KAF", x)
    x = re.sub(r"^TE", "BE", x)
    return x


if "GlyphView" not in locals():

    class GlyphView(NSView):
        def setGlyphs(self, glyphs):
            self.glyphs = glyphs
            self.setNeedsDisplay_(True)

        def drawRect_(self, rect):
            try:
                NSColor.whiteColor().set()
                NSRectFill(self.bounds())
                NSColor.blackColor().setFill()
                p = NSBezierPath.bezierPath()
                xcursor = 0
                ycursor = 0
                for i, g in enumerate(self.glyphs):
                    layer = g.layers[0]
                    if i > 0:
                        # Do anchor correction here
                        prevlayer = self.glyphs[i - 1].layers[0]
                        entry = prevlayer.anchors["entry"]
                        exit = layer.anchors["exit"]
                        if entry and exit:
                            diffX = entry.position.x - exit.position.x
                            diffY = entry.position.y - exit.position.y
                            xcursor = xcursor + diffX
                            ycursor = ycursor + diffY
                        else:
                            NSColor.redColor().setFill()
                    else:
                        xcursor = xcursor - layer.bounds.origin.x
                    thisPath = NSBezierPath.bezierPath()
                    thisPath.appendBezierPath_(layer.completeBezierPath)
                    t = NSAffineTransform.transform()
                    t.translateXBy_yBy_(xcursor, -layer.master.descender + ycursor)
                    thisPath.transformUsingAffineTransform_(t)
                    p.appendBezierPath_(thisPath)

                t = NSAffineTransform.transform()
                if xcursor > 0:
                    master = self.glyphs[0].layers[0].master
                    vscale = self.bounds().size.height / (
                        master.ascender - master.descender
                    )
                    hscale = self.bounds().size.width / xcursor
                    t.scaleBy_(min(hscale, vscale))
                    p.transformUsingAffineTransform_(t)
                p.fill()
            except Exception as e:
                print("Oops!", sys.exc_info()[0], "occured.")
                traceback.print_exc(file=sys.stdout)


class NastaliqEditor(object):
    def __init__(self, connections):
        self.connections = connections
        columns = [
            {"title": x, "editable": x != "Left Glyph", "width": 40}
            for x in self.connections["colnames"]
        ]
        columns[0]["width"] = 100
        self.w = vanilla.Window((950, 600), "Nastaliq Editor", closable=True)
        self.w.LeftLabel = vanilla.TextBox((-200, 10, 200, 17), "", alignment="center")
        self.w.LeftButton = vanilla.Button(
            (-200, 30, 30, 17), "<", callback=self.decrement
        )
        self.w.RightLabel = vanilla.TextBox((-170, 30, 140, 17), "", alignment="center")
        self.w.RightButton = vanilla.Button(
            (-30, 30, 30, 17), ">", callback=self.increment
        )
        self.w.myList = vanilla.List(
            (0, 0, -200, -0),
            self.connections["rows"],
            columnDescriptions=columns,
            editCallback=self.editCallback,
            menuCallback=self.menuCallback,
        )
        self.w.myList._clickTarget = VanillaCallbackWrapper(
            self.clickCallback
        )
        self.w.myList._tableView.setTarget_(self.w.myList._clickTarget)
        self.w.myList._tableView.setAction_("action:")

        self.w.CompileButton = vanilla.Button(
            (-200, -20, 200, 17), "Compile", callback=self.compile
        )

        self.glyphView = GlyphView.alloc().init()
        self.glyphView.glyphs = []
        self.glyphView.setFrame_(((0, 0), (400, 400)))
        self.w.scrollView = vanilla.ScrollView((-200, 50, 200, 400), self.glyphView)
        self.selectedPair = None
        self.inAdd = False
        self.w.open()

    def editCallback(self, sender):
        if self.inAdd:
            return
        crow, ccol = self.w.myList.getEditedColumnAndRow()
        newdata = self.w.myList[crow - 1][self.connections["colnames"][ccol + 1]]
        self.setNewPair(crow - 1, ccol + 1, newdata)
        sys.stdout.flush()

    def clickCallback(self, sender):
        crow = self.w.myList._tableView.clickedRow()
        ccol = self.w.myList._tableView.clickedColumn()
        if ccol < 1:
            return
        self.setNewPair(crow, ccol)

    def decrement(self, sender):
        self.add(-1)

    def increment(self, sender):
        self.add(1)

    def add(self, increment):
        if not self.selectedPair:
            return
        crow, ccol = self.selectedPair
        colname = self.connections["colnames"][ccol]
        data = int(self.connections["rows"][crow][colname]) + increment
        if Glyphs.font.glyphs[colname + str(data)]:
            self.inAdd = True
            self.setNewPair(crow, ccol, data)
            newdict = self.w.myList[crow]
            newdict[colname] = data
            self.w.myList[crow] = newdict
            self.inAdd = False
        else:
            print("No glyph", colname + str(data))

    def setNewPair(self, crow, ccol, newdata=None):
        left = self.connections["rows"][crow]["Left Glyph"]
        colname = self.connections["colnames"][ccol]
        if newdata and Glyphs.font.glyphs[colname + str(newdata)]:
            self.connections["rows"][crow][colname] = newdata
            Glyphs.font.userData["nastaliqConnections"] = self.connections
        data = self.connections["rows"][crow][colname]
        self.w.LeftLabel.set(left)
        self.w.RightLabel.set(colname + str(data))
        self.selectedPair = (crow, ccol)

        if Glyphs.font.glyphs[colname + str(data)]:
            leftglyph = Glyphs.font.glyphs[left]
            rightglyph = Glyphs.font.glyphs[colname + str(data)]
            self.glyphView.setGlyphs([leftglyph, rightglyph])
        sys.stdout.flush()

    def menuCallback(self, sender):
        sys.stdout.flush()

    def compile(self, sender):
        rows = Glyphs.font.userData["nastaliqConnections"]["rows"]
        rules = {}

        for line in rows:
            left_glyph = line["Left Glyph"]
            remainder = line.items()
            for (g, v) in remainder:
                if g == "Left Glyph":
                    continue
                old = g + "1"
                if v == "1" or v == 1 or not v:
                    continue
                replacement = g + str(v)
                if not old in rules:
                    rules[old] = {}
                if not replacement in rules[old]:
                    rules[old][replacement] = []
                if left_glyph in Glyphs.font.glyphs:
                    rules[old][replacement].append(left_glyph)
        code = ""
        for oldglyph in rules:
            if oldglyph not in Glyphs.font.glyphs:
                continue
            for replacement in rules[oldglyph]:
                if replacement not in Glyphs.font.glyphs:
                    continue
                context = rules[oldglyph][replacement]
                if len(context) > 1:
                    context = "[ %s ]" % (" ".join(context))
                else:
                    context = context[0]
                code = code + (
                    "rsub %s' %s by %s;\n" % (oldglyph, context, replacement)
                )
        print(code)

        if not Glyphs.font.features["rlig"]:
            Glyphs.font.features["rlig"] = GSFeature("rlig", "")
        Glyphs.font.features["rlig"].code = "lookupflag IgnoreMarks;\n" + code
        Message("rlig feature written", "New feature rules written")


def mergeConnections(new, old):
    # Turn old into a dict
    dOld = {}
    for row in old["rows"]:
        dOld[row["Left Glyph"]] = row
    for row in new["rows"]:
        for col in new["colnames"]:
            if row["Left Glyph"] in dOld and col in dOld[row["Left Glyph"]]:
                row[col] = dOld[row["Left Glyph"]][col]


def kickoff():
    # Check we have a font open and it's Qalmi-like
    if not Glyphs.font:
        Message("No font open", "Open a font")
        return

    connectables = [
        x.name for x in Glyphs.font.glyphs if re.match(r".*[mif][0-9]+$", x.name)
    ]
    medials = [x for x in connectables if re.match(r".*m[0-9]+$", x)]
    initials = [x for x in connectables if re.match(r".*i[0-9]+$", x)]
    finals = [x for x in connectables if re.match(r".*f[0-9]+$", x)]
    medialstems = sorted(set([re.sub("[0-9]+$", "", x) for x in medials]))
    initialstems = sorted(set([re.sub("[0-9]+$", "", x) for x in initials]))

    if len(medials) == 0:
        Message(
            "Bad glyph name convention",
            "Glyph names must conform to Qalmi convention: RASM{m,i,u,f}number",
        )
        return

    connections = {}

    connections["colnames"] = ["Left Glyph"]
    connections["colnames"].extend(medialstems)
    connections["colnames"].extend(initialstems)
    # Setup dummy data
    connections["rows"] = []
    for row in sorted(medials, key=glyphsort):
        connections["rows"].append({colname: 1 for colname in connections["colnames"]})
        connections["rows"][-1]["Left Glyph"] = row
    for row in sorted(finals, key=glyphsort):
        connections["rows"].append({colname: 1 for colname in connections["colnames"]})
        connections["rows"][-1]["Left Glyph"] = row

    # Do we have some connection data already?
    if Glyphs.font.userData["nastaliqConnections"]:
        mergeConnections(connections, Glyphs.font.userData["nastaliqConnections"])
    w = NastaliqEditor(connections)


try:
    kickoff()
except Exception as e:
    print("Oops!", sys.exc_info()[0], "occured.")
    traceback.print_exc(file=sys.stdout)
