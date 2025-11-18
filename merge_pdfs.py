#!/usr/bin/env python3
"""
Simple CLI utility for merging multiple PDF files.

Example:
    python merge_pdfs.py --output merged.pdf 1.pdf 2.pdf 3.pdf

Dependency:
    pip install PyPDF2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PyPDF2 import PdfMerger
except ImportError as exc:  # pragma: no cover - import guard
    print("Missing dependency PyPDF2. Run `pip install PyPDF2` first.", file=sys.stderr)
    raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge multiple PDF files into a single PDF in the given order."
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output PDF file path.",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Optional explicit PDF file paths appended in the given order.",
    )
    parser.add_argument(
        "--input-dir",
        help="Directory containing PDF files to merge (files sorted lexicographically).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the output file if it already exists.",
    )
    return parser.parse_args()


def validate_paths(args: argparse.Namespace) -> tuple[list[Path], Path]:
    output_path = Path(args.output).expanduser().resolve()
    if output_path.exists() and not args.overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path} (use --overwrite to replace it)."
        )

    output_dir = output_path.parent
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    input_paths: list[Path] = []
    if args.input_dir:
        directory = Path(args.input_dir).expanduser().resolve()
        if not directory.is_dir():
            raise NotADirectoryError(f"Input directory does not exist: {directory}")
        dir_pdfs = sorted(
            (
                path
                for path in directory.iterdir()
                if path.is_file() and path.suffix.lower() == ".pdf"
            ),
            key=lambda path: path.name.lower(),
        )
        dir_pdfs = [path for path in dir_pdfs if path != output_path]
        if not dir_pdfs:
            raise FileNotFoundError(f"No PDF files found in directory: {directory}")
        input_paths.extend(dir_pdfs)

    for raw in args.inputs:
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Input file is not a PDF: {path}")
        input_paths.append(path)

    if len(input_paths) < 2:
        raise ValueError(
            "Provide at least two PDF files via arguments or --input-dir."
        )

    return input_paths, output_path


def merge_pdfs(inputs: list[Path], output: Path) -> None:
    merger = PdfMerger()
    try:
        for pdf in inputs:
            merger.append(str(pdf))
        with output.open("wb") as fh:
            merger.write(fh)
    finally:
        merger.close()


def main() -> int:
    args = parse_args()
    try:
        input_paths, output_path = validate_paths(args)
        merge_pdfs(input_paths, output_path)
    except Exception as exc:  # Print descriptive errors for the user
        print(f"Merge failed: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
