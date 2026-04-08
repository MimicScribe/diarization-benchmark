"""Run MimicScribe pipeline on benchmark audio files and extract results."""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"

# MimicScribe database path
MIMICSCRIBE_DB = Path.home() / "Library/Application Support/app.mimicscribe/mimicscribe.db"


def get_existing_meetings(db_path: Path) -> set[str]:
    """Get set of existing meeting IDs from the database."""
    if not db_path.exists():
        return set()
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute("SELECT id FROM meetings").fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


def run_mimicscribe(audio_path: Path, timeout: int = 600) -> bool:
    """Run swift run mimicscribe --process-file on an audio file."""
    cmd = [
        "swift", "run", "mimicscribe",
        "--process-file", "--file", str(audio_path),
    ]
    # Run from the project root (parent of benchmark/)
    project_root = Path(__file__).resolve().parents[3]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    [timeout] {audio_path.name} exceeded {timeout}s")
        return False


def extract_meeting_rttm(db_path: Path, meeting_id: str, file_id: str) -> str | None:
    """Extract segments from a meeting and convert to RTTM format."""
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT segments_json FROM meetings WHERE id = ?", (meeting_id,)
        ).fetchone()
        if not row or not row[0]:
            return None
        container = json.loads(row[0])
        segments = container.get("segments", [])
        lines = []
        for seg in segments:
            speaker = seg.get("speakerId", "Unknown")
            start = seg.get("startTime", 0.0)
            end = seg.get("endTime", start)
            duration = max(end - start, 0.001)
            # Sanitize speaker ID for RTTM (no spaces)
            speaker_clean = speaker.replace(" ", "_").replace("(", "").replace(")", "")
            lines.append(
                f"SPEAKER {file_id} 1 {start:.3f} {duration:.3f} "
                f"<NA> <NA> {speaker_clean} <NA> <NA>"
            )
        return "\n".join(lines) + "\n" if lines else None
    finally:
        conn.close()


def process_corpus(corpus: str, data_dir: Path, output_dir: Path) -> None:
    """Process all audio files for a corpus."""
    corpus_data = data_dir / corpus / "audio"
    corpus_output = output_dir / corpus / "rttm"
    corpus_output.mkdir(parents=True, exist_ok=True)

    if not corpus_data.exists():
        print(f"  [skip] {corpus}: no audio in {corpus_data}")
        return

    audio_files = sorted(corpus_data.glob("*.wav"))
    if not audio_files:
        print(f"  [skip] {corpus}: no .wav files found")
        return

    print(f"\n=== Processing {corpus} ({len(audio_files)} files) ===")

    for i, audio_path in enumerate(audio_files, 1):
        file_id = audio_path.stem
        rttm_path = corpus_output / f"{file_id}.rttm"

        if rttm_path.exists():
            print(f"  [{i}/{len(audio_files)}] {file_id} [skip] (already processed)")
            continue

        print(f"  [{i}/{len(audio_files)}] {file_id}...", end=" ", flush=True)

        # Snapshot existing meetings before processing
        meetings_before = get_existing_meetings(MIMICSCRIBE_DB)

        t0 = time.time()
        success = run_mimicscribe(audio_path)
        elapsed = time.time() - t0

        if not success:
            print(f"[failed] ({elapsed:.1f}s)")
            continue

        # Find the new meeting
        meetings_after = get_existing_meetings(MIMICSCRIBE_DB)
        new_meetings = meetings_after - meetings_before

        if not new_meetings:
            print(f"[no meeting created] ({elapsed:.1f}s)")
            continue

        if len(new_meetings) > 1:
            print(f"[warning: {len(new_meetings)} meetings created, using first]", end=" ")

        # Extract RTTM from the newest meeting
        meeting_id = new_meetings.pop()
        rttm_content = extract_meeting_rttm(MIMICSCRIBE_DB, meeting_id, file_id)

        if rttm_content:
            rttm_path.write_text(rttm_content)
            n_segments = rttm_content.count("\n")
            print(f"[ok] {n_segments} segments ({elapsed:.1f}s)")
        else:
            print(f"[empty segments] ({elapsed:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="Run MimicScribe pipeline on benchmark audio")
    parser.add_argument(
        "--corpus",
        choices=["ami", "earnings21", "all"],
        default="all",
        help="Which corpus to process (default: all)",
    )
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout per file in seconds (default: 600)",
    )
    args = parser.parse_args()

    corpora = ["ami", "earnings21"] if args.corpus == "all" else [args.corpus]
    for corpus in corpora:
        process_corpus(corpus, args.data_dir, args.output_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
