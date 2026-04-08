# Benchmark Agents Guide

Diarization benchmark suite for the MimicScribe meeting transcription pipeline.

## Quick Reference

```bash
cd benchmark
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Download corpus data
bench-download --corpus ami          # AMI IHM-mix eval (16 sessions, ~512 MB)
bench-download --corpus earnings21   # Earnings-21 eval-10 (11 files, ~2 GB)

# Run MimicScribe pipeline (from project root)
bench-run --corpus ami

# Score results
bench-score --corpus ami
```

## Saving Raw Segments for LLM Comparison

To test alternative LLMs for speaker attribution, capture the pre-LLM diarization segments:

```bash
swift run mimicscribe --process-file --file benchmark/data/ami/audio/ES2004a.wav --save-raw-segments
```

The `--save-raw-segments` flag saves raw segments JSON to `benchmark/output/raw_segments/` before the Gemini attribution step runs. These files are the input for `reattribute.py`.

## Testing Alternative LLMs

Before running reattribution, create `benchmark/attribution_prompt.txt` with the speaker attribution system instruction (this file is gitignored — it is not distributed). The production prompt lives in `TranscriptFusionService.swift` under `speakerAttributionSystemInstruction`.

```bash
# Re-attribute with Qwen 3.5 models via OpenRouter (requires OPENROUTER_API_KEY in .env)
python -m mimicscribe_bench.reattribute --model qwen3.5-9b
python -m mimicscribe_bench.reattribute --model qwen3.5-35b

# Score alternative LLM output
bench-score --corpus ami --output-dir output/qwen3.5-9b
```

Available models: `qwen3.5-9b`, `qwen3.5-35b`, `qwen3.5-397b`. Add new models in `reattribute.py` `MODELS` dict.

## Pyannote Baseline

Reference implementation of pyannote community-1 for baseline DER comparison:

```bash
pip install pyannote.audio torch
export HF_TOKEN=hf_...  # or add HUGGINGFACE_PAT_READ to .env
python pyannote_baseline.py --corpus ami
bench-score --corpus ami --output-dir output/pyannote-community-1
```

Requires accepting the model license at https://huggingface.co/pyannote/speaker-diarization-community-1

## Directory Layout

```
benchmark/
  data/                    # Downloaded corpus audio + ground truth (gitignored)
    ami/audio/             # AMI IHM-mix WAV files
    ami/rttm/              # Ground truth RTTM from BUTSpeechFIT
    ami/uem/               # Scored regions
    earnings21/            # Earnings-21 audio + RTTM
  output/                  # Pipeline outputs (gitignored)
    ami/rttm/              # MimicScribe hypothesis RTTM
    raw_segments/          # Pre-attribution JSON (--save-raw-segments)
    pyannote-community-1/  # Pyannote baseline RTTM
    qwen3.5-9b/rttm/      # Qwen reattribution RTTM
  results/                 # Scored results (committed)
    RESULTS.md             # Markdown results table
    results.json           # Raw JSON scores
  src/mimicscribe_bench/   # Python package
    download.py            # Corpus downloader
    run_pipeline.py        # MimicScribe pipeline runner
    score.py               # DER scoring via pyannote.metrics
    reattribute.py         # Alternative LLM attribution via OpenRouter
    cli.py                 # bench-all entrypoint
  pyannote_baseline.py     # Reference pyannote community-1 script
```

## Metrics

- **DER** (Diarization Error Rate): missed speech + false alarm + speaker confusion. 0.25s collar (standard).
- Scored with `pyannote.metrics.diarization.DiarizationErrorRate`.
- Ground truth RTTM from [BUTSpeechFIT/AMI-diarization-setup](https://github.com/BUTSpeechFIT/AMI-diarization-setup) (words-only, standard benchmark setup).

## Corpora

| Corpus | Source | Eval Sessions | Hours | License |
|--------|--------|--------------|-------|---------|
| AMI IHM-mix | [AMI Corpus](https://groups.inf.ed.ac.uk/ami/corpus/) | 16 | ~8h | CC BY 4.0 |
| Earnings-21 | [Rev.com](https://github.com/revdotcom/speech-datasets) | 11 | ~10h | Free |
