#!/usr/bin/env python3
"""Patch repaired macOS wheels into a fully self-contained VMTK runtime.

The script performs three key post-processing steps on repaired wheels:
1) Vendor ``vtk.py`` and the full ``vtkmodules`` package into ``vmtk/.vtk``.
2) Rewire VMTK binaries to use vendored ``vmtk/.vtk/vtkmodules/.dylibs`` and the
   interpreter's Python runtime path.
3) Remove duplicated ``vmtk/.dylibs`` payload and drop ``Requires-Dist: vtk``.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import re
import shutil
import subprocess
import sys
import sysconfig
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


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def read_macho_dependencies(binary_path: Path) -> list[str]:
    out = run(["otool", "-L", str(binary_path)], check=False)
    if out.returncode != 0:
        return []
    deps: list[str] = []
    for line in out.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        dep = line.split(" (", 1)[0]
        deps.append(dep)
    return deps


def should_rewrite_python_dependency(dep: str) -> bool:
    if dep == "@loader_path/.dylibs/Python":
        return True
    if dep.startswith("@loader_path/.dylibs/libpython"):
        return True
    if "Python.framework" in dep and dep.endswith("/Python"):
        return True
    if Path(dep).name.startswith("libpython"):
        return True
    return False


def should_rewire_to_vtkmodules(dep: str) -> bool:
    libname = Path(dep).name
    if not libname.startswith("libvtk"):
        return False
    if libname.startswith("libvtkvmtk"):
        return False
    return True


def infer_target_python_runtime(expected_py: tuple[int, int]) -> str:
    major, minor = expected_py
    # Use the real interpreter location to detect the canonical runtime layout.
    # cibuildwheel macOS uses framework Python ("Python"), while uv/Homebrew
    # typically expose "libpythonX.Y.dylib" in ../lib.
    exe = Path(sys.executable).resolve()
    exe_prefix = exe.parent.parent
    ldlib = (sysconfig.get_config_var("LDLIBRARY") or "").strip()

    candidates: list[tuple[Path, str]] = []
    if ldlib and (ldlib == "Python" or ldlib.endswith(".dylib")):
        candidates.append((exe_prefix / "lib" / ldlib, f"@executable_path/../lib/{ldlib}"))
        candidates.append((exe_prefix / ldlib, f"@executable_path/../{ldlib}"))

    # Explicit framework fallback.
    candidates.append((exe_prefix / "Python", "@executable_path/../Python"))
    # Generic fallback for non-framework builds.
    candidates.append(
        (
            exe_prefix / "lib" / f"libpython{major}.{minor}.dylib",
            f"@executable_path/../lib/libpython{major}.{minor}.dylib",
        )
    )

    for detected_path, target in candidates:
        if detected_path.exists():
            print(f"[patch-wheel] detected python runtime: {detected_path}")
            return target

    # Last-resort fallback keeps previous behavior.
    return f"@executable_path/../lib/libpython{major}.{minor}.dylib"


def patch_binary(
    binary_path: Path,
    target_python_lib: str,
    *,
    rewrite_vtk_to_vtkmodules: bool,
) -> int:
    deps = read_macho_dependencies(binary_path)
    if not deps:
        return 0

    changes = 0
    for dep in deps:
        target = ""
        if should_rewrite_python_dependency(dep):
            target = target_python_lib
        elif rewrite_vtk_to_vtkmodules and should_rewire_to_vtkmodules(dep):
            target = f"@loader_path/.vtk/vtkmodules/.dylibs/{Path(dep).name}"
        else:
            continue

        if dep == target:
            continue
        run(
            [
                "install_name_tool",
                "-change",
                dep,
                target,
                str(binary_path),
            ]
        )
        changes += 1

    if changes:
        run(["codesign", "--force", "--sign", "-", str(binary_path)], check=False)
    return changes


def iter_macho_binaries(root: Path):
    for path in root.rglob("*"):
        if path.suffix not in {".so", ".dylib"} and path.name != "Python":
            continue
        if path.is_file():
            yield path


def vendor_vtk_python_payload(root: Path, *, expected_py: tuple[int, int]) -> tuple[Path, Path]:
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
    vtk_py_dest = bundle_dir / "vtk.py"
    vtkmodules_dest = bundle_dir / "vtkmodules"

    shutil.copy2(vtk_py_src, vtk_py_dest)
    if vtkmodules_dest.exists():
        shutil.rmtree(vtkmodules_dest)
    shutil.copytree(vtkmodules_src, vtkmodules_dest)
    return vtk_py_dest, vtkmodules_dest


def remove_vmtk_dylibs_tree(root: Path) -> int:
    dylibs_dir = root / "vmtk" / ".dylibs"
    if not dylibs_dir.exists():
        return 0
    files = sum(1 for p in dylibs_dir.rglob("*") if p.is_file())
    shutil.rmtree(dylibs_dir)
    return files


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


def validate_no_vmtk_vtk_dylib_refs(root: Path) -> None:
    vmtk_dir = root / "vmtk"
    if not vmtk_dir.exists():
        return

    bad_refs: list[tuple[str, str]] = []
    for binary in iter_macho_binaries(vmtk_dir):
        rel = binary.relative_to(root).as_posix()
        if rel.startswith("vmtk/.dylibs/"):
            continue
        if rel.startswith("vmtk/.vtk/vtkmodules/"):
            continue
        for dep in read_macho_dependencies(binary):
            libname = Path(dep).name
            if libname.startswith("libvtk") and not libname.startswith("libvtkvmtk"):
                if "/.vtk/vtkmodules/.dylibs/" not in dep:
                    bad_refs.append((rel, dep))
    if bad_refs:
        sample = "; ".join(f"{b} -> {d}" for b, d in bad_refs[:5])
        raise RuntimeError(f"Found unresolved VTK references outside vtkmodules: {sample}")


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


def patch_wheel(wheel_path: Path, *, vendor_vtk_python: bool) -> None:
    major, minor = parse_wheel_python_version(wheel_path)
    target_python_lib = infer_target_python_runtime((major, minor))
    print(f"[patch-wheel] target python runtime: {target_python_lib}")

    with tempfile.TemporaryDirectory() as td:
        unpack_dir = Path(td) / "wheel"
        with ZipFile(wheel_path) as zf:
            zf.extractall(unpack_dir)

        if vendor_vtk_python:
            vtk_py_dest, vtkmodules_dest = vendor_vtk_python_payload(
                unpack_dir, expected_py=(major, minor)
            )
            print(f"[patch-wheel] vendored: {vtk_py_dest.relative_to(unpack_dir)}")
            print(f"[patch-wheel] vendored: {vtkmodules_dest.relative_to(unpack_dir)}")

        patched_binaries = 0
        install_name_changes = 0
        for binary in iter_macho_binaries(unpack_dir):
            rel = binary.relative_to(unpack_dir).as_posix()
            rewrite_vtk = (
                rel.startswith("vmtk/")
                and not rel.startswith("vmtk/.dylibs/")
                and not rel.startswith("vmtk/.vtk/vtkmodules/")
            )
            changes = patch_binary(
                binary,
                target_python_lib,
                rewrite_vtk_to_vtkmodules=rewrite_vtk and vendor_vtk_python,
            )
            if changes:
                patched_binaries += 1
                install_name_changes += changes

        if vendor_vtk_python:
            validate_no_vmtk_vtk_dylib_refs(unpack_dir)
            removed_dylibs = remove_vmtk_dylibs_tree(unpack_dir)
            removed_requirements = strip_vtk_requirement(unpack_dir)
        else:
            removed_dylibs = 0
            removed_requirements = 0

        record_path = rewrite_record(unpack_dir)
        repack_wheel(unpack_dir, wheel_path)

    print(f"[patch-wheel] patched binaries: {patched_binaries}")
    print(f"[patch-wheel] install_name changes: {install_name_changes}")
    print(f"[patch-wheel] removed vmtk/.dylibs files: {removed_dylibs}")
    print(f"[patch-wheel] removed metadata vtk requirements: {removed_requirements}")
    print(f"[patch-wheel] updated RECORD: {record_path.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path, help="Path to repaired macOS wheel")
    parser.add_argument(
        "--no-vendor-vtk-python",
        action="store_true",
        help="Skip vendoring vtk.py and vtkmodules into the wheel",
    )
    args = parser.parse_args()

    wheel_path = args.wheel.resolve()
    if not wheel_path.exists():
        print(f"Wheel not found: {wheel_path}", file=sys.stderr)
        return 1
    patch_wheel(wheel_path, vendor_vtk_python=not args.no_vendor_vtk_python)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
