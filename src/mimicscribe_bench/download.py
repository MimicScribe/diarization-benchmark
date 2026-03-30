"""Download AMI IHM-mix and Earnings-21 eval data with ground-truth RTTMs."""

import argparse
import csv
import io
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# AMI IHM-mix eval split (BUTSpeechFIT standard test partition — 16 sessions)
AMI_EVAL_MEETINGS = [
    "IS1009a", "IS1009b", "IS1009c", "IS1009d",
    "ES2004a", "ES2004b", "ES2004c", "ES2004d",
    "TS3003a", "TS3003b", "TS3003c", "TS3003d",
    "EN2002a", "EN2002b", "EN2002c", "EN2002d",
]

AMI_AUDIO_URL = (
    "https://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus"
    "/{meeting_id}/audio/{meeting_id}.Mix-Headset.wav"
)

AMI_RTTM_URL = (
    "https://raw.githubusercontent.com/BUTSpeechFIT/AMI-diarization-setup"
    "/main/only_words/rttms/test/{meeting_id}.rttm"
)

AMI_UEM_URL = (
    "https://raw.githubusercontent.com/BUTSpeechFIT/AMI-diarization-setup"
    "/main/uems/test/{meeting_id}.uem"
)

# Earnings-21 eval-10 subset (11 files, ~10 hours)
EARNINGS21_EVAL_IDS = [
    "4320211", "4341191", "4346818", "4359971", "4365024",
    "4366522", "4366893", "4367535", "4383161", "4384964", "4387332",
]


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download a file with progress indication. Returns True on success."""
    if dest.exists():
        print(f"  [skip] {desc or dest.name} (already exists)")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    label = desc or dest.name
    print(f"  [download] {label}...", end=" ", flush=True)
    try:
        resp = requests.get(url, stream=True, timeout=600)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(f"\r  [download] {label}... {pct}%", end="", flush=True)
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"\r  [download] {label}... {size_mb:.1f} MB")
        return True
    except (requests.RequestException, OSError) as e:
        print(f"\n  [error] {label}: {e}")
        dest.unlink(missing_ok=True)
        return False


def download_ami(data_dir: Path) -> None:
    """Download AMI IHM-mix eval split audio + RTTM ground truth."""
    ami_dir = data_dir / "ami"
    audio_dir = ami_dir / "audio"
    rttm_dir = ami_dir / "rttm"
    uem_dir = ami_dir / "uem"

    print(f"\n=== AMI IHM-mix eval ({len(AMI_EVAL_MEETINGS)} sessions) ===")

    for meeting_id in AMI_EVAL_MEETINGS:
        download_file(
            AMI_AUDIO_URL.format(meeting_id=meeting_id),
            audio_dir / f"{meeting_id}.wav",
            desc=f"{meeting_id}.wav",
        )
        download_file(
            AMI_RTTM_URL.format(meeting_id=meeting_id),
            rttm_dir / f"{meeting_id}.rttm",
            desc=f"{meeting_id}.rttm",
        )
        download_file(
            AMI_UEM_URL.format(meeting_id=meeting_id),
            uem_dir / f"{meeting_id}.uem",
            desc=f"{meeting_id}.uem",
        )


def download_earnings21(data_dir: Path) -> None:
    """Download Earnings-21 eval-10 subset audio + RTTMs."""
    e21_dir = data_dir / "earnings21"
    audio_dir = e21_dir / "audio"
    rttm_dir = e21_dir / "rttm"

    print(f"\n=== Earnings-21 eval-10 ({len(EARNINGS21_EVAL_IDS)} files) ===")

    # RTTMs from GitHub (small text files)
    for file_id in EARNINGS21_EVAL_IDS:
        rttm_url = (
            "https://raw.githubusercontent.com/revdotcom/speech-datasets"
            f"/master/earnings21/rttms/{file_id}.rttm"
        )
        download_file(rttm_url, rttm_dir / f"{file_id}.rttm", desc=f"{file_id}.rttm")

    # Audio from HuggingFace (large WAV files)
    print("\n  Downloading audio from HuggingFace (this may take a while)...")
    for file_id in EARNINGS21_EVAL_IDS:
        audio_url = (
            "https://huggingface.co/datasets/Revai/earnings21"
            f"/resolve/main/wav/{file_id}.wav"
        )
        download_file(audio_url, audio_dir / f"{file_id}.wav", desc=f"{file_id}.wav")


def main():
    parser = argparse.ArgumentParser(description="Download benchmark corpora")
    parser.add_argument(
        "--corpus",
        choices=["ami", "earnings21", "all"],
        default="all",
        help="Which corpus to download (default: all)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help=f"Data directory (default: {DATA_DIR})",
    )
    args = parser.parse_args()

    if args.corpus in ("ami", "all"):
        download_ami(args.data_dir)
    if args.corpus in ("earnings21", "all"):
        download_earnings21(args.data_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
