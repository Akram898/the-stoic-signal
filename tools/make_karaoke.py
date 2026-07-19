#!/usr/bin/env python3
"""Burn Whisper-synced karaoke captions onto a *nocaptions* master.

Usage:
  python tools/make_karaoke.py short3
  python tools/make_karaoke.py short1 short2

Outputs: final/karaoke/<name>.mp4
Source:  final/<name>_nocaptions.mp4  (original captions never present)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "final" / "karaoke"
WORK = OUT_DIR / "work"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr[-2000:])
        raise SystemExit(1)


def ass_time(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h = cs // 360000
    cs %= 360000
    m = cs // 6000
    cs %= 6000
    s = cs // 100
    cs %= 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def words_to_ass(words: list[dict], duration: float) -> str:
    """Chunked captions timed to speech — single solid color, no karaoke color wipe."""
    chunks: list[list[dict]] = []
    cur: list[dict] = []
    for w in words:
        if not w.get("word"):
            continue
        if cur:
            gap = w["start"] - cur[-1]["end"]
            if gap > 0.45 or len(cur) >= 5:
                chunks.append(cur)
                cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)

    # Single color (warm white), subtle box — no SecondaryColour wipe / no \k
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Arial Black,64,&H00F2F2F2,&H00F2F2F2,&H00000000,&H78000000,-1,0,0,0,100,100,1.2,0,1,4,2,2,48,48,380,1
Style: Mark,Arial Black,26,&H5A3DA3E8,&H5A3DA3E8,&H6E000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,1,8,0,0,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header, f"Dialogue: 0,{ass_time(0)},{ass_time(duration)},Mark,,0,0,0,,THE STOIC SIGNAL"]
    for ch in chunks:
        st = max(0.0, ch[0]["start"] - 0.02)
        en = ch[-1]["end"] + 0.10
        phrase = " ".join(
            w["word"].upper().replace("{", "").replace("}", "") for w in ch
        )
        # Soft fade only — one color, no word motion / color change
        text = r"{\fad(80,100)}" + phrase
        lines.append(f"Dialogue: 1,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{text}")
    return "\n".join(lines) + "\n"


def process(name: str) -> None:
    src = ROOT / "final" / f"{name}_nocaptions.mp4"
    if not src.is_file():
        raise SystemExit(f"Missing clean master: {src}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    wav = WORK / f"{name}_audio.wav"
    words_json = WORK / f"{name}_words.json"
    ass_path = WORK / f"{name}_karaoke.ass"
    out_mp4 = OUT_DIR / f"{name}.mp4"

    print(f"[{name}] extract audio…")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(wav)])

    print(f"[{name}] whisper word timestamps…")
    from faster_whisper import WhisperModel

    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(wav), word_timestamps=True, language="en")
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    payload = {"duration": info.duration, "words": words}
    words_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[{name}] {len(words)} words")

    ass_path.write_text(words_to_ass(words, info.duration or 40.0), encoding="utf-8")

    print(f"[{name}] burn karaoke…")
    # relative ass path — Windows ffmpeg original_size bug with absolute paths
    p = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(src),
            "-vf", f"ass={ass_path.name}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "copy", "-movflags", "+faststart",
            str(out_mp4),
        ],
        cwd=str(WORK),
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        print(p.stderr[-2000:])
        raise SystemExit(1)
    print(f"[{name}] -> {out_mp4}")


def main():
    names = sys.argv[1:] or ["short3"]
    for n in names:
        n = n.replace(".mp4", "").replace("_nocaptions", "")
        process(n)


if __name__ == "__main__":
    main()
