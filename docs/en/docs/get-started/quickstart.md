---
title: Quick start
description: Install PowerContext, configure a generation model, connect Codex, and recover a saved decision in a new session.
---

# Quick start

Run a local PowerContext Server, configure automatic extraction, and verify memory across Codex sessions.
You need Codex, Git, and an API key for a generation model service. The PowerContext Server calls its own model; it does not automatically use Codex's model settings or login credentials.

## 1. Install PowerContext

If uv is already installed, use it directly on macOS, Linux, or Windows. Otherwise, use the installer for your operating system. Windows support is `experimental`.
The operating-system installers reuse compatible uv and Python 3.11+ installations and download only what is missing.

```console tab="uv" tab-group="install-method"
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
uv tool update-shell
```

```bash tab="install.sh (macOS / Linux)" tab-group="install-method"
curl -fsSL https://powercontext.oceanbase.io/install.sh -o powercontext-install.sh
bash powercontext-install.sh --no-hosts
export PATH="$HOME/.local/bin:$PATH"
```

```powershell tab="install.ps1 (Windows)" tab-group="install-method"
$env:Path = "$HOME\.local\bin;$env:Path"
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Invoke-WebRequest https://astral.sh/uv/install.ps1 -OutFile uv-install.ps1
    powershell -ExecutionPolicy Bypass -File .\uv-install.ps1
}
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
$env:Path = "$(uv tool dir --bin);$env:Path"
```

All three paths install release `0.2.0`. Reopen the terminal after `uv tool update-shell`; for the script paths, follow any `PATH` command printed by the installer.
For pip, other versions, or download failures, see [Install and run](install-and-run.md) and [Configure package indexes](configure-package-index.md).

## 2. Configure a generation model

Create a local environment file, accepting the default local settings:

```bash
powercontext config init --output .env
```

Edit `.env` and add the following settings, replacing the API key placeholder. This example uses OpenAI:

```dotenv
OPENAI_API_KEY=replace-with-your-api-key
POWERCONTEXT_SERVER_INFERENCE_GENERATION_MODEL=openai-chat:gpt-4.1-mini
POWERCONTEXT_SERVER_RUNTIME_SCHEDULE_SECONDS=60
```

The generation model extracts Memory from captured Sources; the scheduler checks pending Sources every 60 seconds. Model calls use your service quota.
For another service, follow [Configure models](configure-models.md) to set the model identifier, endpoint, and credentials first.
Keep `.env` local and out of Git. See [Configure the Server environment](configure-server-environment.md) for file loading and protection rules.

## 3. Start and check the Server

```bash
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

Keep this terminal open. The Server listens at `http://127.0.0.1:8000`, persists data in local SQLite, and serves MCP at `/mcp`.
The personal Dashboard is disabled by default; see [Install and run](install-and-run.md) to enable it. `server run` discovers `.env` in the current directory, while the explicit option above guarantees that it loads the file you just validated.

Open another terminal, ensure PowerContext is on `PATH`, and check:

```bash
powercontext doctor
powercontext ready
powercontext capabilities
```

Expect readiness `ready` and Memory extraction enabled. A `degraded` status means a configured inference service needs attention.
With generation alone, search supports `auto` and `fts`. For `vector` and `hybrid`, [configure embeddings](configure-models.md#enable-vector-search).
Configuration validation does not prove a real request will succeed. Follow [Verify a real extraction](configure-models.md#verify-a-real-extraction) to check that a Source produces Memory with source references.

## 4. Connect Codex

In another terminal, install the integration from the same release:

```bash
powercontext setup codex --source oceanbase/powercontext --ref powercontext-v0.2.0
powercontext doctor codex
```

Open a new Codex session in your project to load the plugin. See the [Codex guide](../integrations/codex.md) for connection and authentication settings.
For another host, use its [integration guide](../integrations/index.md), keeping the Runtime and integration on the same release.

Different projects do not automatically receive separate Scopes. Use [Scopes and access control](../workflows/scopes-and-access.md) when projects need isolated data.

## 5. Save and recover a decision

Ask Codex to save an explicit decision that contains no sensitive information:

```text
Remember this project decision in PowerContext: use uv for Python dependency management.
```

Ask it to search PowerContext for the decision, and check its content and Memory citation. Then open a new Codex session in the same project and ask:

```text
Search PowerContext: which tool does this project use for Python dependency management?
```

The result should include the same decision and its citation. This checks memory writes and reads across sessions; the model guide above checks automatic extraction.
Recovery depends on the same Server data and resolved Scope, not on keeping the original session open. Current project files and user instructions still take precedence over historical context.

## Continue with your work

- [Memory and context](../workflows/memory-and-context.md): revise or retire saved information and control recall.
- [Work continuity](../workflows/memory-and-handoff.md): transfer current work through Handoff.
- [Deploy the Server](../operate/deploy-server.md): run a persistent personal service.
- [Troubleshoot](../operate/troubleshoot.md): diagnose installation, Server, or recall problems.
