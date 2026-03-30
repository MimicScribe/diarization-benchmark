# MimicScribe Diarization Benchmark Results

Pipeline: Parakeet TDT 0.6B (on-device ASR) + Pyannote (on-device diarization) + Gemini 3 Flash (LLM speaker attribution)

Run date: 2026-03-29

Collar: 0.25s (standard)

## Benchmark vs Production

These results represent a **worst-case scenario** for the MimicScribe pipeline. In normal use, the pipeline has several advantages not available in this benchmark:

- **Mic/system audio separation**: MimicScribe captures the user's microphone and system audio (remote participants) as separate streams. This gives the diarization a free speaker separation signal — the primary user is always identified from the mic channel, and remote speakers are a distinct pool. In this benchmark, all speakers come from a single mixed audio file with no channel distinction.
- **Voice profiles**: Users can save voice profiles that provide verified speaker recognition with high confidence. The benchmark has no saved profiles.
- **Meeting context**: Users can provide prep context (e.g., "Meeting with Alice and Bob about Q3") that helps the LLM identify speakers. The benchmark has no context.
- **Segment granularity**: The pipeline outputs sentence-level segments because that's what users read. DER penalizes this heavily — silent gaps within a sentence count as false alarm — but it is a deliberate UX choice, not a diarization failure. This accounts for the majority of the false alarm rate.

## Summary

| Corpus | Files | DER | Missed | False Alarm | Confusion |
|--------|------:|----:|-------:|------------:|----------:|
| ami | 16 | 37.7% | 17.2% | 10.7% | 9.8% |
| earnings21 | 11 | 17.4% | 0.5% | 13.7% | 3.2% |

## Per-File Results

### ami

| File | DER | Missed | False Alarm | Confusion | Ref Spk | Hyp Spk |
|------|----:|-------:|------------:|----------:|--------:|--------:|
| EN2002a | 44.0% | 26.4% | 7.2% | 10.4% | 4 | 5 |
| EN2002b | 51.9% | 25.9% | 5.3% | 20.8% | 4 | 8 |
| EN2002c | 42.5% | 27.4% | 4.9% | 10.1% | 3 | 4 |
| EN2002d | 49.7% | 31.5% | 5.9% | 12.3% | 4 | 5 |
| ES2004a | 40.3% | 15.8% | 19.6% | 4.9% | 4 | 4 |
| ES2004b | 24.8% | 9.2% | 7.4% | 8.3% | 4 | 4 |
| ES2004c | 36.0% | 18.9% | 7.2% | 9.9% | 4 | 5 |
| ES2004d | 49.8% | 17.8% | 14.5% | 17.5% | 4 | 4 |
| IS1009a | 39.4% | 12.8% | 16.6% | 10.0% | 4 | 4 |
| IS1009b | 18.8% | 7.7% | 6.1% | 5.0% | 4 | 5 |
| IS1009c | 17.2% | 4.1% | 10.0% | 3.1% | 4 | 6 |
| IS1009d | 39.1% | 10.9% | 13.6% | 14.6% | 4 | 6 |
| TS3003a | 36.1% | 6.6% | 24.1% | 5.3% | 4 | 3 |
| TS3003b | 24.2% | 4.6% | 14.9% | 4.7% | 4 | 5 |
| TS3003c | 35.4% | 20.3% | 10.7% | 4.3% | 4 | 4 |
| TS3003d | 47.6% | 11.3% | 26.1% | 10.2% | 4 | 4 |

### earnings21

| File | DER | Missed | False Alarm | Confusion | Ref Spk | Hyp Spk |
|------|----:|-------:|------------:|----------:|--------:|--------:|
| 4320211 | 21.7% | 0.6% | 16.1% | 5.0% | 10 | 10 |
| 4341191 | 23.7% | 0.7% | 16.7% | 6.3% | 15 | 9 |
| 4346818 | 16.9% | 1.3% | 13.8% | 1.8% | 15 | 15 |
| 4359971 | 14.6% | 0.4% | 10.9% | 3.4% | 10 | 10 |
| 4365024 | 9.3% | 0.3% | 6.8% | 2.2% | 13 | 12 |
| 4366522 | 12.5% | 0.0% | 12.2% | 0.3% | 5 | 5 |
| 4366893 | 11.2% | 0.4% | 9.8% | 1.0% | 9 | 9 |
| 4367535 | 18.1% | 0.6% | 11.4% | 6.0% | 11 | 10 |
| 4383161 | 10.7% | 0.2% | 10.1% | 0.4% | 11 | 11 |
| 4384964 | 33.7% | 0.4% | 29.4% | 3.9% | 15 | 15 |
| 4387332 | 10.7% | 0.2% | 10.2% | 0.3% | 6 | 6 |
