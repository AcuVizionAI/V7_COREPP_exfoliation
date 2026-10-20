#!/usr/bin/env python3
"""Compare two JARVIS exfoliation prediction ZIPs without loading model code.

Usage: python verify.py SUBMITTED.csv.zip REPRODUCED.csv.zip [--atol 1e-4]

Both archives must contain one CSV with exactly 81 unique, ordered IDs and
the columns ``id,prediction``. Exit 0 means all checks passed; exit 1 means a
comparison or input check failed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import math
import zipfile
from pathlib import Path


EXPECTED_ROWS = 81
EXPECTED_COLUMNS = ["id", "prediction"]


class VerificationError(ValueError):
    """An archive cannot be accepted as a benchmark prediction file."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> list[tuple[str, float]]:
    with zipfile.ZipFile(path) as archive:
        members = [member for member in archive.infolist()
                   if not member.is_dir() and member.filename.lower().endswith(".csv")]
        if len(members) != 1:
            raise VerificationError(f"{path}: expected exactly one CSV member")
        if members[0].file_size > 1_000_000:
            raise VerificationError(f"{path}: CSV member is unexpectedly large")
        contents = archive.read(members[0]).decode("utf-8")

    reader = csv.DictReader(io.StringIO(contents, newline=""), strict=True)
    if reader.fieldnames != EXPECTED_COLUMNS:
        raise VerificationError(f"{path}: expected columns id,prediction in that order")

    rows: list[tuple[str, float]] = []
    seen: set[str] = set()
    for row_number, row in enumerate(reader, start=2):
        if set(row) != set(EXPECTED_COLUMNS) or any(value is None for value in row.values()):
            raise VerificationError(f"{path}: malformed CSV row {row_number}")
        record_id = row["id"]
        if not record_id or record_id != record_id.strip():
            raise VerificationError(f"{path}: blank or padded ID on row {row_number}")
        if record_id in seen:
            raise VerificationError(f"{path}: duplicate ID on row {row_number}: {record_id}")
        seen.add(record_id)
        try:
            prediction = float(row["prediction"])
        except ValueError as exc:
            raise VerificationError(f"{path}: invalid prediction on row {row_number}") from exc
        if not math.isfinite(prediction):
            raise VerificationError(f"{path}: non-finite prediction on row {row_number}")
        rows.append((record_id, prediction))
        if len(rows) > EXPECTED_ROWS:
            raise VerificationError(f"{path}: more than {EXPECTED_ROWS} rows")

    if len(rows) != EXPECTED_ROWS:
        raise VerificationError(f"{path}: expected {EXPECTED_ROWS} rows, found {len(rows)}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submitted", type=Path)
    parser.add_argument("reproduced", type=Path)
    parser.add_argument("--atol", type=float, default=1e-4,
                        help="maximum allowed absolute prediction difference")
    args = parser.parse_args()

    if not math.isfinite(args.atol) or args.atol < 0:
        print("INVALID ATOL: --atol must be finite and nonnegative")
        print("RESULT: FAIL")
        return 1

    try:
        sub_hash = sha256(args.submitted)
        rep_hash = sha256(args.reproduced)
        submitted = load(args.submitted)
        reproduced = load(args.reproduced)
    except (OSError, zipfile.BadZipFile, UnicodeError, csv.Error, VerificationError) as exc:
        print(f"INVALID INPUT: {exc}")
        print("RESULT: FAIL")
        return 1

    print(f"submitted  : {args.submitted}  sha256={sub_hash}")
    print(f"reproduced : {args.reproduced}  sha256={rep_hash}")

    sub_ids = [record_id for record_id, _ in submitted]
    rep_ids = [record_id for record_id, _ in reproduced]
    if sub_ids != rep_ids:
        missing = sorted(set(sub_ids) - set(rep_ids))
        extra = sorted(set(rep_ids) - set(sub_ids))
        if missing or extra:
            print(f"ID SET MISMATCH: missing={missing[:10]} extra={extra[:10]}")
        else:
            print("ID ORDER MISMATCH: the same IDs are in a different order")
        print("RESULT: FAIL")
        return 1

    deltas = [abs(reproduced[i][1] - submitted[i][1])
              for i in range(EXPECTED_ROWS)]
    if not all(math.isfinite(delta) for delta in deltas):
        print("NON-FINITE DIFFERENCE: prediction subtraction overflowed")
        print("RESULT: FAIL")
        return 1
    worst_index = max(range(EXPECTED_ROWS), key=deltas.__getitem__)
    mean_abs = math.fsum(delta / EXPECTED_ROWS for delta in deltas)
    n_over = sum(delta > args.atol for delta in deltas)
    print(f"rows compared : {EXPECTED_ROWS}")
    print(f"max |delta|   : {deltas[worst_index]:.12g}  (id={sub_ids[worst_index]})")
    print(f"mean |delta|  : {mean_abs:.12g}")
    print(f"rows > atol={args.atol:g}: {n_over}")
    print("RESULT:", "PASS" if n_over == 0 else "FAIL")
    return 0 if n_over == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
