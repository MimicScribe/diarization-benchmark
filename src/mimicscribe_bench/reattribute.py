"""Re-attribute speaker segments using alternative LLMs via OpenRouter.

Takes pre-attribution segments (saved by MimicScribe during file import)
and sends them through the same speaker attribution prompt to a different
LLM, producing hypothesis RTTMs for comparison against Gemini results.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"
RAW_SEGMENTS_DIR = OUTPUT_DIR / "raw_segments"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "qwen3.5-9b": "qwen/qwen3.5-9b",
    "qwen3.5-35b": "qwen/qwen3.5-35b-a3b",
    "qwen3.5-397b": "qwen/qwen3.5-397b-a17b",
}

# Speaker attribution system instruction — loaded from a local file not tracked in git.
# Create attribution_prompt.txt with your own prompt, or sync from the production codebase.
# See AGENTS.md for setup instructions.
_PROMPT_PATH = Path(__file__).resolve().parents[2] / "attribution_prompt.txt"


def _load_attribution_prompt() -> str:
    if not _PROMPT_PATH.exists():
        print(
            f"Error: {_PROMPT_PATH} not found.\n"
            "This file contains the speaker attribution system instruction.\n"
            "See benchmark/AGENTS.md for setup instructions.",
            file=sys.stderr,
        )
        sys.exit(1)
    return _PROMPT_PATH.read_text().strip()


def load_api_key() -> str:
    """Load OpenRouter API key from environment or .env file."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    print("Error: OPENROUTER_API_KEY not found in environment or .env", file=sys.stderr)
    sys.exit(1)


def call_openrouter(
    model_id: str,
    system: str,
    user_message: str,
    api_key: str,
    timeout: int = 120,
) -> dict | None:
    """Call OpenRouter API and return parsed JSON response."""
    payload = json.dumps({
        "model": model_id,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.1,
        "max_tokens": 32768,
        "response_format": {"type": "json_object"},
    }).encode()

    req = Request(
        OPENROUTER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mimicscribe.app",
        },
    )

    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]
        if not content:
            print(f"    [error] Empty response content")
            return None
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        # Strip thinking tags if present (Qwen3 uses <think>...</think>)
        if "<think>" in content:
            think_end = content.find("</think>")
            if think_end != -1:
                content = content[think_end + len("</think>"):].strip()
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"    [error] JSON parse failed: {e}")
        return None
    except (HTTPError, KeyError, IndexError) as e:
        print(f"    [error] API call failed: {e}")
        return None


def build_user_message(raw_data: dict) -> str:
    """Build the attribution user message from raw segments data."""
    duration_minutes = int(raw_data["duration_seconds"] / 60)
    segments = raw_data["segments"]
    segments_json = json.dumps(segments, indent=2)
    return f'<TRANSCRIPT duration_minutes="{duration_minutes}">\n{segments_json}\n</TRANSCRIPT>'


def attribution_to_rttm(response: dict, file_id: str) -> str:
    """Convert attribution response segments to RTTM format."""
    lines = []
    for seg in response.get("segments", []):
        speaker = seg.get("speakerId", "Unknown")
        start = seg.get("startTime", 0.0)
        end = seg.get("endTime", start)
        duration = max(end - start, 0.001)
        speaker_clean = speaker.replace(" ", "_").replace("(", "").replace(")", "")
        lines.append(
            f"SPEAKER {file_id} 1 {start:.3f} {duration:.3f} "
            f"<NA> <NA> {speaker_clean} <NA> <NA>"
        )
    return "\n".join(lines) + "\n" if lines else ""


def process_file(
    raw_path: Path,
    model_key: str,
    model_id: str,
    api_key: str,
    output_dir: Path,
    attribution_prompt: str,
) -> bool:
    """Process one raw segments file through the alternative LLM."""
    raw_data = json.loads(raw_path.read_text())
    file_id = raw_path.stem

    rttm_path = output_dir / f"{file_id}.rttm"
    if rttm_path.exists():
        print(f"  [{file_id}] [skip] (already processed)")
        return True

    user_message = build_user_message(raw_data)
    n_segments = len(raw_data["segments"])

    print(f"  [{file_id}] {n_segments} segments, {model_key}...", end=" ", flush=True)
    t0 = time.time()

    response = call_openrouter(model_id, attribution_prompt, user_message, api_key)
    elapsed = time.time() - t0

    if not response:
        print(f"[failed] ({elapsed:.1f}s)")
        return False

    rttm = attribution_to_rttm(response, file_id)
    if not rttm:
        print(f"[empty response] ({elapsed:.1f}s)")
        return False

    rttm_path.write_text(rttm)
    n_out = rttm.count("\n")
    mapping = response.get("speakerMapping", [])
    mapping_str = ", ".join(f"{m['from']}→{m['to']}" for m in mapping[:5])
    print(f"[ok] {n_out} segments ({elapsed:.1f}s) [{mapping_str}]")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Re-attribute speaker segments using alternative LLMs"
    )
    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()),
        default="qwen3.5-35b",
        help="Model to use (default: qwen3.5-35b)",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_SEGMENTS_DIR,
        help="Directory containing raw segment JSON files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for hypothesis RTTMs (default: output/<model>/rttm)",
    )
    args = parser.parse_args()

    model_key = args.model
    model_id = MODELS[model_key]
    api_key = load_api_key()

    out_dir = args.output_dir or OUTPUT_DIR / model_key / "rttm"
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(args.raw_dir.glob("*.json"))
    if not raw_files:
        print(f"No raw segment files found in {args.raw_dir}")
        print("Run the MimicScribe pipeline first to generate raw segments.")
        sys.exit(1)

    attribution_prompt = _load_attribution_prompt()

    print(f"\n=== Re-attributing with {model_key} ({model_id}) ===")
    print(f"  Input: {args.raw_dir} ({len(raw_files)} files)")
    print(f"  Output: {out_dir}")
    print()

    success = 0
    for raw_path in raw_files:
        if process_file(raw_path, model_key, model_id, api_key, out_dir, attribution_prompt):
            success += 1

    print(f"\n{success}/{len(raw_files)} files processed successfully.")


if __name__ == "__main__":
    main()
