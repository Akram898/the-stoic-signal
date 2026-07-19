# THE STOIC SIGNAL — Full automation stack (1–2 Shorts/day)

## What just shipped (manual-director run)

| Asset | Path |
|--------|------|
| **Captioned master** (publish) | `final/short3.mp4` — modern karaoke + punch + watermark + low SFX |
| **Clean master** (always) | `final/short3_nocaptions.mp4` — same picture/VO/SFX, **no** burn-in captions |
| Script | `short3/SCRIPT.md` |
| Stills / motion | `short3/img/`, `short3/clips/` (8/8 Grok motion) |
| VO (free Edge default) | `short3/audio/` ← Christopher; packs in `audio_edge_*` |
| SFX (low) | `sound_effects/Light Rain.mp3`, `Distant Thunder.mp3` |
| Assembler | `python assemble_s3.py` |
| OpenMontage notes | `OPENMONTAGE.md` |

**Title:** Your Anger Is Their Remote Control  
**Pillar:** Discipline / modern application  
**CapCut:** import `short3_nocaptions.mp4` if you want manual caption polish, SFX, or end-screen; or upload `short3.mp4` as-is.

---

## Voice: free vs ElevenLabs

| Option | Cost | Quality | How |
|--------|------|---------|-----|
| **Edge TTS (used for Short 3)** | Free | Good deep male (Ryan/Christopher) | `pip install edge-tts` — no key |
| **ElevenLabs** | Paid | Closest to original “Arthur” | Set `ELEVENLABS_API_KEY` + voice id |
| **Higgsfield (original S1/S2)** | Credits | Matched Arthur | Their UI / API |

You do **not** need an ElevenLabs key for daily volume. For brand-closest VO later, add:

```
ELEVENLABS_API_KEY=sk-...
ELEVENLABS_VOICE_ID=<arthur-or-clone>
```

---

## What you need for a **finished daily product** (1–2 reels/day)

### A. Production (already mostly built)

1. **Topic + script** — agent writes 8 beats (hook + tactic + CTA) from `CHANNEL_BIBLE.md` pillars  
2. **VO** — Edge TTS (free) or ElevenLabs  
3. **8 stills** — Grok Imagine / image_edit (MARCUS ref locked)  
4. **8 motion clips** — Grok `image_to_video` (sequential; watch rate limits)  
5. **Mux** — `assemble_s3.py` pattern: grade + drone/rain bed + ASS captions + watermark  
6. **Masters** — captioned + nocaptions into `final/`

**Not required for MVP:** Remotion. FFmpeg assembler already matches your S1/S2 quality system. CapCut = optional human polish.

### B. Accounts & keys (for auto-post)

| Need | Purpose | Required? |
|------|---------|-----------|
| YouTube channel + Brand Account | Upload Shorts | Yes |
| Google Cloud OAuth client (YouTube Data API) | Auto-upload | Yes for full auto |
| (Optional) TikTok / IG / Meta developer apps | Cross-post | No for YT-only |
| Grok / xAI image+video access | Visuals | Yes (you have in Grok Build) |
| Edge TTS | Free VO | Already works |
| ElevenLabs key | Premium VO | Optional |
| Canva / nothing | Thumbnails can be Grok stills | Optional |

### C. Daily schedule (realistic)

| Slot | Cadence | Notes |
|------|---------|--------|
| Generate 1–2 Shorts | Night batch or morning | ~15–40 min wall time + rate limits on video gen |
| Review 2 min each | You or “approve” flag | CapCut only if something looks off |
| Post | 1× peak (e.g. 12:00) + optional 2nd (19:00) | Shorts feed prefers consistency over volume |

### D. Folder pipeline (recommended)

```
inbox/topics.md          # ideas queue
queue/shortN/SCRIPT.md
queue/shortN/audio|img|clips|work/
final/shortN.mp4
final/shortN_nocaptions.mp4
published/               # move after upload
```

One command later: `python pipeline.py --topic "cold showers" --post youtube`

### E. Auto-post (minimal)

1. Enable **YouTube Data API v3**  
2. OAuth desktop client → `client_secret.json`  
3. Script: upload `final/shortN.mp4` as Short (≤60s, vertical) + title/description/hashtags from `PUBLISHING.md` template  
4. Windows Task Scheduler / cron: run generate 06:00, upload 12:00  

### F. Quality gates (keep you monetizable)

- MARCUS face consistency every open/close  
- No pure static openings (motion in first 3s)  
- Burned captions + watermark  
- Original argument (not quote dump)  
- Human glance: reject slop once/day  

---

## Cost sketch (per Short, rough)

| Step | Free path | Paid path |
|------|-----------|-----------|
| Script | Agent | — |
| VO | Edge TTS $0 | ElevenLabs ~$0.05–0.30 |
| 8 images | Grok quota | — |
| 8 videos | Grok quota / rate limit | — |
| Assemble | FFmpeg $0 | — |
| Upload | YT API $0 | — |

Bottleneck is usually **video gen rate limits** (we hit 429 when parallel). Generate **sequentially** or queue overnight.

---

## CapCut handoff

Use when you want:

- Extra whoosh / thunder on pattern interrupts  
- Fine-tuned caption timing  
- Trend audio under VO (careful: keep VO primary)  
- Thumbnail frame pick  

Source: **`final/short3_nocaptions.mp4`** + re-export with your overlays.

---

## Next agent commands (when you want Short 4+)

```text
Make short4 on [topic]. Same pipeline as short3. Edge TTS. All scenes motion. Assemble to final/.
```

Or fully auto once `pipeline.py` exists:

```text
Batch 7 shorts for the week from pillars; leave in final/ for me to CapCut-check.
```
