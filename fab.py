#!/usr/bin/env python3
# Generate Gerbers + Excellon drill for JLCPCB from ereader.kicad_pcb.
# Re-run AFTER routing: python3 fab.py
import os, sys, zipfile, pcbnew
HERE=os.path.dirname(os.path.abspath(__file__))
PCB=os.path.join(HERE,"ereader.kicad_pcb")
OUT=os.path.join(HERE,"gerbers")
os.makedirs(OUT,exist_ok=True)
b=pcbnew.LoadBoard(PCB)
pc=pcbnew.PLOT_CONTROLLER(b); po=pc.GetPlotOptions()
po.SetOutputDirectory(OUT)
po.SetPlotFrameRef(False); po.SetAutoScale(False); po.SetScale(1); po.SetMirror(False)
po.SetUseGerberProtelExtensions(False)
po.SetUseGerberX2format(True); po.SetUseGerberAttributes(True)
po.SetIncludeGerberNetlistInfo(True); po.SetCreateGerberJobFile(True)
po.SetSubtractMaskFromSilk(True)
try: po.SetDrillMarksType(pcbnew.DRILL_MARKS_NO_DRILL_SHAPE)
except Exception:
    try: po.SetDrillMarksType(0)
    except Exception: pass
L=[(pcbnew.F_Cu,"F_Cu"),(pcbnew.In1_Cu,"In1_Cu"),(pcbnew.In2_Cu,"In2_Cu"),(pcbnew.B_Cu,"B_Cu"),
   (pcbnew.F_Paste,"F_Paste"),(pcbnew.B_Paste,"B_Paste"),
   (pcbnew.F_SilkS,"F_Silkscreen"),(pcbnew.B_SilkS,"B_Silkscreen"),
   (pcbnew.F_Mask,"F_Mask"),(pcbnew.B_Mask,"B_Mask"),(pcbnew.Edge_Cuts,"Edge_Cuts")]
for lid,name in L:
    pc.SetLayer(lid); pc.OpenPlotfile(name,pcbnew.PLOT_FORMAT_GERBER,name); pc.PlotLayer()
pc.ClosePlot()
# drill (Excellon) + map
drl=pcbnew.EXCELLON_WRITER(b)
drl.SetOptions(False,False,pcbnew.VECTOR2I(0,0),False)
drl.SetFormat(True)   # metric
drl.CreateDrillandMapFilesSet(OUT,True,False)
files=sorted(os.listdir(OUT))
zf=os.path.join(HERE,"ereader-gerbers.zip")
with zipfile.ZipFile(zf,"w",zipfile.ZIP_DEFLATED) as z:
    for f in files: z.write(os.path.join(OUT,f),f)
print("layers/files:",len(files)); print("\n".join(files)); print("zip:",zf)
