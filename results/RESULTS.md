# MimicScribe Diarization Benchmark Results

Pipeline: Parakeet TDT 0.6B (on-device ASR) + Pyannote (on-device diarization) + Gemini 3 Flash (LLM speaker attribution)

Run date: 2026-03-31

Collar: 0.25s (standard)

## Benchmark vs Production

These results are a **worst-case scenario**. In production, the pipeline has advantages unavailable here:

- **Mic/system audio separation**: MimicScribe captures mic and system audio (remote participants) as separate streams, giving diarization a free speaker separation signal. This benchmark uses a single mixed file with no channel distinction.
- **Voice profiles**: Users can save voice profiles for verified speaker recognition. The benchmark has no saved profiles.
- **Meeting context**: Users can provide prep context that helps the LLM identify speakers. The benchmark has no context.
- **Segment granularity**: The pipeline outputs sentence-level segments for readability. Silent gaps within a sentence count as false alarm in DER, but this is a deliberate UX choice — it accounts for most of the false alarm rate.

## Summary

DER is the sum of three components. **Confusion** — speech attributed to the wrong speaker — is the most meaningful quality signal. **False Alarm** is inflated by sentence-level segments spanning silent gaps (see above). **Missed** is undetected speech.

| Corpus | Files | DER | Confusion (speaker error) | False Alarm (segment boundaries) | Missed |
|--------|------:|----:|--------------------------:|--------------------------------:|-------:|
| ami | 16 | 37.0% | 10.0% | 11.2% | 15.7% |
| earnings21 | 11 | 18.3% | 4.0% | 13.7% | 0.6% |

## Baseline Comparison

[Pyannote Community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) is the reference open-source diarization system, run with default parameters.

| Corpus | Pyannote Community-1 | MimicScribe Pipeline |
|--------|--------------------:|--------------------:|
| ami | 13.1% | 37.0% |
| earnings21 | 4.6% | 18.3% |

## Per-File Results

### ami

| File | Pyannote C1 | MimicScribe | Ref Spk | Hyp Spk |
|------|------------:|------------:|--------:|--------:|
| EN2002a | 17.8% | 44.6% | 4 | 5 |
| EN2002b | 17.2% | 46.2% | 4 | 7 |
| EN2002c | 15.4% | 41.9% | 3 | 4 |
| EN2002d | 20.1% | 47.4% | 4 | 5 |
| ES2004a | 14.4% | 41.1% | 4 | 5 |
| ES2004b | 8.7% | 27.5% | 4 | 5 |
| ES2004c | 8.5% | 22.3% | 4 | 5 |
| ES2004d | 14.0% | 61.8% | 4 | 4 |
| IS1009a | 14.6% | 45.2% | 4 | 4 |
| IS1009b | 10.5% | 17.8% | 4 | 5 |
| IS1009c | 6.3% | 20.2% | 4 | 6 |
| IS1009d | 11.1% | 41.0% | 4 | 7 |
| TS3003a | 14.0% | 38.3% | 4 | 4 |
| TS3003b | 8.4% | 25.9% | 4 | 5 |
| TS3003c | 10.3% | 26.4% | 4 | 4 |
| TS3003d | 16.2% | 45.8% | 4 | 4 |

### earnings21

| File | Pyannote C1 | MimicScribe | Ref Spk | Hyp Spk |
|------|------------:|------------:|--------:|--------:|
| 4320211 | 5.0% | 20.5% | 10 | 10 |
| 4341191 | 3.1% | 23.7% | 15 | 9 |
| 4346818 | 2.3% | 17.2% | 15 | 15 |
| 4359971 | 3.1% | 18.0% | 10 | 10 |
| 4365024 | 2.3% | 11.9% | 13 | 13 |
| 4366522 | 2.0% | 12.2% | 5 | 5 |
| 4366893 | 2.2% | 11.0% | 9 | 9 |
| 4367535 | 7.5% | 20.0% | 11 | 11 |
| 4383161 | 1.8% | 10.9% | 11 | 11 |
| 4384964 | 18.1% | 35.3% | 15 | 15 |
| 4387332 | 0.9% | 10.7% | 6 | 6 |
