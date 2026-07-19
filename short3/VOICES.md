# Short 3+ free narrator packs (Edge TTS)

Stay on **free Edge** for now. Swap packs by copying into `audio/` then `python assemble_s3.py`.

| Pack | Voice | Path | When to use |
|------|--------|------|-------------|
| **ACTIVE (default)** | `en-US-ChristopherNeural` −15% / −12Hz | `audio_edge_christopher/` → copied to `audio/` | Deep US authority; current Short 3 |
| Alternate | `en-GB-RyanNeural` −15% / −12Hz | `audio_edge_ryan/` | British alternate; interchange with Christopher |
| Optional paid | ElevenLabs Daniel | `audio_elevenlabs_daniel/` | Only if we leave free tier later |

## Swap narrator

```powershell
# Christopher (default)
Copy-Item short3\audio_edge_christopher\*.mp3 short3\audio\ -Force
python assemble_s3.py

# Ryan
Copy-Item short3\audio_edge_ryan\*.mp3 short3\audio\ -Force
python assemble_s3.py
```

## Samples
`voice_samples_edge/` — one-line previews for A/B.
