#!/usr/bin/env python3
"""Smoke-test a pip-installed VMTK package."""

from __future__ import annotations

import argparse
import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


CORE_WRAPPER_ATTRIBUTES = [
    "vtkvmtkMath",
    "vtkvmtkPolyDataCenterlines",
    "vtkvmtkCenterlineAttributesFilter",
    "vtkvmtkCenterlineGeometry",
    "vtkvmtkVoronoiDiagram3D",
    "vtkvmtkPolyDataNetworkExtraction",
    "vtkvmtkPolyDataBoundaryExtractor",
]


def assert_installed_location(module_file: str) -> None:
    normalized = module_file.replace("\\", "/")
    if "/site-packages/" not in normalized:
        raise RuntimeError(
            "vmtk was not imported from site-packages: "
            f"{module_file}"
        )


def run_help_command(command: str) -> None:
    executable = shutil.which(command)
    if not executable:
        raise RuntimeError(f"Command not found on PATH: {command}")

    proc = subprocess.run(
        [executable, "--help"],
        check=True,
        text=True,
        capture_output=True,
    )
    first_line = next(
        (line.strip() for line in proc.stdout.splitlines() if line.strip()),
        "",
    )
    print(f"[smoke] command={command} path={executable}")
    if first_line:
        print(f"[smoke] {command} --help: {first_line}")


def require_command(command: str) -> str:
    executable = shutil.which(command)
    if not executable:
        raise RuntimeError(f"Command not found on PATH: {command}")
    print(f"[smoke] command={command} path={executable}")
    return executable


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-cli",
        action="store_true",
        help="Skip testing `vmtk --help` and `vmtkimagereader --help`.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    script_dir = Path(__file__).resolve().parent

    # Ensure we import the installed package, not this checkout.
    filtered_path: list[str] = []
    for entry in sys.path:
        probe = Path(entry if entry else os.getcwd()).resolve()
        if probe in {repo_root, script_dir}:
            continue
        filtered_path.append(entry)
    sys.path[:] = filtered_path

    os.chdir(tempfile.gettempdir())
    if "" not in sys.path:
        sys.path.insert(0, "")

    print(f"[smoke] cwd={Path.cwd()}")
    print(f"[smoke] python={sys.executable}")

    python_bin_dir = str(Path(sys.executable).parent)
    os.environ["PATH"] = python_bin_dir + os.pathsep + os.environ.get("PATH", "")

    import vmtk  # type: ignore

    assert_installed_location(vmtk.__file__)
    print(f"[smoke] vmtk={vmtk.__file__}")

    from vmtk import vtkvmtk  # type: ignore

    missing = [name for name in CORE_WRAPPER_ATTRIBUTES if not hasattr(vtkvmtk, name)]
    if missing:
        raise RuntimeError(f"Missing core vtkvmtk symbols: {missing}")
    print(f"[smoke] vtkvmtk={vtkvmtk.__file__}")

    scripts_registry = importlib.import_module("vmtk.vmtkscripts")
    if "vmtk.vmtkcenterlines" not in getattr(scripts_registry, "__all__", []):
        raise RuntimeError("vmtk.vmtkscripts registry is missing vmtkcenterlines")
    print(f"[smoke] vmtkscripts_count={len(scripts_registry.__all__)}")

    if not args.skip_cli:
        require_command("vmtkimagereader")
        run_help_command("vmtk")

    print("[smoke] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
