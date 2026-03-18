#!/usr/bin/env python3
"""Vendor VTK Python payload into a built wheel and strip external vtk metadata.

This script is platform-neutral and is intended to run before wheel repair
(e.g. auditwheel/delocate) so binary dependencies of vendored vtkmodules are
captured by the repair step.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def parse_wheel_python_version(wheel_path: Path) -> tuple[int, int]:
    match = re.search(r"-cp(\d+)-cp\d+-", wheel_path.name)
    if not match:
        raise ValueError(f"Cannot parse Python tag from wheel name: {wheel_path.name}")
    tag = match.group(1)
    if len(tag) < 2:
        raise ValueError(f"Unsupported Python tag: cp{tag}")
    major = int(tag[0])
    minor = int(tag[1:])
    return major, minor


def vendor_vtk_payload(root: Path, *, expected_py: tuple[int, int]) -> list[Path]:
    if sys.version_info[:2] != expected_py:
        raise RuntimeError(
            "Patch interpreter version does not match wheel tag: "
            f"interpreter={sys.version_info.major}.{sys.version_info.minor}, "
            f"wheel={expected_py[0]}.{expected_py[1]}"
        )

    try:
        import vtk  # type: ignore
        import vtkmodules  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("vtk/vtkmodules not found in build environment") from exc

    vtk_py_src = Path(vtk.__file__).resolve()
    vtkmodules_src = Path(vtkmodules.__file__).resolve().parent

    bundle_dir = root / "vmtk" / ".vtk"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []

    vtk_py_dest = bundle_dir / "vtk.py"
    shutil.copy2(vtk_py_src, vtk_py_dest)
    copied.append(vtk_py_dest)

    vtkmodules_dest = bundle_dir / "vtkmodules"
    if vtkmodules_dest.exists():
        shutil.rmtree(vtkmodules_dest)
    shutil.copytree(vtkmodules_src, vtkmodules_dest)
    copied.append(vtkmodules_dest)

    # Linux VTK wheels often store shared libs in a sibling "vtk.libs" folder.
    vtk_libs_src = vtk_py_src.parent / "vtk.libs"
    if vtk_libs_src.exists():
        vtk_libs_dest = bundle_dir / "vtk.libs"
        if vtk_libs_dest.exists():
            shutil.rmtree(vtk_libs_dest)
        shutil.copytree(vtk_libs_src, vtk_libs_dest)
        copied.append(vtk_libs_dest)

    return copied


def strip_vtk_requirement(root: Path) -> int:
    metadata_files = list(root.rglob("*.dist-info/METADATA"))
    if len(metadata_files) != 1:
        raise RuntimeError(f"Expected exactly one METADATA file, found {len(metadata_files)}")

    metadata_path = metadata_files[0]
    lines = metadata_path.read_text(encoding="utf-8").splitlines()
    kept: list[str] = []
    removed = 0
    for line in lines:
        if line.startswith("Requires-Dist: vtk"):
            removed += 1
            continue
        kept.append(line)
    metadata_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return removed


def compute_record_row(file_path: Path, root: Path) -> tuple[str, str, str]:
    rel = file_path.relative_to(root).as_posix()
    data = file_path.read_bytes()
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
    return rel, f"sha256={digest}", str(len(data))


def rewrite_record(root: Path) -> Path:
    records = list(root.rglob("*.dist-info/RECORD"))
    if len(records) != 1:
        raise RuntimeError(f"Expected exactly one RECORD file, found {len(records)}")

    record_path = records[0]
    record_rel = record_path.relative_to(root).as_posix()

    rows: list[tuple[str, str, str]] = []
    for file_path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = file_path.relative_to(root).as_posix()
        if rel == record_rel:
            continue
        rows.append(compute_record_row(file_path, root))
    rows.append((record_rel, "", ""))

    with record_path.open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)
    return record_path


def repack_wheel(unpack_dir: Path, wheel_path: Path) -> None:
    tmp_wheel = wheel_path.with_suffix(wheel_path.suffix + ".tmp")
    with ZipFile(tmp_wheel, "w", compression=ZIP_DEFLATED) as zf:
        for file_path in sorted(p for p in unpack_dir.rglob("*") if p.is_file()):
            arcname = file_path.relative_to(unpack_dir).as_posix()
            zf.write(file_path, arcname)
    tmp_wheel.replace(wheel_path)


def patch_wheel(wheel_path: Path) -> None:
    major, minor = parse_wheel_python_version(wheel_path)

    with tempfile.TemporaryDirectory() as td:
        unpack_dir = Path(td) / "wheel"
        with ZipFile(wheel_path) as zf:
            zf.extractall(unpack_dir)

        copied = vendor_vtk_payload(unpack_dir, expected_py=(major, minor))
        removed_requirements = strip_vtk_requirement(unpack_dir)
        record_path = rewrite_record(unpack_dir)
        repack_wheel(unpack_dir, wheel_path)

    for path in copied:
        print(f"[vendor-vtk] vendored: {path}")
    print(f"[vendor-vtk] removed metadata vtk requirements: {removed_requirements}")
    print(f"[vendor-vtk] updated RECORD: {record_path.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path, help="Path to built wheel")
    args = parser.parse_args()

    wheel_path = args.wheel.resolve()
    if not wheel_path.exists():
        print(f"Wheel not found: {wheel_path}", file=sys.stderr)
        return 1

    patch_wheel(wheel_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
