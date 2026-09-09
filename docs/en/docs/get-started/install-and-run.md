---
title: Install and run
description: Install PowerContext, choose a release and installation method, and manage a local Server.
---

# Install and run

For your first Agent connection, follow [Quick start](quickstart.md) through installation, model configuration, and verification. Use this guide to choose an installation method, version, platform, or optional database.

## Platforms and prerequisites

| Platform | Status | Installation entry point |
| --- | --- | --- |
| macOS, Linux | Supported | Bash installer, or uv on any platform |
| Windows | `experimental` | PowerShell installer, or uv on any platform |

The script needs Bash, curl or wget, and access to the installation and package download services. It reuses existing uv and Python 3.11+ installations. It installs uv only when missing and downloads Python 3.12 only when no compatible local interpreter is found.
You do not need Python installed beforehand or have to change system Python.

Agent integration setup also requires Git and the host's own prerequisites. The script does not install Agent applications. Without Git, use `--no-hosts` to install the Runtime first.
On Windows, individual hosts and databases have their own platform requirements. Embedded seekDB does not support Windows.

## Install the application

Choose the installer for your operating system, use an existing uv installation on any platform, or create a virtual environment from an existing Python installation. Each method installs the CLI, Server, and default SQLite backend.

```bash tab="Install script"
curl -fsSL https://powercontext.oceanbase.io/install.sh -o powercontext-install.sh
bash powercontext-install.sh --no-hosts
export PATH="$HOME/.local/bin:$PATH"
```

```console tab="Existing uv (all platforms)"
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
uv tool update-shell
```

```bash tab="pip + venv"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install "powercontext[cli,server]==0.2.0"
```

The pip method requires Python 3.11+ with venv support. uv obtains Python if it is missing.
Reopen the terminal after `uv tool update-shell`. For custom directories, use the `PATH` command printed by the Bash installer.

On Windows, use these commands. They reuse uv when it is already available:

```powershell
$env:Path = "$HOME\.local\bin;$env:Path"
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Invoke-WebRequest https://astral.sh/uv/install.ps1 -OutFile uv-install.ps1
    powershell -ExecutionPolicy Bypass -File .\uv-install.ps1
}
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
$env:Path = "$(uv tool dir --bin);$env:Path"
```

See the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) for other ways to obtain uv.
If uv, Python, or PyPI downloads fail, use [Configure package indexes](configure-package-index.md) to identify which service failed.

### Installer behavior

You can inspect the downloaded script or read its [source](https://github.com/oceanbase/powercontext/blob/master/website/public/install.sh).
The script checks `PATH` and `~/.local/bin` for uv, then uses uv to find a compatible local Python, including interpreters previously downloaded by uv. When one is found, the script selects it and disables further Python downloads. It does not upgrade existing uv.
It then installs PowerContext in its user tool environment, checks that the CLI starts, and prints the model configuration guide.
It preserves existing uv settings. It does not write global package index settings, model credentials, or a Server environment file, and does not register a personal service.

To install integrations at the same time, select hosts explicitly:

```bash
bash powercontext-install.sh --version 0.2.0 --host codex --host claude-code
```

Without host options, an interactive terminal opens `powercontext setup select`. Automation must pass `--host` or `--no-hosts`.
Downloading the file before running it preserves interactive input. If you pipe the script to Bash, pass those options explicitly.
Installation and verification use the existing `setup` commands. A failed host returns a nonzero status with results; the installed Runtime remains available.
After fixing host prerequisites, retry its `powercontext setup` command with the same release tag.

## Choose a version

Use a stable release for normal use. Keep the Runtime package and Agent integration on the same release.
These examples show both commands together for Codex, which must already be installed and configured before setup.

```bash tab="Stable release"
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
powercontext setup codex --ref powercontext-v0.2.0
```

```bash tab="Prerelease"
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==<version>"
powercontext setup codex --ref "powercontext-v<version>"
```

```bash tab="Development source"
POWERCONTEXT_REF="$(git ls-remote https://github.com/oceanbase/powercontext.git refs/heads/master | cut -f1)"
uv tool install --python ">=3.11,<4" --force "powercontext[cli,server] @ git+https://github.com/oceanbase/powercontext.git@${POWERCONTEXT_REF}"
powercontext setup codex --ref "$POWERCONTEXT_REF"
```

Replace both `<version>` placeholders with the same published prerelease. A version such as `0.3.0rc1` illustrates the format; it does not claim that release exists.
If no prerelease is available, use the stable release rather than falling back to `master`.
The source example uses Bash to resolve `master` to a single commit for both installations. Source capabilities may be unreleased; check the [capability matrix](../integrations/capabilities.md).

The script also accepts `--version` and uses the matching `powercontext-v<version>` integration tag. It supports releases using that naming convention from `0.1.0` onward.
An unavailable version fails instead of downgrading. See [Configure package indexes](configure-package-index.md) for mirror synchronization delays.

## Configure and start the Server

After [configuring models](configure-models.md), validate and start with the same environment file:

```bash
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

The Server listens on `127.0.0.1:8000`, serves MCP at `/mcp`, creates a default Scope, and stores SQLite data in the user data directory.
Press `Ctrl-C` to stop it. Restarting with the same data directory restores existing data.

If you only need explicit Memory writes and full-text search, `powercontext server run` works without models.
That mode does not enable model extraction or vector search. Automatic extraction needs a generation model and a schedule; vector search also needs embeddings.

Check the service from another terminal:

```bash
powercontext doctor
powercontext ready
powercontext capabilities
```

`doctor` checks packages, Server liveness, and readiness. Runtime or database failures return `not_ready`; a configured inference service failure returns `degraded`.
See [Troubleshoot](../operate/troubleshoot.md) for status details. For persistent services, Docker, authentication, or remote access, see [Deploy the Server](../operate/deploy-server.md).

### Enable the Dashboard

The Dashboard is an optional content viewer for personal use and demonstrations. It is disabled by default and needs
no separate frontend installation or model configuration. To enable it, put these settings in a protected environment
file and replace the token example with your own long random credential:

```dotenv
POWERCONTEXT_SERVER_DASHBOARD_ENABLED=true
POWERCONTEXT_SERVER_ACCESS_MODE=enforced
POWERCONTEXT_SERVER_AUTH_TOKEN=replace-with-your-random-token
```

```bash
chmod 600 /path/to/powercontext.env
powercontext config validate --env-file /path/to/powercontext.env
powercontext server run --env-file /path/to/powercontext.env
```

Open `http://127.0.0.1:8000/dashboard/home` and enter the same token. Use the actual port if you change it.
The token also protects the Server API and MCP, so connected Agents need it too. `server run` discovers `.env` in the
current directory; use `--env-file <path>` for another file or `--no-env-file` to disable file loading.

The first sign-in selects the Server default Scope. Pages are empty until content is saved. Save a Memory through an
Agent or public API, then refresh Memories in the same Scope. Experiences, skills, handoffs, and usage also come from
saved records. The Dashboard does not capture sessions, run generation, or approve candidates. The Dashboard and Agent
must use the same Server and Scope.

All token holders use one identity. Multi-user RBAC deployments should leave the Dashboard disabled and use the API,
MCP, or host integrations. See [Deploy the Server](../operate/deploy-server.md) for network and credential configuration.

## Use embedded seekDB

On Linux/macOS systems with a compatible `pylibseekdb` wheel, add the seekDB extra to the installation:

```bash
uv tool install --python ">=3.11,<4" "powercontext[cli,server,seekdb]==0.2.0"
```

Set `POWERCONTEXT_SERVER_DATABASE_KIND=seekdb` in `.env` and remove `POWERCONTEXT_SERVER_DATABASE_URL`.
seekDB does not accept an explicit SQLAlchemy database URL and uses its built-in `test` database.
Its default path is `seekdb` within the user data directory, or `$POWERCONTEXT_HOME/seekdb` when `POWERCONTEXT_HOME` is set.
Use `POWERCONTEXT_SERVER_DATABASE_PATH` for a custom path. Switching backends does not migrate existing SQLite data.

## Update an installation

Read the target release notes, then update the Runtime and the integrations you use to that exact release:

```bash
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==<version>"
powercontext setup codex --ref "powercontext-v<version>"
```

Replace both `<version>` placeholders before running the commands. Restart the Server, then start a new Agent session.
A pinned uv tool installation retains its version constraint; `uv tool upgrade powercontext` does not cross that constraint.
You can rerun the installer with a new `--version`; selected hosts must be updated together.
Package updates do not delete data, but database compatibility and migration requirements depend on the target release notes.

## Install a Python role

If your application imports the asynchronous Client SDK, add the dependency to that application's environment:

```bash
uv add "powercontext[client]==0.2.0"
```

Use `client` for the Python SDK, `builtin` for in-process composition, `server` for the service, and `cli` for commands.
Packages in a uv tool environment cannot be imported directly by another Python project. See [Interfaces](../develop/interfaces.md) for usage.
