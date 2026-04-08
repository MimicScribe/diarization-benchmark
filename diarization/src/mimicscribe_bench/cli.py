"""Run the full benchmark pipeline: download, process, score."""

import argparse
from pathlib import Path

from . import download, run_pipeline, score


def main():
    parser = argparse.ArgumentParser(
        description="MimicScribe diarization benchmark — full pipeline"
    )
    parser.add_argument(
        "--corpus",
        choices=["ami", "earnings21", "all"],
        default="all",
        help="Which corpus to benchmark (default: all)",
    )
    parser.add_argument(
        "--step",
        choices=["download", "run", "score", "all"],
        default="all",
        help="Which step to run (default: all)",
    )
    parser.add_argument(
        "--collar",
        type=float,
        default=0.25,
        help="DER collar in seconds (default: 0.25)",
    )
    args = parser.parse_args()

    if args.step in ("download", "all"):
        print("=" * 60)
        print("STEP 1: Download corpus data")
        print("=" * 60)
        _download(args)

    if args.step in ("run", "all"):
        print("\n" + "=" * 60)
        print("STEP 2: Run MimicScribe pipeline")
        print("=" * 60)
        _run(args)

    if args.step in ("score", "all"):
        print("\n" + "=" * 60)
        print("STEP 3: Score results")
        print("=" * 60)
        _score(args)


def _download(args):
    import sys
    sys.argv = ["bench-download", "--corpus", args.corpus]
    download.main()


def _run(args):
    import sys
    sys.argv = ["bench-run", "--corpus", args.corpus]
    run_pipeline.main()


def _score(args):
    import sys
    sys.argv = ["bench-score", "--corpus", args.corpus, "--collar", str(args.collar)]
    score.main()


if __name__ == "__main__":
    main()
