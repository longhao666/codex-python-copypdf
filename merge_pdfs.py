#!/usr/bin/env python3
"""
Simple CLI utility for merging multiple PDF files.

Example:
    # Merge explicit files
    python merge_pdfs.py --output merged.pdf 1.pdf 2.pdf 3.pdf

    # Merge an entire directory with 4-up layout
    python merge_pdfs.py --input-dir ./docs --output merged.pdf --pages-per-sheet 4

Dependency:
    pip install PyPDF2
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
from PyPDF2 import PdfReader, PdfWriter
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
        "--pages-per-sheet",
        type=int,
        default=1,
        help="Number of original pages to place onto a single output page (default: 1).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the output file if it already exists.",
    )
    return parser.parse_args()


def validate_paths(args: argparse.Namespace) -> tuple[list[Path], Path]:
    ensure_pages_per_sheet(args.pages_per_sheet)

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


def ensure_pages_per_sheet(value: int) -> int:
    if value < 1:
        raise ValueError("`--pages-per-sheet` must be a positive integer.")
    return value


def load_pages(input_paths: list[Path]) -> tuple[list, list[PdfReader]]:
    readers: list[PdfReader] = []
    pages: list = []
    for path in input_paths:
        reader = PdfReader(str(path))
        readers.append(reader)
        pages.extend(reader.pages)
    if not pages:
        raise ValueError("No PDF pages found in the provided inputs.")
    return pages, readers


def write_linear(pages: list, output: Path) -> None:
    writer = PdfWriter()
    for page in pages:
        writer.add_page(page)
    with output.open("wb") as fh:
        writer.write(fh)


def get_page_size(page) -> tuple[float, float]:
    mediabox = page.mediabox
    return float(mediabox.width), float(mediabox.height)


def write_nup(pages: list, output: Path, pages_per_sheet: int) -> None:
    writer = PdfWriter()
    cols = math.ceil(math.sqrt(pages_per_sheet))
    rows = math.ceil(pages_per_sheet / cols)
    for start in range(0, len(pages), pages_per_sheet):
        chunk = pages[start : start + pages_per_sheet]
        base_width, base_height = get_page_size(chunk[0])
        add_nup_page(writer, chunk, base_width, base_height, rows, cols)
    with output.open("wb") as fh:
        writer.write(fh)


def add_nup_page(
    writer: PdfWriter,
    chunk: list,
    page_width: float,
    page_height: float,
    rows: int,
    cols: int,
) -> None:
    canvas = writer.add_blank_page(width=page_width, height=page_height)
    cell_width = page_width / cols
    cell_height = page_height / rows
    for idx, src in enumerate(chunk):
        src_width, src_height = get_page_size(src)
        scale = min(cell_width / src_width, cell_height / src_height)
        row_from_top = idx // cols
        col = idx % cols
        row_from_bottom = rows - 1 - row_from_top
        offset_x = col * cell_width + (cell_width - src_width * scale) / 2
        offset_y = row_from_bottom * cell_height + (cell_height - src_height * scale) / 2
        ctm = (scale, 0, 0, scale, offset_x, offset_y)
        canvas.merge_transformed_page(src, ctm)


def main() -> int:
    args = parse_args()
    try:
        input_paths, output_path = validate_paths(args)
        pages_per_sheet = ensure_pages_per_sheet(args.pages_per_sheet)
        pages, readers = load_pages(input_paths)
        _ = readers  # Keep references alive until writing completes.
        if pages_per_sheet == 1:
            write_linear(pages, output_path)
        else:
            write_nup(pages, output_path, pages_per_sheet)
    except Exception as exc:  # Print descriptive errors for the user
        print(f"Merge failed: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
