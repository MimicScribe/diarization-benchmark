#!/usr/bin/env python3
"""
Pyannote Community-1 reference diarization baseline.

Runs the standard pyannote/speaker-diarization-community-1 pipeline on
benchmark audio files and outputs RTTM hypothesis files for scoring.
This is the reference open-source diarization baseline — no ASR, no LLM
correction, just pyannote's pretrained pipeline with default parameters.

Requirements:
    pip install pyannote.audio torch

Usage:
    # Set your HuggingFace token (required for model download)
    export HF_TOKEN=hf_...

    # Run on AMI eval set
    python pyannote_baseline.py --corpus ami

    # Run on a single file
    python pyannote_baseline.py --file data/ami/audio/ES2004a.wav

    # Score results
    bench-score --corpus ami --output-dir output/pyannote-community-1

Published DER for community-1 on AMI IHM: 17.0%
(https://www.pyannote.ai/benchmark)
"""

import argparse
import os
import sys
import time
from pathlib import Path

import torch
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook

DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "pyannote-community-1" / "rttm"

MODEL_ID = "pyannote/speaker-diarization-community-1"


def get_device() -> torch.device:
    """Select best available device."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_pipeline(token: str | None = None) -> Pipeline:
    """Load the pyannote community-1 pipeline."""
    hf_token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_PAT_READ")
    if not hf_token:
        # Try .env file
        env_path = Path(__file__).resolve().parents[1] / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                for key in ("HF_TOKEN", "HUGGINGFACE_PAT_READ"):
                    if line.startswith(f"{key}="):
                        hf_token = line.split("=", 1)[1].strip()
                        break
                if hf_token:
                    break
    if not hf_token:
        print(
            "Error: HuggingFace token required. Set HF_TOKEN environment variable\n"
            "or pass --token. Get a token at https://huggingface.co/settings/tokens\n"
            f"and accept the model license at https://huggingface.co/{MODEL_ID}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Loading {MODEL_ID}...")
    pipeline = Pipeline.from_pretrained(MODEL_ID, token=hf_token)

    device = get_device()
    print(f"Using device: {device}")
    pipeline.to(device)

    return pipeline


def diarize_file(pipeline: Pipeline, audio_path: Path, output_path: Path) -> None:
    """Run diarization on a single audio file and write RTTM output."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"  [{audio_path.stem}] [skip] (already exists)")
        return

    print(f"  [{audio_path.stem}]...", end=" ", flush=True)
    t0 = time.time()

    # Run pipeline with default parameters — no num_speakers hint
    result = pipeline(str(audio_path))

    # pyannote 4.0 returns DiarizeOutput; extract the Annotation
    if hasattr(result, "speaker_diarization"):
        diarization = result.speaker_diarization
    else:
        diarization = result  # pyannote 3.x returns Annotation directly

    elapsed = time.time() - t0
    n_speakers = len(diarization.labels())
    n_segments = len(list(diarization.itertracks(yield_label=True)))

    # Write RTTM
    with open(output_path, "w") as f:
        diarization.write_rttm(f)

    print(f"[ok] {n_segments} segments, {n_speakers} speakers ({elapsed:.1f}s)")


def process_corpus(pipeline: Pipeline, corpus: str, data_dir: Path, output_dir: Path) -> None:
    """Process all audio files for a corpus."""
    audio_dir = data_dir / corpus / "audio"
    if not audio_dir.exists():
        print(f"  [skip] {corpus}: no audio in {audio_dir}")
        return

    audio_files = sorted(audio_dir.glob("*.wav"))
    if not audio_files:
        print(f"  [skip] {corpus}: no .wav files")
        return

    print(f"\n=== Pyannote Community-1 baseline: {corpus} ({len(audio_files)} files) ===")

    for i, audio_path in enumerate(audio_files, 1):
        file_id = audio_path.stem
        rttm_path = output_dir / f"{file_id}.rttm"
        print(f"  [{i}/{len(audio_files)}]", end=" ")
        diarize_file(pipeline, audio_path, rttm_path)


def main():
    parser = argparse.ArgumentParser(
        description="Pyannote Community-1 reference diarization baseline"
    )
    parser.add_argument(
        "--corpus",
        choices=["ami", "earnings21", "all"],
        default=None,
        help="Which corpus to process",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Process a single audio file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Output directory for RTTM files (default: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="HuggingFace access token (or set HF_TOKEN env var)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help=f"Data directory (default: {DATA_DIR})",
    )
    args = parser.parse_args()

    if not args.corpus and not args.file:
        parser.error("Specify --corpus or --file")

    pipeline = load_pipeline(token=args.token)

    if args.file:
        file_id = args.file.stem
        rttm_path = args.output_dir / f"{file_id}.rttm"
        diarize_file(pipeline, args.file, rttm_path)
    else:
        corpora = ["ami", "earnings21"] if args.corpus == "all" else [args.corpus]
        for corpus in corpora:
            process_corpus(pipeline, corpus, args.data_dir, args.output_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
