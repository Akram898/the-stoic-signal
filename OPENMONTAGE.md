# OpenMontage — how it fits THE STOIC SIGNAL

Repo: [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)

## What it is
Agentic **video production studio**: pipelines (research → script → assets → edit → compose), Remotion/HyperFrames compose, word-level captions, TTS selectors, music/SFX tools, quality gates, Backlot storyboard.

## What we use **now** (this repo)
We do **not** vendor the full OpenMontage tree yet (heavy: Node remotion-composer, many optional APIs). Instead we **adopt its product rules** inside our light FFmpeg pipeline:

| OpenMontage idea | Our implementation |
|------------------|--------------------|
| Dual masters (publish + clean) | `final/shortN.mp4` + `final/shortN_nocaptions.mp4` always |
| Word-level / modern captions | ASS karaoke + punch keywords (`captions_modern.ass`) |
| Low bed SFX under VO | `sound_effects/Light Rain.mp3` + `Distant Thunder.mp3` |
| Stage-like reproducibility | `assemble_s3.py` + `short3/SCRIPT.md` + `VOICES.md` |
| No silent quality downgrade | All beats stay real motion clips |

## What to add later (full automation)
1. `git clone https://github.com/calesthio/OpenMontage.git tools/OpenMontage` (optional submodule)
2. `make setup` / Windows venv + `remotion-composer` npm install
3. Point agents at `AGENT_GUIDE.md` for **new** shorts when we want Remotion atelier / WhisperX word timestamps / music library
4. Keep **Stoic Signal** brand pack: MARCUS, palette, Edge Christopher/Ryan, Grok motion, FFmpeg grade

## When to use OpenMontage vs `assemble_s3.py`
| Job | Tool |
|-----|------|
| Daily Shorts (this channel) | `assemble_s3.py` (fast, locked brand) |
| New formats / explainers / Remotion kinetic type | OpenMontage pipelines |
| CapCut hand polish | Always start from `*_nocaptions.mp4` |

## Command (Short 3)
```bash
python assemble_s3.py
```
