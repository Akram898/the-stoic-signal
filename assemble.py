#!/usr/bin/env python3
# THE STOIC SIGNAL - Shorts assembler
# Usage: python assemble.py s1   |   python assemble.py s2
import os, sys, subprocess, json, math

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTSDIR = "C\\:/Windows/Fonts"  # escaped colon for ffmpeg filtergraph
TAIL = 0.30
OUTRO_TAIL = 0.9
FPS = 30

# All beats are motion clips (stills animated via Grok i2v). VO/captions/SFX pipeline unchanged.
BEATS = {
 "s1": [
  {"src":"clips/s1_b1_eyeignite.mp4","kind":"clip","vo":"../audio/s1_b1.mp3","l1":"THEY THOUGHT SILENCE","l2":"WAS WEAKNESS"},
  {"src":"clips/s1_b2_forum.mp4","kind":"clip","vo":"../audio/s1_b2.mp3","l1":"EVERYONE FOUGHT","l2":"TO BE HEARD"},
  {"src":"clips/s1_b3_balcony.mp4","kind":"clip","vo":"../audio/s1_b3.mp3","l1":"HE SAID","l2":"NOTHING"},
  {"src":"clips/s1_b4_eyes.mp4","kind":"clip","vo":"../audio/s1_b4.mp3","l1":"NOISE   vs.","l2":"CONTROL"},
  {"src":"clips/s1_b5_tablet.mp4","kind":"clip","vo":"../audio/s1_b5.mp3","l1":"TWO EARS.","l2":"ONE MOUTH."},
  {"src":"clips/s1_b6_lightning.mp4","kind":"clip","vo":"../audio/s1_b6.mp3","l1":"SILENCE IS A","l2":"FORTRESS"},
  {"src":"clips/s1_b7_provoker.mp4","kind":"clip","vo":"../audio/s1_b7.mp3","l1":"SAY NOTHING.","l2":"WATCH THEM LOSE"},
  {"src":"clips/s1_b8_marcus.mp4","kind":"clip","vo":"../audio/s1_b8.mp3","l1":"FOLLOW","l2":"THE STOIC SIGNAL"},
 ],
 "s2": [
  {"src":"clips/s2_b1_hourglass.mp4","kind":"clip","vo":"../audio/s2_b1.mp3","l1":"YOU GET ABOUT","l2":"4,000 WEEKS"},
  {"src":"clips/s2_b2_candle.mp4","kind":"clip","vo":"../audio/s2_b2.mp3","l1":"1,000 ARE","l2":"ALREADY GONE"},
  {"src":"clips/s2_b3_phone.mp4","kind":"clip","vo":"../audio/s2_b3.mp3","l1":"1,000 MORE TO","l2":"A SCREEN"},
  {"src":"clips/s2_b4_memento.mp4","kind":"clip","vo":"../audio/s2_b4.mp3","l1":"THE CURE","l2":"MEMENTO MORI"},
  {"src":"clips/s2_b5_skull.mp4","kind":"clip","vo":"../audio/s2_b5.mp3","l1":"REMEMBER YOU","l2":"WILL DIE"},
  {"src":"clips/s2_b6_writing.mp4","kind":"clip","vo":"../audio/s2_b6.mp3","l1":"— TO","l2":"WAKE YOU UP"},
  {"src":"clips/s2_b7_sunrise.mp4","kind":"clip","vo":"../audio/s2_b7.mp3","l1":"WASTE NO","l2":"AFTERNOON"},
  {"src":"clips/s2_b8_marcus.mp4","kind":"clip","vo":"../audio/s2_b8.mp3","l1":"HOW WILL YOU SPEND","l2":"THIS WEEK?"},
 ],
}

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("CMD FAILED:", " ".join(cmd[:6]), "...")
        print(p.stderr[-1500:])
        raise SystemExit(1)
    return p

def probe(path):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(out)

def ass_time(t):
    cs = int(round(t*100))
    h = cs//360000; cs%=360000
    m = cs//6000; cs%=6000
    s = cs//100; cs%=100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

GRADE = "eq=contrast=1.05:saturation=1.07:gamma=0.97,vignette=PI/5"

def build(short):
    beats = BEATS[short]
    sd = "short1" if short=="s1" else "short2"
    os.chdir(os.path.join(ROOT, sd))
    os.makedirs("work", exist_ok=True)
    segs=[]; durs=[]
    for i,b in enumerate(beats):
        vo = probe(b["vo"])
        tail = OUTRO_TAIL if i==len(beats)-1 else TAIL
        seg = vo + tail
        # Clip may be shorter than VO: freeze last frame (tpad) rather than cutting VO
        fr = max(2, int(round(seg*FPS)))
        seg = fr/FPS
        out=f"work/seg_{i}.mp4"
        if b["kind"]=="img":
            drift = "+0.12*on" if i%2==0 else "-0.12*on"
            vf = (f"scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,"
                  f"zoompan=z='min(zoom+0.0009,1.20)':d=1:"
                  f"x='iw/2-(iw/zoom/2){drift}':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={FPS},"
                  f"setsar=1,{GRADE},noise=alls=4:allf=t,format=yuv420p")
            run(["ffmpeg","-y","-v","error","-loop","1","-i",b["src"],"-t",f"{seg:.3f}","-r",str(FPS),
                 "-vf",vf,"-frames:v",str(fr),"-c:v","libx264","-preset","medium","-crf","18","-an",out])
        else:
            vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                  f"setsar=1,{GRADE},noise=alls=3:allf=t,fps={FPS},"
                  f"tpad=stop_mode=clone:stop_duration=8,trim=duration={seg:.3f},setpts=PTS-STARTPTS,"
                  f"format=yuv420p")
            run(["ffmpeg","-y","-v","error","-i",b["src"],
                 "-vf",vf,"-frames:v",str(fr),"-c:v","libx264","-preset","medium","-crf","18","-an",out])
        segs.append(out); durs.append(seg)
        print(f"  beat {i}: {b['kind']:4s} vo={vo:.2f} seg={seg:.2f} -> {out}")

    total = sum(durs)
    # ---- concat video ----
    with open("work/vlist.txt","w") as f:
        for s in segs: f.write(f"file '{os.path.basename(s)}'\n")
    # write list referencing files in work/
    with open("work/vlist.txt","w") as f:
        for i in range(len(segs)): f.write(f"file 'seg_{i}.mp4'\n")
    run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i","work/vlist.txt","-c","copy","work/video.mp4"])

    # ---- per-beat padded audio ----
    alist=[]
    for i,b in enumerate(beats):
        ao=f"work/a_{i}.wav"
        run(["ffmpeg","-y","-v","error","-i",b["vo"],"-af",
             f"apad=whole_dur={durs[i]:.3f},atrim=0:{durs[i]:.3f},asetpts=PTS-STARTPTS,aresample=48000",
             "-ar","48000","-ac","2",ao])
        alist.append(ao)
    with open("work/alist.txt","w") as f:
        for i in range(len(alist)): f.write(f"file 'a_{i}.wav'\n")
    run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i","work/alist.txt","-c","copy","work/vo.wav"])

    # ---- storm drone + rain ambient bed ----
    T=f"{total:.3f}"
    bed_fc=(f"sine=frequency=55:duration={T}[s1];"
            f"sine=frequency=82.41:duration={T}[s2];"
            f"[s1][s2]amix=inputs=2:normalize=0[dr];"
            f"[dr]tremolo=f=0.10:d=0.5,lowpass=f=220[drone];"
            f"anoisesrc=d={T}:color=pink:amplitude=0.6,highpass=f=500,lowpass=f=7000[rn];"
            f"[drone][rn]amix=inputs=2:normalize=0,volume=0.6,aresample=48000[bed]")
    run(["ffmpeg","-y","-v","error","-filter_complex",bed_fc,"-map","[bed]","-t",T,
         "-ar","48000","-ac","2","work/bed.wav"])

    # ---- mix VO + bed ----
    mix_fc=("[0:a]volume=1.0,acompressor=threshold=-18dB:ratio=3:attack=8:release=180[v];"
            "[1:a]volume=0.20[b];"
            "[v][b]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,aresample=48000[mix]")
    run(["ffmpeg","-y","-v","error","-i","work/vo.wav","-i","work/bed.wav",
         "-filter_complex",mix_fc,"-map","[mix]","work/mixed.wav"])

    # ---- captions.ass ----
    header=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Impact,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,5,3,2,70,70,300,1
Style: Mark,Arial Black,30,&H5A3DA3E8,&H5A3DA3E8,&H6E000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,1,8,0,0,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines=[header]
    # persistent watermark
    lines.append(f"Dialogue: 0,{ass_time(0)},{ass_time(total)},Mark,,0,0,0,,THE STOIC SIGNAL")
    t=0.0
    for i,b in enumerate(beats):
        st=t; en=t+durs[i]; t=en
        l1=b["l1"].replace(",","\\,") if False else b["l1"]
        amber="{\\c&H003DA3E8&\\fs104}"
        if b["l1"]:
            txt=f"{l1}\\N{amber}{b['l2']}"
        else:
            txt=f"{amber}{b['l2']}"
        # fade in/out 120ms
        txt="{\\fad(120,90)}"+txt
        lines.append(f"Dialogue: 0,{ass_time(st+0.04)},{ass_time(en)},Cap,,0,0,0,,{txt}")
    with open("captions.ass","w",encoding="utf-8") as f:
        f.write("\n".join(lines)+"\n")

    # ---- final mux: captioned + clean (no-caption) masters from the same work files ----
    base = 'short1' if short=='s1' else 'short2'
    enc = ["-c:v","libx264","-preset","slow","-crf","19","-pix_fmt","yuv420p",
           "-r",str(FPS),"-maxrate","14M","-bufsize","28M","-c:a","aac","-b:a","192k","-shortest"]
    # captioned
    run(["ffmpeg","-y","-v","error","-i","work/video.mp4","-i","work/mixed.wav",
         "-vf","ass=captions.ass","-map","0:v","-map","1:a",*enc,f"../final/{base}.mp4"])
    # no captions (clean graded video + same mix; watermark also omitted)
    run(["ffmpeg","-y","-v","error","-i","work/video.mp4","-i","work/mixed.wav",
         "-map","0:v","-map","1:a",*enc,f"../final/{base}_nocaptions.mp4"])
    print(f"DONE: ../final/{base}.mp4 (+ _nocaptions)  total={total:.2f}s")
    os.chdir(ROOT)

if __name__=="__main__":
    build(sys.argv[1])
