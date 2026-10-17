#!/usr/bin/env python3
"""Build the public ChatGPT plugin ZIP from an explicit portable allowlist."""

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "cloudbees-unify-chatgpt.zip"
ROOT_FILES = ("plugin.json", "mcp.json", "README.md", "LICENSE")


def portable_files() -> list[Path]:
    files = [ROOT / relative_path for relative_path in ROOT_FILES]
    files.extend(sorted((ROOT / "skills").glob("*/SKILL.md")))
    files.extend(sorted((ROOT / "skills").glob("*/agents/openai.yaml")))
    return files


def build(output_path: Path) -> None:
    missing = [path for path in portable_files() if not path.is_file()]
    if missing:
        missing_names = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise FileNotFoundError(f"Missing required package files: {missing_names}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in portable_files():
            archive.write(path, path.relative_to(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination ZIP path.",
    )
    args = parser.parse_args()

    try:
        build(args.output.resolve())
    except (FileNotFoundError, OSError) as error:
        parser.error(str(error))

    print(f"Built ChatGPT plugin: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
