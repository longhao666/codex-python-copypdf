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
    from PyPDF2._page import PageObject
except ImportError as exc:  # pragma: no cover - import guard
    print("Missing dependency PyPDF2. Run `pip install PyPDF2` first.", file=sys.stderr)
    raise


DEFAULT_PAGES_PER_SHEET = 1
DEFAULT_ORIENTATION = "portrait"


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
        default=None,
        help="Number of original pages to place onto a single output page (default: 1).",
    )
    parser.add_argument(
        "--nup-rows",
        type=int,
        help="Rows per sheet when using N-up layout (must be used with --nup-cols).",
    )
    parser.add_argument(
        "--nup-cols",
        type=int,
        help="Columns per sheet when using N-up layout (must be used with --nup-rows).",
    )
    parser.add_argument(
        "--orientation",
        choices=("portrait", "landscape"),
        default=DEFAULT_ORIENTATION,
        help="Orientation to use for N-up pages (portrait default; only applies when pages-per-sheet > 1).",
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


def load_page_refs(input_paths: list[Path]) -> tuple[list[tuple[PdfReader, int]], list[PdfReader]]:
    readers: list[PdfReader] = []
    page_refs: list[tuple[PdfReader, int]] = []
    for path in input_paths:
        reader = PdfReader(str(path))
        readers.append(reader)
        for index in range(len(reader.pages)):
            page_refs.append((reader, index))
    if not page_refs:
        raise ValueError("No PDF pages found in the provided inputs.")
    return page_refs, readers


def write_linear(page_refs: list[tuple[PdfReader, int]], output: Path) -> None:
    writer = PdfWriter()
    for reader, index in page_refs:
        writer.add_page(reader.pages[index])
    with output.open("wb") as fh:
        writer.write(fh)


def get_page_size(page) -> tuple[float, float]:
    mediabox = page.mediabox
    return float(mediabox.width), float(mediabox.height)


def write_nup(
    page_refs: list[tuple[PdfReader, int]],
    output: Path,
    pages_per_sheet: int,
    rows: int,
    cols: int,
    orientation: str,
) -> None:
    writer = PdfWriter()
    for start in range(0, len(page_refs), pages_per_sheet):
        chunk_refs = page_refs[start : start + pages_per_sheet]
        chunk_pages = [reader.pages[index] for reader, index in chunk_refs]
        base_width, base_height = get_page_size(chunk_pages[0])
        oriented_width, oriented_height = orient_dimensions(
            base_width, base_height, orientation
        )
        add_nup_page(
            writer,
            chunk_pages,
            oriented_width,
            oriented_height,
            rows,
            cols,
            orientation,
        )
    with output.open("wb") as fh:
        writer.write(fh)


def add_nup_page(
    writer: PdfWriter,
    chunk: list,
    page_width: float,
    page_height: float,
    rows: int,
    cols: int,
    orientation: str,
) -> None:
    canvas = PageObject.create_blank_page(width=page_width, height=page_height)
    cell_width = page_width / cols
    cell_height = page_height / rows
    for idx, src in enumerate(chunk):
        src_width, src_height = get_page_size(src)
        scale = min(cell_width / src_width, cell_height / src_height)
        if orientation == "portrait":
            col = idx // rows
            row_from_top = idx % rows
        else:
            row_from_top = idx // cols
            col = idx % cols
        row_from_bottom = rows - 1 - row_from_top
        offset_x = col * cell_width + (cell_width - src_width * scale) / 2
        # 将页面顶部与单元格顶部对齐，避免出现额外的上边距
        offset_y = row_from_bottom * cell_height + (cell_height - src_height * scale)
        ctm = (scale, 0, 0, scale, offset_x, offset_y)
        duplicated = PageObject.create_blank_page(width=src_width, height=src_height)
        duplicated.merge_page(src)
        duplicated.add_transformation(ctm)
        canvas.merge_page(duplicated)
    writer.add_page(canvas)


def resolve_nup_options(args: argparse.Namespace) -> tuple[int, int, int]:
    """Determine pages per sheet plus grid rows/cols."""
    pages_per_sheet = args.pages_per_sheet
    nup_rows = args.nup_rows
    nup_cols = args.nup_cols
    orientation = getattr(args, "orientation", DEFAULT_ORIENTATION)

    if pages_per_sheet is None and (nup_rows is None and nup_cols is None):
        pages_per_sheet = DEFAULT_PAGES_PER_SHEET

    if nup_rows is None and nup_cols is None:
        pages_per_sheet = ensure_positive_int(
            pages_per_sheet, "--pages-per-sheet must be a positive integer."
        )
        cols = math.ceil(math.sqrt(pages_per_sheet))
        rows = math.ceil(pages_per_sheet / cols)
        if (
            orientation == "portrait"
            and pages_per_sheet > 1
            and rows < cols
        ):
            rows, cols = cols, rows
        return pages_per_sheet, rows, cols

    if (nup_rows is None) != (nup_cols is None):
        raise ValueError("`--nup-rows` and `--nup-cols` must be used together.")

    rows = ensure_positive_int(nup_rows, "`--nup-rows` must be a positive integer.")
    cols = ensure_positive_int(nup_cols, "`--nup-cols` must be a positive integer.")

    if pages_per_sheet is None:
        pages_per_sheet = rows * cols
    else:
        pages_per_sheet = ensure_positive_int(
            pages_per_sheet, "--pages-per-sheet must be a positive integer."
        )
        if pages_per_sheet != rows * cols:
            raise ValueError(
                "`--pages-per-sheet` must equal rows * cols when specifying both."
            )

    return pages_per_sheet, rows, cols


def ensure_positive_int(value: int | None, message: str) -> int:
    if value is None or value < 1:
        raise ValueError(message)
    return value


def orient_dimensions(width: float, height: float, orientation: str) -> tuple[float, float]:
    """Return page dimensions adjusted for the requested orientation."""
    if orientation == "portrait":
        return (min(width, height), max(width, height))
    if orientation == "landscape":
        return (max(width, height), min(width, height))
    raise ValueError(f"Unsupported orientation: {orientation!r}")


def main() -> int:
    args = parse_args()
    try:
        input_paths, output_path = validate_paths(args)
        pages_per_sheet, rows, cols = resolve_nup_options(args)
        page_refs, readers = load_page_refs(input_paths)
        _ = readers  # Keep references alive until writing completes.
        if pages_per_sheet == 1:
            write_linear(page_refs, output_path)
        else:
            write_nup(
                page_refs,
                output_path,
                pages_per_sheet,
                rows,
                cols,
                args.orientation,
            )
    except Exception as exc:  # Print descriptive errors for the user
        print(f"Merge failed: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
