# Copyright (c) 2026 OceanBase.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Exercise the public installer with isolated command fixtures and no Python on PATH."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "website/public/install.sh"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None or sys.platform == "win32", reason="Bash installer targets Unix")


def write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(0o755)


@pytest.fixture
def installer_env(tmp_path: Path) -> dict[str, str]:
    command_dir = tmp_path / "commands"
    command_dir.mkdir()
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    for name in ("sh", "dirname", "uname", "mktemp", "rm", "grep", "mkdir", "cp"):
        executable = shutil.which(name)
        assert executable is not None
        (command_dir / name).symlink_to(executable)

    # Fixtures use the test interpreter by absolute path. The installer cannot find python, python3, or uv.
    uv_fixture = tmp_path / "uv-fixture"
    write_executable(
        uv_fixture,
        f"#!{sys.executable}\n"
        + """import json
import os
import sys
from pathlib import Path

root = Path(os.environ["HOME"])
args = sys.argv[1:]
if args[:2] == ["tool", "dir"]:
    print(root / ".local/bin")
elif args[:2] == ["python", "find"]:
    if not os.environ.get("LOCAL_PYTHON"):
        raise SystemExit(1)
    print(os.environ["LOCAL_PYTHON"])
elif args[:2] == ["tool", "install"]:
    requirement = next(arg for arg in args if arg.startswith("powercontext["))
    (root / "installed.json").write_text(json.dumps({
        "requirement": requirement,
        "index": os.environ.get("UV_DEFAULT_INDEX"),
        "python": args[args.index("--python") + 1],
        "python_downloads_disabled": "--no-python-downloads" in args,
    }))
    target = root / ".local/bin/powercontext"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("#!/bin/sh\\n" +
        'if [ "$1" = "setup" ]; then\\n' +
        '  printf "%s\\\\n" "$@" > "$HOME/setup-args"\\n' +
        '  exit "${SETUP_STATUS:-0}"\\nfi\\n')
    target.chmod(0o755)
else:
    raise SystemExit(f"Unexpected uv command: {args}")
""",
    )
    write_executable(
        command_dir / "curl",
        f"#!{sys.executable}\n"
        + """import os
import sys
from pathlib import Path

args = sys.argv[1:]
url = next(arg for arg in args if arg.startswith("https://"))
target = Path(args[args.index("-o") + 1])
with (Path(os.environ["HOME"]) / "downloads").open("a") as stream:
    stream.write(url + "\\n")
if url == "https://astral.sh/uv/install.sh":
    target.write_text('#!/bin/sh\\nmkdir -p "$UV_INSTALL_DIR"\\ncp "$UV_FIXTURE" "$UV_INSTALL_DIR/uv"\\n')
elif os.environ.get("INDEX_UNREACHABLE"):
    raise SystemExit(28)
else:
    version = os.environ.get("AVAILABLE_VERSION", "0.2.0")
    target.write_text(f'<a href="powercontext-{version}-py3-none-any.whl">wheel</a>')
""",
    )
    return {
        "HOME": str(home_dir),
        "PATH": str(command_dir),
        "XDG_CONFIG_HOME": str(home_dir / ".config"),
        "XDG_CONFIG_DIRS": str(home_dir / "system-config"),
        "TMPDIR": str(tmp_path),
        "UV_FIXTURE": str(uv_fixture),
    }


def run_installer(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    assert BASH is not None
    return subprocess.run(
        [BASH, str(SCRIPT), *args],
        env=env,
        cwd=env["HOME"],
        input="",
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )


def test_installs_without_python_or_uv_and_preserves_user_files(installer_env: dict[str, str]) -> None:
    home_dir = Path(installer_env["HOME"])
    for name in (".env", ".bashrc"):
        (home_dir / name).write_text("existing user configuration\n")
    for _ in range(2):
        result = run_installer(installer_env, "--no-hosts")
        assert result.returncode == 0, result.stderr
        assert "Configure a generation model" in result.stdout
    installed = json.loads((home_dir / "installed.json").read_text())
    assert installed["requirement"] == "powercontext[cli,server]==0.2.0"
    assert installed["python"] == "3.12"
    assert (home_dir / ".local/bin/uv").is_file()
    assert (home_dir / ".local/bin/powercontext").is_file()
    assert (home_dir / "downloads").read_text().count("https://astral.sh/uv/install.sh") == 1
    assert not (home_dir / "setup-args").exists()
    for name in (".env", ".bashrc"):
        assert (home_dir / name).read_text() == "existing user configuration\n"


@pytest.mark.parametrize("existing_uv", [False, True])
def test_reuses_local_python_without_downloading_an_interpreter(
    installer_env: dict[str, str], existing_uv: bool
) -> None:
    home_dir = Path(installer_env["HOME"])
    installer_env["LOCAL_PYTHON"] = "/opt/local python/bin/python3.13"
    if existing_uv:
        (Path(installer_env["PATH"]) / "uv").symlink_to(installer_env["UV_FIXTURE"])
    result = run_installer(installer_env, "--no-hosts")
    assert result.returncode == 0, result.stderr
    installed = json.loads((home_dir / "installed.json").read_text())
    assert installed["python"] == installer_env["LOCAL_PYTHON"]
    assert installed["python_downloads_disabled"]
    downloads = (home_dir / "downloads").read_text()
    assert ("https://astral.sh/uv/install.sh" in downloads) is not existing_uv


@pytest.mark.parametrize("version", ["0.2.0", "0.3.0rc1"])
def test_runtime_and_selected_hosts_use_the_same_release(installer_env: dict[str, str], version: str) -> None:
    home_dir = Path(installer_env["HOME"])
    write_executable(Path(installer_env["PATH"]) / "git", "#!/bin/sh\nexit 0\n")
    installer_env["AVAILABLE_VERSION"] = version
    result = run_installer(installer_env, "--version", version, "--host", "codex", "--host", "claude-code")
    assert result.returncode == 0, result.stderr
    installed = json.loads((home_dir / "installed.json").read_text())
    assert installed["requirement"] == f"powercontext[cli,server]=={version}"
    setup = (home_dir / "setup-args").read_text().splitlines()
    assert setup[setup.index("--ref") + 1] == f"powercontext-v{version}"
    assert "codex" in setup and "claude-code" in setup


def test_preserves_existing_index_and_does_not_probe_public_pypi(installer_env: dict[str, str]) -> None:
    home_dir = Path(installer_env["HOME"])
    installer_env["UV_DEFAULT_INDEX"] = "https://user:private-token@packages.example/simple"
    result = run_installer(installer_env, "--no-hosts")
    assert result.returncode == 0, result.stderr
    installed = json.loads((home_dir / "installed.json").read_text())
    assert installed["index"] == installer_env["UV_DEFAULT_INDEX"]
    assert "pypi.org" not in (home_dir / "downloads").read_text()
    assert "private-token" not in result.stdout + result.stderr


def test_preserves_user_uv_configuration(installer_env: dict[str, str]) -> None:
    config = Path(installer_env["XDG_CONFIG_HOME"]) / "uv/uv.toml"
    config.parent.mkdir(parents=True)
    content = '[[index]]\nurl = "https://packages.example/simple"\ndefault = true\n'
    config.write_text(content)
    result = run_installer(installer_env, "--no-hosts")
    assert result.returncode == 0, result.stderr
    assert config.read_text() == content
    assert "pypi.org" not in (Path(installer_env["HOME"]) / "downloads").read_text()


def test_explicit_mirror_applies_without_changing_global_configuration(installer_env: dict[str, str]) -> None:
    home_dir = Path(installer_env["HOME"])
    mirror = "https://mirror.example/simple"
    result = run_installer(installer_env, "--no-hosts", "--index-url", mirror)
    assert result.returncode == 0, result.stderr
    assert json.loads((home_dir / "installed.json").read_text())["index"] == mirror
    assert f"{mirror}/powercontext/" in (home_dir / "downloads").read_text()
    assert not (home_dir / ".config/uv/uv.toml").exists()


@pytest.mark.parametrize("failure", ["missing-version", "unreachable"])
def test_index_failure_stops_without_installing_another_version(installer_env: dict[str, str], failure: str) -> None:
    installer_env["AVAILABLE_VERSION"] = "0.1.0"
    if failure == "unreachable":
        installer_env["INDEX_UNREACHABLE"] = "1"
    result = run_installer(installer_env, "--no-hosts")
    assert result.returncode != 0
    assert not (Path(installer_env["HOME"]) / "installed.json").exists()
    assert "index" in result.stderr.lower()


def test_partial_setup_failure_retains_runtime(installer_env: dict[str, str]) -> None:
    home_dir = Path(installer_env["HOME"])
    write_executable(Path(installer_env["PATH"]) / "git", "#!/bin/sh\nexit 0\n")
    installer_env["SETUP_STATUS"] = "1"
    result = run_installer(installer_env, "--host", "codex")
    assert result.returncode != 0
    assert (home_dir / ".local/bin/powercontext").is_file()
    assert "Runtime installed, but integration setup did not complete" in result.stderr


@pytest.mark.parametrize(
    "args",
    [(), ("--host", "codex", "--no-hosts"), ("--version",), ("--no-hosts", "--version", "master")],
)
def test_invalid_or_missing_selection_does_not_mutate_installation(
    installer_env: dict[str, str], args: tuple[str, ...]
) -> None:
    result = run_installer(installer_env, *args)
    assert result.returncode != 0
    assert not (Path(installer_env["HOME"]) / "downloads").exists()


def test_index_argument_does_not_echo_credentials(installer_env: dict[str, str]) -> None:
    result = run_installer(installer_env, "--no-hosts", "--index-url", "https://user:private-token@host/simple")
    assert result.returncode != 0
    assert "private-token" not in result.stdout + result.stderr
