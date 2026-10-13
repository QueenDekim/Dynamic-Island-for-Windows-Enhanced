#!/usr/bin/env python3
"""Deterministic synthetic, offline documentation previews for Enhanced.

This deliberately doesn't impersonate screenshots: README labels them as
synthetic mockups. Layout, proportions and palette emulate the real Windhawk
UI. Input is fixed, no private app data, network, login or live sessions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2
BG = "#0B0910"
SURFACE = "#18141F"
EDGE = "#3A3148"
TEXT = "#F5F1FA"
MUTED = "#ACA4B9"
DIM = "#766F83"
PURPLE = "#8877F8"
DISCORD = "#5865F2"
BLUE = "#46B6D8"
GREEN = "#5ED9A5"
RED = "#EF5C7F"
GOLD = "#EAB66F"
random.seed(100)

def rgb(v):
    v=v.lstrip("#")
    return tuple(int(v[i:i+2],16) for i in (0,2,4))

def fontpath(bold=False):
    for p in (
        Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ):
        if p.is_file():
            return str(p)
    raise RuntimeError("Install Segoe UI (Windows) or DejaVu Sans to render previews.")

FONT_CACHE = {}
def ft(size, bold=False):
    key=(size,bold)
    if key not in FONT_CACHE:
        FONT_CACHE[key]=ImageFont.truetype(fontpath(bold),round(size*S))
    return FONT_CACHE[key]

class Art:
    def __init__(self, w=760, h=254, bg=BG):
        self.w,self.h=w,h
        self.im=Image.new("RGB",(w*S,h*S),rgb(bg))
        self.d=ImageDraw.Draw(self.im)

    def xy(self,bounds):
        return [round(v*S) for v in bounds]

    def rr(self,rect,r=12,fill=SURFACE,outline=None,width=1):
        self.d.rounded_rectangle(self.xy(rect),round(r*S),fill=fill,
                                 outline=outline,width=round(width*S))

    def circ(self,x,y,r,color,outline=None,width=1):
        self.d.ellipse(self.xy((x-r,y-r,x+r,y+r)),fill=color,
                       outline=outline,width=round(width*S))

    def line(self,points,color,width=2):
        self.d.line([(round(x*S),round(y*S)) for x,y in points],
                    fill=color,width=round(width*S),joint="curve")

    def txt(self,x,y,text,size=14,color=TEXT,bold=False,anchor="lt"):
        self.d.text((round(x*S),round(y*S)),str(text),font=ft(size,bold),
                    fill=color,anchor=anchor,stroke_width=0)

    def pill(self,x,y,w,h,r=18):
        self.rr((x,y,x+w,y+h),r,SURFACE,EDGE,1)

    def icon(self,x,y,kind,size=38,color=PURPLE):
        self.rr((x,y,x+size,y+size),max(8,size//3),color)
        cx,cy=x+size/2,y+size/2
        if kind=="music":
            self.txt(cx,cy+1,"♫",size*0.64,"#FFFFFF",True,"mm")
        elif kind=="discord":
            self.circ(cx-7,cy,3.8,"#FFFFFF")
            self.circ(cx+7,cy,3.8,"#FFFFFF")
            self.line([(cx-12,cy+6),(cx,cy+10),(cx+12,cy+6)],"#FFFFFF",2.5)
        elif kind=="cpu":
            self.txt(cx,cy,"%",size*0.44,"#FFFFFF",True,"mm")
        elif kind=="clock":
            self.circ(cx,cy,12,"#FFFFFF")
            self.circ(cx,cy,9,color)
            self.line([(cx,cy),(cx,cy-6),(cx+5,cy-3)],"#FFFFFF",2)
        elif kind=="weather":
            self.circ(cx-4,cy-2,9,"#FFFFFF")
            self.circ(cx+8,cy+3,7,"#FFFFFF")
        elif kind=="alert":
            self.txt(cx,cy,"!",size*0.54,"#FFFFFF",True,"mm")
        elif kind=="bluetooth":
            self.txt(cx,cy,"ᛒ",size*0.65,"#FFFFFF",True,"mm")
        elif kind=="file":
            self.txt(cx,cy,"▤",size*0.63,"#FFFFFF",True,"mm")
        else:
            self.txt(cx,cy,"●",size*0.45,"#FFFFFF",True,"mm")

    def bars(self,x,y,count=10,step=7,maxh=26,color=PURPLE,phase=0.0):
        for i in range(count):
            height=4+maxh*(0.14+0.86*abs(math.sin(i*1.43+phase)))
            self.rr((x+i*step,y-height/2,x+i*step+3,y+height/2),1.5,color)

    def cover(self,x,y,size=45,variant=0):
        colors=[("#3F4E75","#D28AA8"),("#255C68","#5AC2CB"),
                ("#413268","#B8A0D8"),("#4B5866","#9CB9C0")]
        a,b=colors[variant%len(colors)]
        self.rr((x,y,x+size,y+size),size*0.28,a)
        for i in range(4):
            self.line([(x+3,y+size*(0.2+i*0.19)),
                       (x+size*(.6+i*.05),y+size*(.05+i*.16)),
                       (x+size*.9,y+size*(.5+i*.13))],b,1.6)

    def save(self,path):
        path.parent.mkdir(parents=True,exist_ok=True)
        self.im.resize((self.w,self.h),Image.Resampling.LANCZOS).save(path,optimize=True)

def frame(title,w=760,h=254,card_width=600,card_height=126):
    a=Art(w,h)
    a.txt(30,20,title.upper(),11,DIM,True)
    x=(w-card_width)/2
    y=(h-card_height)/2+8
    a.pill(x,y,card_width,card_height,18)
    return a,x,y,card_width,card_height

def linebar(a,x,y,w,ratio=0.52,color=PURPLE):
    a.rr((x,y,x+w,y+3),1.5,"#36303E")
    a.rr((x,y,x+max(3,w*ratio),y+3),1.5,color)

def small_metric(a,x,y,label,value,color=BLUE,w=95):
    a.rr((x,y,x+w,y+70),10,"#25202D")
    a.txt(x+12,y+10,label.upper(),10,MUTED,True)
    a.txt(x+12,y+30,str(value),23,TEXT,True)
    a.rr((x+12,y+61,x+w-12,y+64),2,"#36303F")
    a.rr((x+12,y+61,x+12+(w-24)*.60,y+64),2,color)

def draw(scene):
    if scene=="desktop":
        a=Art(1000,520,"#111623")
        for y in range(520):
            f=y/520
            a.d.line([(0,y*S),(1000*S,y*S)],fill=(int(13+23*f),int(17+18*f),int(31+39*f)),width=S)
        for i in range(14):
            x=35+i*77
            a.circ(x,320+18*math.sin(i*.6),105,"#26243D")
        a.pill(270,32,460,66,19)
        a.cover(285,42,46,0)
        a.txt(348,50,"1:19/2:24",14,TEXT,True)
        a.bars(485,66,8,6,22)
        a.line([(564,45),(564,83)],"#41394D",1)
        a.icon(582,45,"discord",35,DISCORD)
        a.txt(630,46,"CAPTAIN MORIS",12,TEXT,True)
        a.txt(630,64,"Voice · 24:13",10,MUTED)
        a.bars(840,66,8,6,18,BLUE,1.5)
        a.txt(40,452,"SYNTHETIC DESKTOP PREVIEW",12,"#CDD4E5",True)
        return a
    if scene=="themes":
        a=Art(900,310)
        palettes=[("OBSIDIAN",SURFACE,PURPLE),("NORD","#202935","#82A8C2"),
                  ("EVERGREEN","#1D302B","#62CE92"),("PLUM","#312036","#B886DB"),
                  ("PORCELAIN","#E8E4EA","#5865F2"),("GRAPHITE","#24262C","#8B94A0")]
        for i,(name,surface,accent) in enumerate(palettes):
            x=34+(i%3)*283
            y=53+(i//3)*130
            a.txt(x+8,y-20,name,11,MUTED,True)
            a.rr((x,y,x+262,y+92),23,surface,"#514757")
            a.circ(x+31,y+46,18,accent)
            a.txt(x+66,y+37,"Dynamic Island",16,"#191824" if name=="PORCELAIN" else TEXT,True)
            a.bars(x+202,y+48,6,7,20,accent)
        return a

    if scene in {"media-v2","compact-media","discord-voice-compact"}:
        a,x,y,w,h=frame("Media • Collapsed" if scene!="discord-voice-compact" else
                         "Voice • Collapsed",card_width=500 if scene!="discord-voice-compact" else 690,card_height=72)
        a.cover(x+11,y+11,50,0)
        a.txt(x+81,y+36,"0:19/2:24",16,TEXT,False,"lm")
        a.bars(x+302,y+37,10,7,20,PURPLE)
        if scene=="discord-voice-compact":
            a.line([(x+435,y+14),(x+435,y+58)],EDGE,2)
            a.icon(x+447,y+17,"discord",39,DISCORD)
            a.txt(x+500,y+28,"24:13",13,TEXT,True)
            a.bars(x+575,y+37,9,7,15,BLUE,.8)
        return a

    a,x,y,w,h=frame(scene.replace("-"," "),card_width=620,
                    card_height=136 if scene not in {"idle-v2","camera-detected-v2","mic-detected-v2"} else 100)
    mid=y+h/2

    if scene in {"discord-voice","discord-signed-out"}:
        a.icon(x+24,y+22,"discord",52,DISCORD)
        a.txt(x+93,y+23,"Discord",17,TEXT,True)
        if scene=="discord-voice":
            a.txt(x+93,y+47,"Northwind  •  General Voice",13,MUTED)
            a.txt(x+93,y+78,"CAPTAIN MORIS  •  24:13",12,TEXT,True)
            for j,color in enumerate([BLUE,PURPLE,GREEN,GOLD]):
                a.circ(x+310+j*28,y+93,13,color)
            a.bars(x+510,y+94,10,6,22,BLUE,.9)
        else:
            a.txt(x+93,y+50,"Sign in to connect voice and notifications",12,MUTED)
            a.rr((x+w-143,y+76,x+w-22,y+118),10,DISCORD)
            a.txt(x+w-82.5,y+97,"Log in",14,TEXT,True,"mm")
        return a

    if scene in {"idle-v2","clock","focus-clock"}:
        a.txt(x+34,mid-33,"WEDNESDAY",13,MUTED,True)
        a.txt(x+32,mid-10,"10:24",43,TEXT,True)
        a.txt(x+220,mid+8,"14 October 2026",15,MUTED)
        a.circ(x+w-35,y+27,4,GREEN)
        return a

    if scene=="calendar":
        a.txt(x+27,y+19,"OCTOBER 2026",15,TEXT,True)
        a.txt(x+30,y+51,"M  T  W  T  F  S  S",15,MUTED)
        for row in range(2):
            for col in range(7):
                i=row*7+col+12
                px=x+32+col*35
                py=y+75+row*27
                if i==14:a.circ(px+7,py+8,13,PURPLE)
                a.txt(px,py,str(i),13,TEXT,True)
        a.txt(x+360,y+44,"Today",13,MUTED)
        a.txt(x+358,y+62,"Wednesday, 14 October",19,TEXT,True)
        a.txt(x+358,y+95,"2 events scheduled",12,MUTED)
        return a

    if scene=="weather-v2":
        a.icon(x+22,y+27,"weather",66,BLUE)
        a.txt(x+109,y+20,"AMSTERDAM",12,MUTED,True)
        a.txt(x+108,y+40,"18°C",39,TEXT,True)
        a.txt(x+107,y+97,"Partly cloudy",13,MUTED)
        small_metric(a,x+400,y+34,"Humidity","62%",BLUE,94)
        small_metric(a,x+504,y+34,"Wind","14",GREEN,92)
        return a

    if scene=="gamebar-v2":
        small_metric(a,x+18,y+32,"FPS",144,PURPLE,110)
        for j,(label,val,color) in enumerate([("CPU","42%",BLUE),("GPU","67%",PURPLE),
                                               ("RAM","14G",GREEN),("DISK","12%",GOLD)]):
            small_metric(a,x+141+j*114,y+32,label,val,color,102)
        return a

    if scene=="hardware-monitor":
        for j,(label,val,color) in enumerate([("CPU", "27%",BLUE),("GPU","58%",PURPLE),
                                               ("RAM","17 GB",GREEN),("SSD","19%",GOLD)]):
            small_metric(a,x+25+j*145,y+31,label,val,color,128)
        return a

    if scene in {"camera-detected-v2","mic-detected-v2"}:
        a.txt(x+35,y+34,"Privacy",16,TEXT,True)
        a.txt(x+35,y+61,"Camera active" if scene.startswith("camera") else
              "Microphone active",13,MUTED)
        a.circ(x+w-48,y+50,9,GREEN if scene.startswith("camera") else GOLD)
        return a

    if scene in {"discord-notification","notification","clipboard"}:
        a.icon(x+20,y+32,"discord" if scene.startswith("discord") else "alert",
               55,DISCORD if scene.startswith("discord") else PURPLE)
        a.txt(x+94,y+21,"Discord · CAPTAIN MORIS" if scene.startswith("discord") else
              ("Clipboard" if scene=="clipboard" else "Notifications"),
              14,MUTED,True)
        a.txt(x+94,y+53,
              "Are you joining voice tonight?" if scene.startswith("discord") else
              ("New text copied to clipboard" if scene=="clipboard" else
               "Your download is ready"),17,TEXT,True)
        linebar(a,x+95,y+112,w-120,.55,BLUE)
        return a

    if scene in {"volume","brightness"}:
        a.icon(x+23,y+29,"music" if scene=="volume" else "weather",58,BLUE)
        a.txt(x+101,y+27,"SYSTEM VOLUME" if scene=="volume" else "DISPLAY BRIGHTNESS",
              13,MUTED,True)
        a.txt(x+101,y+53,"72%" if scene=="volume" else "68%",24,TEXT,True)
        linebar(a,x+225,y+83,325,.72 if scene=="volume" else .68,BLUE)
        return a

    if scene in {"caps-lock","num-lock"}:
        a.icon(x+23,y+28,"alert",60,PURPLE)
        a.txt(x+105,y+32,"Caps Lock" if scene=="caps-lock" else "Num Lock",19,TEXT,True)
        a.txt(x+105,y+69,"Enabled",15,GREEN)
        a.circ(x+w-42,mid,7,GREEN)
        return a

    if scene in {"device","bluetooth","battery-low","usb"}:
        a.icon(x+24,y+27,"bluetooth" if scene=="bluetooth" else "file",59,BLUE)
        names={"device":"New device connected","bluetooth":"Bluetooth connected",
               "battery-low":"Battery low · 15%","usb":"USB storage connected"}
        a.txt(x+102,y+28,names[scene],20,TEXT,True)
        a.txt(x+102,y+66,"Wireless headphones" if scene=="bluetooth" else
              "Windows device status",13,MUTED)
        linebar(a,x+102,y+113,w-130,.25 if scene=="battery-low" else .65,
                RED if scene=="battery-low" else GREEN)
        return a

    if scene in {"timer","focus-timer"}:
        a.icon(x+25,y+29,"clock",58,PURPLE)
        a.txt(x+104,y+28,"FOCUS TIMER" if scene=="focus-timer" else "TIMER",13,MUTED,True)
        a.txt(x+102,y+48,"18:32",30,TEXT,True)
        linebar(a,x+280,y+83,290,.55,PURPLE)
        return a

    if scene=="progress":
        a.icon(x+22,y+32,"file",55,BLUE)
        a.txt(x+95,y+25,"Downloading update",17,TEXT,True)
        a.txt(x+95,y+55,"67% complete",13,MUTED)
        linebar(a,x+95,y+104,475,.67,BLUE)
        return a

    if scene=="dnd":
        a.icon(x+25,y+31,"alert",56,PURPLE)
        a.txt(x+98,y+35,"Do Not Disturb",19,TEXT,True)
        a.txt(x+99,y+72,"Notifications silenced",13,MUTED)
        return a

    if scene=="file-tray":
        a.txt(x+28,y+18,"FILE TRAY",13,MUTED,True)
        for i,(name,size) in enumerate([("project-notes.md","8 KB"),
                                         ("presentation.pptx","2.3 MB"),
                                         ("design-reference.png","726 KB")]):
            yy=y+42+i*28
            a.rr((x+26,yy,x+w-28,yy+23),5,"#251E30")
            a.txt(x+39,yy+2,name,12,TEXT)
            a.txt(x+w-86,yy+2,size,11,MUTED)
        return a

    if scene=="lyrics":
        a.cover(x+28,y+28,70,2)
        a.txt(x+125,y+31,"Yellow",14,MUTED,True)
        a.txt(x+124,y+58,"We were made for this moment",20,TEXT,True)
        linebar(a,x+124,y+108,w-154,.71,PURPLE)
        return a

    raise ValueError("Unknown preview scenario "+scene)


SCENES=[
    "desktop","media-v2","calendar","weather-v2","gamebar-v2","idle-v2",
    "hardware-monitor","themes","camera-detected-v2","mic-detected-v2",
    "compact-media","discord-voice-compact","discord-voice","discord-signed-out",
    "discord-notification","notification","clipboard","volume","brightness",
    "caps-lock","num-lock","device","bluetooth","battery-low","usb",
    "timer","focus-timer","progress","dnd","file-tray","lyrics"
]

KIND_PREVIEWS={
    "Idle":"idle-v2",
    "Media":"media-v2",
    "Progress":"progress",
    "Clipboard":"clipboard",
    "Notification":"notification",
    "Volume":"volume",
    "BatteryLow":"battery-low",
    "CapsLock":"caps-lock",
    "Device":"device",
    "Bluetooth":"bluetooth",
    "Timer":"timer",
    "DoNotDisturb":"dnd",
    "Discord":"discord-voice",
    "Split":"discord-voice-compact",
}

def montage(paths,out):
    cards=[Image.open(p).convert("RGB") for p in paths]
    width=1012
    head=75
    cellw=486
    cellh=235
    rows=math.ceil(len(cards)/2)
    canvas=Art(width,head+rows*cellh+25)
    canvas.txt(36,20,"DYNAMIC ISLAND / ENHANCED",27,TEXT,True)
    canvas.txt(38,56,"Synthetic interface previews · October 2026",11,MUTED)
    for i,(pic,path) in enumerate(zip(cards,paths)):
        x=16+(i%2)*(cellw+10)
        y=head+(i//2)*cellh
        frame=pic.resize((cellw*S,200*S),Image.Resampling.LANCZOS)
        canvas.im.paste(frame,(x*S,y*S))
        canvas.txt(x+18,y+202,path.stem.replace("-"," ").upper(),11,MUTED,True)
    canvas.save(out)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parents[1]/"previews")
    args=parser.parse_args()
    output=args.output
    output.mkdir(parents=True,exist_ok=True)
    expected={"Full-preview-v2.png","preview-manifest.json"}.union(
        {name+".png" for name in SCENES})
    for existing in output.glob("*.png"):
        if existing.name not in expected:existing.unlink()
    for scene in SCENES:
        draw(scene).save(output/(scene+".png"))
    featured=["media-v2","calendar","weather-v2","gamebar-v2","idle-v2",
              "discord-voice","hardware-monitor","discord-notification"]
    montage([output/(s+".png") for s in featured],output/"Full-preview-v2.png")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.glob("*.png"))}
    (output/"preview-manifest.json").write_text(json.dumps({
       "type":"synthetic preview illustrations (not live Windhawk screenshots)",
       "source":"scripts/render_previews.py",
       "rendered_scenarios": SCENES,
       "island_kinds":KIND_PREVIEWS,
       "files_sha256":hashes
    },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"PREVIEWS_OK images={len(hashes)} directory={output}")

if __name__=="__main__":
    main()
