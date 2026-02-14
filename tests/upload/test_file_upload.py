#!/usr/bin/env python3
"""Smoke test for multipart file uploads to backend.

The script creates temporary files of different formats and sends them to the
configured backend endpoint as multipart/form-data.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Iterable

import requests


DEFAULT_TYPES = ["txt", "json", "csv", "png", "pdf"]


def _write_sample_file(file_path: Path, fmt: str) -> None:
    if fmt == "txt":
        file_path.write_text("upload smoke test\n", encoding="utf-8")
    elif fmt == "json":
        file_path.write_text(json.dumps({"ping": "upload-test"}), encoding="utf-8")
    elif fmt == "csv":
        file_path.write_text("id,name\n1,test\n", encoding="utf-8")
    elif fmt == "png":
        # Minimal PNG header + IEND chunk for smoke testing transport.
        file_path.write_bytes(
            bytes.fromhex(
                "89504E470D0A1A0A"
                "0000000D49484452000000010000000108060000001F15C489"
                "0000000049454E44AE426082"
            )
        )
    elif fmt == "pdf":
        file_path.write_bytes(
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] >>\nendobj\n"
            b"xref\n0 4\n0000000000 65535 f \n"
            b"trailer\n<< /Root 1 0 R /Size 4 >>\nstartxref\n0\n%%EOF\n"
        )
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def _upload(base_url: str, endpoint: str, field_name: str, file_path: Path, timeout: float) -> tuple[int, str]:
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    with file_path.open("rb") as payload:
        resp = requests.post(
            url,
            files={field_name: (file_path.name, payload)},
            timeout=timeout,
        )
    return resp.status_code, resp.text[:300]


def run(base_url: str, endpoint: str, field_name: str, formats: Iterable[str], timeout: float) -> int:
    failures = []

    with tempfile.TemporaryDirectory(prefix="upload-smoke-") as tmp:
        tmpdir = Path(tmp)

        for fmt in formats:
            sample_file = tmpdir / f"sample.{fmt}"
            _write_sample_file(sample_file, fmt)

            try:
                status, body_head = _upload(base_url, endpoint, field_name, sample_file, timeout)
            except Exception as exc:  # network/connection errors should fail test run
                failures.append((fmt, f"request_error: {exc}"))
                continue

            if 200 <= status < 300:
                print(f"[PASS] {fmt}: HTTP {status}")
            else:
                failures.append((fmt, f"HTTP {status}; body={body_head!r}"))

    if failures:
        print("\n[FAIL] Upload checks failed:")
        for fmt, reason in failures:
            print(f"  - {fmt}: {reason}")
        return 1

    print("\n[OK] All upload checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload smoke tests for multiple file formats")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--endpoint", default="/upload", help="Upload endpoint path")
    parser.add_argument("--field-name", default="file", help="Multipart field name")
    parser.add_argument(
        "--formats",
        default=",".join(DEFAULT_TYPES),
        help=f"Comma-separated extensions. Default: {','.join(DEFAULT_TYPES)}",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")

    args = parser.parse_args()
    formats = [item.strip() for item in args.formats.split(",") if item.strip()]
    return run(args.base_url, args.endpoint, args.field_name, formats, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
