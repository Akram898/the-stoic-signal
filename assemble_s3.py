#!/usr/bin/env python3
"""Assemble Short 3 — VO + low SFX + dual masters (modern captions / clean).

Outputs:
  final/short3.mp4            — publish: modern karaoke captions + watermark + SFX
  final/short3_nocaptions.mp4 — always kept: graded picture + VO + SFX, no burn-in text
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SD = os.path.join(ROOT, "short3")
SFX_DIR = os.path.join(ROOT, "sound_effects")
RAIN = os.path.join(SFX_DIR, "Light Rain.mp3")
THUNDER = os.path.join(SFX_DIR, "Distant Thunder.mp3")

TAIL = 0.30
OUTRO_TAIL = 0.9
FPS = 30
GRADE = "eq=contrast=1.05:saturation=1.07:gamma=0.97,vignette=PI/5"

# Rain/thunder under VO (louder bed; still under voice)
RAIN_VOL = 0.28
THUNDER_VOL = 0.38

BEATS = [
    {
        "src": "clips/s3_b1_remote.mp4",
        "vo": "audio/s3_b1.mp3",
        "l1": "YOUR ANGER IS",
        "l2": "THEIR REMOTE",
        "words": "Your anger is their remote control.",
        "thunder": True,  # hook hit
    },
    {
        "src": "clips/s3_b2_insult.mp4",
        "vo": "audio/s3_b2.mp3",
        "l1": "ONE INSULT.",
        "l2": "YOU HAND POWER",
        "words": "One insult. One glance. And you hand them the power.",
        "thunder": False,
    },
    {
        "src": "clips/s3_b3_study.mp4",
        "vo": "audio/s3_b3.mp3",
        "l1": "ANGER IS A",
        "l2": "SHORT MADNESS",
        "words": "Seneca warned: anger is a short madness.",
        "thunder": False,
    },
    {
        "src": "clips/s3_b4_burn.mp4",
        "vo": "audio/s3_b4.mp3",
        "l1": "YOU BURN.",
        "l2": "THEY WIN",
        "words": "While you burn, they stay cold and win.",
        "thunder": True,
    },
    {
        "src": "clips/s3_b5_eyes.mp4",
        "vo": "audio/s3_b5.mp3",
        "l1": "PAUSE BEFORE",
        "l2": "THE REACTION",
        "words": "The Stoic move: pause before the reaction.",
        "thunder": False,
    },
    {
        "src": "clips/s3_b6_clock.mp4",
        "vo": "audio/s3_b6.mp3",
        "l1": "MASTER THE",
        "l2": "FIRST SECOND",
        "words": "Master the first second or it masters you.",
        "thunder": False,
    },
    {
        "src": "clips/s3_b7_throne.mp4",
        "vo": "audio/s3_b7.mp3",
        "l1": "SMILE. KEEP",
        "l2": "YOUR THRONE",
        "words": "Next time they poke, smile, and keep your throne.",
        "thunder": True,
    },
    {
        "src": "clips/s3_b8_logo.mp4",
        "vo": "audio/s3_b8.mp3",
        "l1": "FOLLOW",
        "l2": "THE STOIC SIGNAL",
        "words": "The Stoic Signal.",
        "thunder": False,
    },
]


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("CMD FAILED:", " ".join(str(c) for c in cmd[:10]), "...")
        print(p.stderr[-2500:])
        raise SystemExit(1)
    return p


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def ass_time(t):
    cs = int(round(max(0.0, t) * 100))
    h = cs // 360000
    cs %= 360000
    m = cs // 6000
    cs %= 6000
    s = cs // 100
    cs %= 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def tokenize(text):
    # Keep words; drop empty after stripping punctuation for display uppercase
    parts = re.findall(r"[A-Za-z0-9']+|[.,:;!?]", text)
    words = [p for p in parts if re.match(r"[A-Za-z0-9']", p)]
    return [w.upper() for w in words]


def karaoke_line(words, vo_dur, pad_tail=0.05):
    """ASS karaoke: active word pops amber (SecondaryColour), rest white."""
    if not words:
        return ""
    usable = max(0.35, vo_dur - pad_tail)
    # {\kN} unit = centiseconds
    total_cs = max(len(words), int(round(usable * 100)))
    base = total_cs // len(words)
    rem = total_cs - base * len(words)
    chunks = []
    for i, w in enumerate(words):
        k = base + (1 if i < rem else 0)
        chunks.append(rf"{{\k{k}}}{w}")
    return " ".join(chunks)


def build_modern_ass(durs, total):
    """TikTok/OpenMontage-style word karaoke + brand watermark + beat keyword punch."""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Arial Black,72,&H00FFFFFF,&H003DA3E8,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,2,2,50,50,420,1
Style: Punch,Impact,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,2,0,1,6,3,2,60,60,280,1
Style: Mark,Arial Black,28,&H5A3DA3E8,&H5A3DA3E8,&H6E000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,1,8,0,0,56,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    lines.append(f"Dialogue: 0,{ass_time(0)},{ass_time(total)},Mark,,0,0,0,,THE STOIC SIGNAL")
    t = 0.0
    for i, b in enumerate(BEATS):
        st = t
        en = t + durs[i]
        t = en
        vo = probe(os.path.join(SD, b["vo"])) if not os.path.isabs(b["vo"]) else probe(b["vo"])
        # re-probe from short3 cwd context — main() chdirs
        words = tokenize(b["words"])
        # Karaoke follows VO length inside the beat
        k_end = min(en, st + vo + 0.08)
        kar = karaoke_line(words, vo)
        # Soft fade in + karaoke highlight (SecondaryColour = amber)
        lines.append(
            f"Dialogue: 1,{ass_time(st + 0.03)},{ass_time(k_end)},Word,,0,0,0,,"
            rf"{{\fad(80,60)\bord5\shad2}}{kar}"
        )
        # Keyword punch on L2 (amber) for first ~1.1s of beat — modern hook style
        punch_en = min(en, st + min(1.35, durs[i] * 0.45))
        amber = r"{\c&H003DA3E8&\fs100}"
        punch = rf"{{\fad(60,120)\fscx108\fscy108\t(0,180,\fscx100\fscy100)}}{b['l1']}\N{amber}{b['l2']}"
        lines.append(
            f"Dialogue: 2,{ass_time(st + 0.02)},{ass_time(punch_en)},Punch,,0,0,0,,{punch}"
        )
    return "\n".join(lines) + "\n"


def mix_audio(vo_path, total, durs, out_path):
    """VO + looped light rain (low) + thunder hits on selected beats (low)."""
    if not os.path.isfile(RAIN) or not os.path.isfile(THUNDER):
        print("WARNING: SFX missing — VO only")
        run([
            "ffmpeg", "-y", "-v", "error", "-i", vo_path,
            "-af", "acompressor=threshold=-18dB:ratio=3:attack=8:release=180,alimiter=limit=0.95",
            "-ar", "48000", "-ac", "2", out_path,
        ])
        return

    # Build thunder chain: trim short hits, delay to beat starts
    # inputs: 0=vo, 1=rain loop, 2=thunder source
    thunder_starts = []
    t = 0.0
    for i, b in enumerate(BEATS):
        if b.get("thunder"):
            thunder_starts.append(t)
        t += durs[i]

    T = f"{total:.3f}"
    fade_out_st = max(0.0, total - 1.2)
    parts = [
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{T},asetpts=PTS-STARTPTS,"
        f"volume={RAIN_VOL},afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_st:.3f}:d=1.0[rain]",
        "[0:a]volume=1.05,acompressor=threshold=-18dB:ratio=3:attack=8:release=180[vo]",
    ]
    th_labels = []
    for j, start in enumerate(thunder_starts):
        delay_ms = int(round(start * 1000))
        lab = f"th{j}"
        parts.append(
            f"[2:a]atrim=0:2.8,asetpts=PTS-STARTPTS,volume={THUNDER_VOL},"
            f"afade=t=in:d=0.05,afade=t=out:st=2.2:d=0.55,"
            f"adelay={delay_ms}|{delay_ms}[{lab}]"
        )
        th_labels.append(f"[{lab}]")

    n_mix = 2 + len(th_labels)
    amix_inputs = "[vo][rain]" + "".join(th_labels)
    parts.append(
        f"{amix_inputs}amix=inputs={n_mix}:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.95,aresample=48000[mix]"
    )
    fc = ";".join(parts)

    run([
        "ffmpeg", "-y", "-v", "error",
        "-i", vo_path,
        "-stream_loop", "-1", "-i", RAIN,
        "-i", THUNDER,
        "-filter_complex", fc,
        "-map", "[mix]", "-t", T, "-ar", "48000", "-ac", "2", out_path,
    ])
    print(f"  mix: rain@{RAIN_VOL} thunder@{THUNDER_VOL} hits={thunder_starts}")


def main():
    os.chdir(SD)
    os.makedirs("work", exist_ok=True)
    os.makedirs(os.path.join(ROOT, "final"), exist_ok=True)
    segs, durs = [], []

    for i, b in enumerate(BEATS):
        vo = probe(b["vo"])
        tail = OUTRO_TAIL if i == len(BEATS) - 1 else TAIL
        seg = vo + tail
        fr = max(2, int(round(seg * FPS)))
        seg = fr / FPS
        out = f"work/seg_{i}.mp4"
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"setsar=1,{GRADE},noise=alls=3:allf=t,fps={FPS},"
            f"tpad=stop_mode=clone:stop_duration=8,trim=duration={seg:.3f},setpts=PTS-STARTPTS,"
            f"format=yuv420p"
        )
        run([
            "ffmpeg", "-y", "-v", "error", "-i", b["src"],
            "-vf", vf, "-frames:v", str(fr),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", out,
        ])
        segs.append(out)
        durs.append(seg)
        print(f"  beat {i}: vo={vo:.2f} seg={seg:.2f}")

    total = sum(durs)
    with open("work/vlist.txt", "w") as f:
        for i in range(len(segs)):
            f.write(f"file 'seg_{i}.mp4'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "work/vlist.txt", "-c", "copy", "work/video.mp4"])

    for i, b in enumerate(BEATS):
        ao = f"work/a_{i}.wav"
        run([
            "ffmpeg", "-y", "-v", "error", "-i", b["vo"],
            "-af", f"apad=whole_dur={durs[i]:.3f},atrim=0:{durs[i]:.3f},asetpts=PTS-STARTPTS,aresample=48000",
            "-ar", "48000", "-ac", "2", ao,
        ])
    with open("work/alist.txt", "w") as f:
        for i in range(len(BEATS)):
            f.write(f"file 'a_{i}.wav'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "work/alist.txt", "-c", "copy", "work/vo.wav"])

    mix_audio("work/vo.wav", total, durs, "work/mixed.wav")

    # Original sparse captions only (Impact L1 + amber L2 per beat) — no karaoke stream
    header = """[Script Info]
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
    lines = [header]
    lines.append(f"Dialogue: 0,{ass_time(0)},{ass_time(total)},Mark,,0,0,0,,THE STOIC SIGNAL")
    t = 0.0
    for i, b in enumerate(BEATS):
        st, en = t, t + durs[i]
        t = en
        amber = r"{\c&H003DA3E8&\fs104}"
        txt = r"{\fad(120,90)}" + f"{b['l1']}\\N{amber}{b['l2']}"
        lines.append(f"Dialogue: 0,{ass_time(st + 0.04)},{ass_time(en)},Cap,,0,0,0,,{txt}")
    with open("captions.ass", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    enc = [
        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-maxrate", "14M", "-bufsize", "28M",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
    ]
    out_cap = os.path.join(ROOT, "final", "short3.mp4")
    out_clean = os.path.join(ROOT, "final", "short3_nocaptions.mp4")

    # Always produce clean master first (no captions)
    run([
        "ffmpeg", "-y", "-v", "error",
        "-i", "work/video.mp4", "-i", "work/mixed.wav",
        "-map", "0:v", "-map", "1:a", *enc, out_clean,
    ])
    # Sparse original-style captions (publish)
    run([
        "ffmpeg", "-y", "-v", "error",
        "-i", "work/video.mp4", "-i", "work/mixed.wav",
        "-vf", "ass=captions.ass",
        "-map", "0:v", "-map", "1:a", *enc, out_cap,
    ])
    print(f"DONE: {out_cap}  (original sparse captions only)")
    print(f"      {out_clean}  (always kept, no captions)")
    print(f"      total={total:.2f}s  SFX=Light Rain + Distant Thunder (low)")


if __name__ == "__main__":
    main()
