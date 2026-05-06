# MimicScribe Diarization Benchmark Results

Pipeline: Parakeet TDT 0.6B ASR + Pyannote Community-1 diarization + on-device post-clustering refinement + Gemini 3 Flash for naming.

Run date: 2026-05-06

## What's new in this update

**94.0% → 95.0% pre-LLM SAA** (+1.0 pp aggregate). Two changes since the 2026-05-02 publication.

A new post-clustering stage recovers chunks the diarizer had stranded as their own miniature clusters and reassigns them where they acoustically belong. Per-corpus deltas: AMI +1.7 pp, VoxConverse +1.9 pp, SCOTUS +1.3 pp, Earnings-21 +0.1 pp, Podcast +0.8 pp.

The LLM step changed structurally. The previous publication showed a separate **+ LLM SAA** column where the LLM lifted aggregate SAA from 94.0% to 95.1% — partly by collapsing acoustic clusters that the deterministic pipeline had over-fragmented. That gain was real but architecturally ambiguous: the LLM was sometimes stitching two different speakers together under one name. The current pipeline disables that path. **Post-LLM SAA equals pre-LLM SAA on every file in the corpus** — the LLM names speakers and cleans up text but no longer changes speaker counts or boundaries.

The "+ LLM SAA" column is gone. There is no longer a post-LLM number distinct from the deterministic-pipeline number.

The corpus is unchanged from the prior publication — same 58 files at 16 kHz wideband across five domains. **Several of the post-clustering stages primarily address embedding failures on compressed and narrowband audio — phone calls, Bluetooth meeting mics, low-bitrate streams.** Their contribution to SAA on this wideband corpus is conservative; a separate narrowband publication is planned.

## Speaker Attribution Accuracy (SAA)

**SAA = 1 − confusion rate.** Percentage of speech time attributed to the correct speaker.

| Corpus | Files | Pyannote C1 SAA | MimicScribe SAA | Speedup |
|--------|------:|----------------:|----------------:|--------:|
| Earnings-21 | 11 | 98.1% | **96.6%** | 2.6x |
| VoxConverse | 20 | 95.9% | **94.4%** | 3.8x |
| SCOTUS | 5 | 99.2% | **96.3%** | 3.1x |
| AMI | 16 | 97.0% | **95.3%** | 3.3x |
| Podcast | 6 | — | **91.5%** | — |
| **Aggregate** | **58** | — | **95.0%** | — |

Speedup is diarization-only on Apple M1 Max (ANE vs MPS GPU). **Pyannote C1** is the reference [community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) pipeline run in Python with default parameters.

Over-segmentation is preferred over under-segmentation. Merging two speakers in the UI is a single correction; splitting one speaker requires manual per-segment reassignment.

## What the LLM step does

The deterministic pipeline outputs anonymous speaker IDs (e.g. `Speaker 2`) with raw ASR text. The LLM pass renames each cluster from transcript context, fixes ASR errors, and cleans up formatting:

**Before (deterministic pipeline output):**
```
[  10.9-149.0] Speaker 2:  ? Mr. Chief Justice, and may it please the court, the Fifth Circuit's
                            decision in this case is the f...
[ 154.6-158.9] Speaker 3:  w. Are there any limits on what Congress can do
[ 388.1-389.0] Speaker 2:  you're
[ 389.0-459.0] Speaker 1:  you have a very aggressive view of Congress's authority...
```

**After (LLM naming + cleanup):**
```
[  10.9-149.0] Elizabeth Prelogar:  Mr. Chief Justice, and may it please the court, the Fifth
                                    Circuit's decision in this case is the fir...
[ 154.6-158.9] Justice Thomas:     Are there any limits on what Congress can do?
[ 388.1-459.0] Speaker 1:          General, one of the things that struck me as I was reading
                                    it, you have a very aggressive view of Co...
```

A cluster is renamed only when the transcript directly identifies that speaker — by self-introduction, by another speaker addressing them, or by a role mentioned in the transcript. Clusters without identification keep their cluster ID. The model is instructed to default to the cluster ID rather than guess from setting or topic.

The LLM is also not allowed to give two cluster IDs the same name. A deterministic post-process verifies this: if the model attempts to collapse two acoustic clusters under one identity, the larger cluster keeps the name and the other is reset to its cluster ID. Across all 58 files in this corpus, post-LLM SAA equals pre-LLM SAA exactly — the LLM cannot regress speaker accuracy.

## Post-clustering refinement

The deterministic pipeline does not stop at the diarizer's output. Several on-device stages run between clustering and the LLM step, addressing common failure modes: turn-change boundaries that land a few seconds off, chunks that the clustering placed in the wrong cluster on long meetings or with similar-voice speakers, and short fragments that the diarizer left as one-off singletons but actually belong to a larger cluster. These stages run on the Neural Engine and on cached embeddings — total cost is well under 10 s per 30-minute meeting.

This phase carries most of the difference between the Pyannote C1 SAA column and the MimicScribe SAA column.

## Latency

| Corpus | File | Audio | Pyannote | MimicScribe | Speedup |
|--------|------|------:|---------:|------------:|--------:|
| VoxConverse | duvox | 16 min | 47.7s | 12.7s | 3.8x |
| SCOTUS | 22-842 | 74 min | 312.7s | 99.3s | 3.1x |
| Earnings-21 | 4320211 | 55 min | 208.7s | 79.7s | 2.6x |
| AMI | ES2004a | 40 min | 53.4s | 16.0s | 3.3x |

Diarization-only, Apple M1 Max. Pyannote uses MPS (GPU); MimicScribe uses ANE.

## DER Breakdown

SAA isolates **confusion** — was the right speaker tagged on speech the system actually transcribed? DER mixes confusion with **missed speech** (omitted by the system) and **false alarm** (speech the system attributed but ground-truth marks as silence). On meeting-style audio, those last two are dominated by UX choices rather than diarization quality:

- Sentence-level segmentation deliberately leaves gaps between turns; pyannote.metrics counts them as false alarm when adjacent same-speaker segments are merged.
- An ASR that drops mumbled or overlapped speech can score *lower* DER than a system that captures it, because missed speech can't be confused.

**Confusion** is the meaningful component for attribution quality.

| Corpus | DER | Confusion | False Alarm | Missed |
|--------|----:|----------:|------------:|-------:|
| Earnings-21 | 18.2% | 3.4% | 11.6% | 3.2% |
| VoxConverse | 16.9% | 5.6% | 5.6% | 5.8% |
| SCOTUS | 6.0% | 3.7% | 0.0% | 2.3% |
| AMI | 26.3% | 4.7% | 5.8% | 15.7% |
| Podcast | 10.4% | 8.5% | 1.2% | 0.7% |
| **Aggregate** | **15.5%** | **5.0%** | **4.9%** | **5.6%** |

## Benchmark vs Production

These results are a **worst-case scenario** using single-channel mixed audio with no prior context. In production:

- **Dual-channel audio** eliminates local/remote speaker confusion.
- **Voice profiles** enable verified speaker recognition.
- **Meeting context** helps the LLM identify participants by name and role.

## Corpora

| Corpus | Source | Files | Duration | Speakers |
|--------|--------|------:|---------:|---------:|
| [Earnings-21](https://huggingface.co/datasets/Revai/earnings21) | Public earnings calls | 11 | ~10 hrs | 5–15 |
| [VoxConverse](https://github.com/joonson/voxconverse) | YouTube debates/interviews | 20 | ~2 hrs | 2–6 |
| [SCOTUS](https://www.oyez.org) | Supreme Court oral arguments | 5 | ~7.5 hrs | 10–12 |
| [AMI](https://groups.inf.ed.ac.uk/ami/corpus/) | Meeting recordings (IHM-mix) | 16 | ~9 hrs | 4 |
| Podcast | Long-form interview podcasts | 6 | ~10 hrs | 2–4 |

## Methodology

- **Collar**: 0.25s | **Scoring**: [pyannote.metrics](https://pyannote.github.io/pyannote-metrics/) DiarizationErrorRate, `skip_overlap=False`
- **Diarization**: Pyannote Community-1 via [FluidAudio](https://github.com/FluidInference/FluidAudio) CoreML
- **ASR**: Parakeet TDT 0.6B via FluidAudio CoreML
- **LLM**: Gemini 3 Flash (temp 0.1, thinking minimal)

## Reproducibility

The deterministic pipeline runs end-to-end in Swift; Python only does the LLM step and scoring.

```
swift build -c release
.build/release/mimicscribe --benchmark-pipeline-corpus
benchmark/.venv313/bin/python3 scripts/run_corpus_eval.py
```

The first command runs the deterministic pipeline on the 58-file corpus and writes per-file post-clustering segments plus per-stage timings. The second runs the LLM attribution and scores against the ground-truth RTTMs. Both halves persist progress per file. Audio source paths and ground-truth RTTMs come from the public corpora linked above.
