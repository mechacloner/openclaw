#!/usr/bin/env python3
"""
Reorder a project register into strict numerical sequence by project number.

Handles:
  * Plain numbers with any prefix, e.g. AKK.PO.001, 019, PO-19, 1
  * Suffixed / sub-numbered entries, e.g. "019 (A)", "019 (B)", "019A", "19-B"
    -> the base number defines position, the suffix defines sub-order,
       so 019 (A) sorts immediately before 019 (B), and both sit between
       018 and 020. The suffix text itself is preserved, never rewritten.

Usage:
    python3 tools/reorder_projects.py INPUT [-o OUTPUT] [--column NAME]
        [--sheet NAME] [--keep-order]

INPUT may be .xlsx, .xlsm, .csv or .txt. Extra columns are carried through
untouched and no values are modified -- rows are only re-sequenced.

A .txt input is read as a pasted list: one entry per line, where an entry is
either just a project number ("AKK.PO.019 (A)") or a number then a name
separated by a comma / tab / " - " ("AKK.PO.019 (A), Sub-station upgrade").
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# A project number = optional prefix + digits + optional suffix.
# Prefixes may contain letters and separators (. - / _ space), e.g. AKK.PO.
NUMBER_RE = re.compile(
    r"""^\s*
    (?P<prefix>[A-Za-z][A-Za-z0-9.\-/_ ]*?)?      # optional alphabetic prefix
    (?P<num>\d+)                                   # the base number
    \s*
    (?:\(\s*(?P<paren>[A-Za-z0-9]{1,4})\s*\)|     # (A) style suffix
       [\-\s]?(?P<plain>[A-Za-z]{1,4})(?![A-Za-z0-9]))?   # A / -A / 019A style
    \s*$""",
    re.VERBOSE,
)

# Suffix -> sort key. Numeric suffixes sort as ints, letters as letters.
def _suffix_key(suffix: str):
    if not suffix:
        return (0, 0, "")
    s = suffix.strip().upper()
    if s.isdigit():
        return (1, int(s), "")
    return (2, 0, s)


def parse_project_no(value) -> tuple:
    """Return a sort key for one project-number cell, plus a display flag."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    m = NUMBER_RE.match(text)
    if not m:
        return None
    base = int(m.group("num"))
    suffix = m.group("paren") or m.group("plain") or ""
    prefix = (m.group("prefix") or "").strip().upper()
    return (prefix, base, _suffix_key(suffix), text.upper())


def sort_key_for(value) -> tuple:
    """Total sort order: numbered rows first in numeric order, others last."""
    parsed = parse_project_no(value)
    if parsed is None:
        return (1, "", 0, (0, 0, ""), str(value).upper())
    prefix, base, suf, text = parsed
    return (0, prefix, base, suf, text)


def read_table(path: Path, sheet: str | None):
    """Read the whole sheet as a list of rows (lists of cell values)."""
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as fh:
            return [row for row in csv.reader(fh)]

    if path.suffix.lower() in (".txt", ".list", ".md"):
        return read_pasted_list(path)

    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet else wb[wb.sheetnames[0]]
    rows = []
    for row in ws.iter_rows(values_only=True):
        rows.append(["" if c is None else c for c in row])
    return rows


def read_pasted_list(path: Path):
    """Parse a pasted list: one project per line, number then optional name."""
    rows = []
    with path.open(encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # Split "NUMBER <sep> NAME" on the first comma, tab, or " - ".
            parts = None
            for sep in (",", "\t", ";", " – ", " — ", " - ", "  "):
                if sep in line:
                    parts = [p.strip() for p in line.split(sep, 1)]
                    break
            if parts is None:
                parts = [line]
            rows.append(parts)
    if not rows:
        return rows
    width = max(len(r) for r in rows)
    return [r + [""] * (width - len(r)) for r in rows]


def detect_column(rows, header_row_idx: int, names) -> int:
    """Find the project-number column by header text, else by content."""
    if header_row_idx is not None:
        header = [str(c).strip().lower() for c in rows[header_row_idx]]
        for idx, cell in enumerate(header):
            for want in names:
                if want in cell:
                    return idx
    # Fall back: the column where the most cells parse as a project number.
    width = max(len(r) for r in rows)
    best, best_hits = 0, -1
    for idx in range(width):
        hits = sum(
            1 for r in rows[header_row_idx + 1:] if idx < len(r) and parse_project_no(r[idx])
        )
        if hits > best_hits:
            best, best_hits = idx, hits
    return best


def find_header_row(rows, names) -> int | None:
    """Locate the header row (first row mentioning 'no'/'number'/'project')."""
    for i, row in enumerate(rows[:25]):
        cells = [str(c).strip().lower() for c in row]
        if any(any(n in c for n in names) for c in cells if c):
            return i
    return None


def fmt_value(v, header: str):
    """Render a value for Excel, keeping leading zeros on the No. column only."""
    if v == "" or v is None:
        return ""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if float(v).is_integer():
            return int(v)
        return float(v)
    return str(v)


def write_excel(rows, out_path: Path, header_row_idx):
    wb = Workbook()
    ws = wb.active
    ws.title = "Projects"

    for r in rows:
        ws.append(r)

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="1F4E79")
    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    max_col = max((len(r) for r in rows), default=1)
    max_row = len(rows)

    for row in ws.iter_rows(min_row=1, max_row=max_row, max_col=max_col):
        for cell in row:
            cell.border = border
            if header_row_idx is not None and cell.row == header_row_idx + 1:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Column widths sized to content.
    for idx in range(1, max_col + 1):
        longest = 0
        for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=idx, max_col=idx):
            for cell in row:
                longest = max(longest, len(str(cell.value)) if cell.value is not None else 0)
        ws.column_dimensions[get_column_letter(idx)].width = min(max(longest + 3, 10), 60)

    if header_row_idx is not None:
        ws.freeze_panes = ws.cell(row=header_row_idx + 2, column=1)
        ws.auto_filter.ref = f"A{header_row_idx + 1}:{get_column_letter(max_col)}{max_row}"

    wb.save(out_path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--column", default=None, help="project-number column letter or 1-based index")
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--header-row", type=int, default=None, help="1-based header row number")
    ap.add_argument("--no-header", action="store_true", help="data has no header row")
    ap.add_argument("--keep-order", action="store_true", help="only sort, do not touch anything else")
    args = ap.parse_args(argv)

    if not args.input.exists():
        ap.error(f"input not found: {args.input}")

    out = args.output or args.input.with_name(args.input.stem + " - reordered.xlsx")
    rows = read_table(args.input, args.sheet)
    rows = [r for r in rows if any(str(c).strip() for c in r)]
    if not rows:
        ap.error("no rows found in input")

    header_idx = None if args.no_header else (
        args.header_row - 1 if args.header_row else find_header_row(rows, ("project no", "proj no", "no.", "number", "code", "id"))
    )

    pasted = args.input.suffix.lower() in (".txt", ".list", ".md")
    if pasted and args.header_row is None and not args.no_header:
        # A pasted list has no header line; add usable column titles below.
        header_idx = None
        width = max(len(r) for r in rows)
        titles = ["Project No.", "Description", "Remarks", "Notes"]
        header = [titles[i] if i < len(titles) else f"Column {i + 1}" for i in range(width)]
        rows = [header] + rows
        header_idx = 0

    if args.column:
        token = args.column.strip().upper()
        if token.isdigit():
            col = int(token) - 1
        else:
            col = ord(token[0]) - ord("A")
    else:
        col = detect_column(rows, header_idx, ("project no", "proj no", "no.", "number", "code", "id"))

    header = rows[header_idx] if header_idx is not None else None
    body = rows[header_idx + 1:] if header_idx is not None else rows

    parsed = [(sort_key_for(r[col] if col < len(r) else ""), i, r) for i, r in enumerate(body)]
    parsed.sort(key=lambda t: (t[0], t[1]))
    ordered = [r for _, _, r in parsed]

    unparsed = [r for r in ordered if parse_project_no(r[col] if col < len(r) else "") is None]
    if unparsed:
        print(f"note: {len(unparsed)} row(s) had no parseable project number and were kept at the end", file=sys.stderr)

    final = ([header] if header is not None else []) + ordered
    write_excel(final, out, header_idx if header is not None else None)

    print(f"rows sorted : {len(ordered)}")
    print(f"number column: {get_column_letter(col + 1)}" + (f" ({header[col]!r})" if header and col < len(header) else ""))
    print(f"output      : {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
