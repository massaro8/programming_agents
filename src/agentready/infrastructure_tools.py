"""Opt-in project-local CloudFormation tools; ordinary checks never download."""

from __future__ import annotations

import hashlib
import io
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

from agentready.local_paths import local_path

GUARD_VERSION = "3.2.1"
ASSETS = {
    ("Windows", "x86_64"): (
        "x86_64-windows-latest",
        "52af28c02081f1067c6710c08619d359899734ec59d51f17f68e1b4b396a1203",
    ),
    ("Windows", "aarch64"): (
        "aarch64-windows-latest",
        "faa9a14382314cd2c3ce6adc21388e0422280ab33ded3c8b1321877efd761300",
    ),
    ("Linux", "x86_64"): (
        "x86_64-linux-latest",
        "8c66efb19c63e6c2bf26b9a41bbcf2f85baa8a937b01d350940194faaf64cf1d",
    ),
    ("Linux", "aarch64"): (
        "aarch64-linux-latest",
        "cd378026dad0f865926ab1d1c082e2faf825f7fd888a9fe6b5c142cdf175c129",
    ),
    ("Darwin", "x86_64"): (
        "x86_64-macos-latest",
        "5089dfaa05a766cf118a020518e62f77eddbd43acf3a0b69d36b23175c6c6fda",
    ),
    ("Darwin", "aarch64"): (
        "aarch64-macos-latest",
        "4c1eb10c061731159eaaf0e7dbd465db9fa4b767b82186a4ab489671cc00b7d0",
    ),
}
MAX_DOWNLOAD = 64 * 1024 * 1024


def tool_search_path(root: Path) -> str:
    """Discover local tools without modifying the user's shell or global PATH."""
    scripts = "Scripts" if os.name == "nt" else "bin"
    paths = [
        local_path(root, f".tools/.venv/{scripts}"),
        local_path(root, ".tools/bin"),
        local_path(root, f".venv/{scripts}"),
    ]
    return os.pathsep.join([*(str(path) for path in paths), os.environ.get("PATH", "")])


def find_tool(root: Path, name: str) -> str | None:
    return shutil.which(name, path=tool_search_path(root))


def _install_guard(root: Path) -> None:
    machine = platform.machine().lower()
    machine = {"amd64": "x86_64", "arm64": "aarch64"}.get(machine, machine)
    asset = ASSETS.get((platform.system(), machine))
    if asset is None:
        raise ValueError("Guard bootstrap unsupported on this platform; install Guard on PATH")
    suffix, digest = asset
    url = (
        "https://github.com/aws-cloudformation/cloudformation-guard/releases/download/"
        f"{GUARD_VERSION}/cfn-guard-v3-{suffix}.tar.gz"
    )
    print(f"Installing Guard {GUARD_VERSION} in .tools/bin", flush=True)
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("Guard archive size or SHA-256 mismatch; nothing installed")
    binary = "cfn-guard.exe" if os.name == "nt" else "cfn-guard"
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = [member for member in archive.getmembers() if Path(member.name).name == binary]
        if len(members) != 1 or not members[0].isfile() or members[0].size > MAX_DOWNLOAD:
            raise ValueError("Guard archive does not contain one safe executable")
        stream = archive.extractfile(members[0])
        if stream is None:
            raise ValueError("Guard executable could not be read")
        with stream:
            executable = stream.read(MAX_DOWNLOAD + 1)
    destination = local_path(root, f".tools/bin/{binary}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with destination.open("xb") as output:
            created = True
            output.write(executable)
        destination.chmod(0o755)
    except OSError:
        if created:
            destination.unlink()
        raise


def prepare_tools(root: Path) -> None:
    """Install missing pinned tools only on an explicitly requested bootstrap."""
    # Validate local destinations before performing any installation.
    tool_search_path(root)
    if find_tool(root, "cfn-lint") is None:
        uv = shutil.which("uv")
        if uv is None:
            raise ValueError("uv is required to install local cfn-lint; install uv and retry")
        environment = local_path(root, ".tools/.venv")
        scripts = "Scripts/python.exe" if os.name == "nt" else "bin/python"
        # POSIX virtual environments normally link their interpreter to host Python.
        python = (
            local_path(root, f".tools/.venv/{Path(scripts).parent.as_posix()}") / Path(scripts).name
        )
        commands = []
        if not python.is_file():
            commands.append([uv, "venv", str(environment)])
        commands.append([uv, "pip", "install", "--python", str(python), "cfn-lint==1.57.2"])
        for command in commands:
            result = subprocess.run(command, cwd=root, check=False)
            if result.returncode:
                raise ValueError("local cfn-lint installation failed; retry bootstrap")
    if find_tool(root, "cfn-guard") is None:
        _install_guard(root)
