#!/usr/bin/env python3
"""Download and stage the Linux VTK SDK for wheel builds.

The PyPI ``vtk`` runtime wheel does not ship ``vtk-config.cmake``, but VMTK's
native build uses ``find_package(VTK)``. This helper fetches the official VTK
SDK tarball used for wheel builds and places it in a deterministic location so
CI can set ``VTK_DIR`` and ``CMAKE_PREFIX_PATH``.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import tarfile
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
import sys


SDK_VERSION = "9.5.0"
SDK_BASE_URL = "https://vtk.org/files/wheel-sdks"
VTK_CONFIG_REL = Path(f"vtk-{SDK_VERSION}.data/headers/cmake/vtk-config.cmake")

ARCHIVE_TAGS_BY_MACHINE = {
    "x86_64": "manylinux2014_x86_64.manylinux_2_17_x86_64",
    "amd64": "manylinux2014_x86_64.manylinux_2_17_x86_64",
    "aarch64": "manylinux_2_28_aarch64",
    "arm64": "manylinux_2_28_aarch64",
}


@dataclass(frozen=True)
class SdkSpec:
    sdk_url: str
    archive_root: str
    python_tag: str
    machine: str


def normalize_machine(machine: str) -> str:
    machine = machine.strip().lower()
    if machine == "amd64":
        return "x86_64"
    if machine == "arm64":
        return "aarch64"
    return machine


def default_python_tag() -> str:
    return f"cp{sys.version_info.major}{sys.version_info.minor}"


def default_target_root(python_tag: str, machine: str) -> Path:
    return Path(f"/tmp/vmtk-vtk-sdk/linux-{python_tag}-{machine}")


def build_sdk_spec(*, sdk_version: str, python_tag: str, machine: str) -> SdkSpec:
    machine = normalize_machine(machine)
    archive_tag = ARCHIVE_TAGS_BY_MACHINE.get(machine)
    if archive_tag is None:
        known = ", ".join(sorted(set(normalize_machine(k) for k in ARCHIVE_TAGS_BY_MACHINE)))
        raise RuntimeError(
            f"Unsupported machine architecture '{machine}'. "
            f"Supported values: {known}."
        )

    if not python_tag.startswith("cp") or not python_tag[2:].isdigit():
        raise RuntimeError(
            f"Unsupported python tag '{python_tag}'. Expected format like cp310/cp311."
        )

    archive_root = f"vtk-wheel-sdk-{sdk_version}-{python_tag}-{python_tag}-{archive_tag}"
    sdk_url = f"{SDK_BASE_URL}/{archive_root}.tar.xz"
    return SdkSpec(
        sdk_url=sdk_url,
        archive_root=archive_root,
        python_tag=python_tag,
        machine=machine,
    )


def ensure_sdk(target_root: Path, *, spec: SdkSpec) -> None:
    vtk_config = target_root / VTK_CONFIG_REL
    if vtk_config.exists():
        print(f"[linux-vtk-sdk] reuse: {target_root}")
        print(f"[linux-vtk-sdk] vtk-config: {vtk_config}")
        return

    target_root.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="vmtk-vtk-sdk-") as td:
        temp_dir = Path(td)
        archive_path = temp_dir / "vtk-sdk.tar.xz"
        print(f"[linux-vtk-sdk] python-tag: {spec.python_tag}")
        print(f"[linux-vtk-sdk] machine: {spec.machine}")
        print(f"[linux-vtk-sdk] download: {spec.sdk_url}")
        urllib.request.urlretrieve(spec.sdk_url, archive_path)

        with tarfile.open(archive_path, "r:xz") as tar:
            tar.extractall(temp_dir)

        extracted_root = temp_dir / spec.archive_root
        if not extracted_root.exists():
            raise RuntimeError(f"Extracted SDK root not found: {extracted_root}")

        if target_root.exists():
            shutil.rmtree(target_root)
        shutil.move(str(extracted_root), str(target_root))

    vtk_config = target_root / VTK_CONFIG_REL
    if not vtk_config.exists():
        raise RuntimeError(f"VTK config missing after extraction: {vtk_config}")

    print(f"[linux-vtk-sdk] ready: {target_root}")
    print(f"[linux-vtk-sdk] vtk-config: {vtk_config}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sdk-version",
        default=SDK_VERSION,
        help=f"VTK SDK version (default: {SDK_VERSION}).",
    )
    parser.add_argument(
        "--python-tag",
        default=default_python_tag(),
        help="Python compatibility tag, e.g. cp310/cp311 (default: current interpreter).",
    )
    parser.add_argument(
        "--machine",
        default=normalize_machine(platform.machine()),
        help="CPU architecture tag, e.g. x86_64/aarch64 (default: current machine).",
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        default=None,
        help="Extraction target directory for the VTK SDK payload.",
    )
    args = parser.parse_args()

    spec = build_sdk_spec(
        sdk_version=args.sdk_version,
        python_tag=args.python_tag,
        machine=args.machine,
    )
    target_root = args.target_root or default_target_root(spec.python_tag, spec.machine)
    ensure_sdk(target_root.resolve(), spec=spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
