---
title: Configure package indexes
description: Diagnose download failures, select a PyPI mirror, and configure persistent uv or pip indexes.
---

# Configure package indexes

When installation times out or a version cannot be found, identify the failing download service first.
A PyPI mirror only affects Python packages. It does not change the download locations for uv, Python interpreters, GitHub, or Agent plugins.

| Failure | What to check |
| --- | --- |
| Downloading `install.sh` | Connectivity, proxies, and TLS certificates for `powercontext.oceanbase.io` |
| Downloading uv | Access to `astral.sh` and its GitHub release downloads |
| Downloading Python | The download URL in uv's error; alternatively, install Python 3.11+ before retrying |
| Resolving packages or downloading wheels | Effective indexes, package download URLs, target version, and platform compatibility |
| Installing an Agent integration | GitHub, the host marketplace, and the host package manager's registry |

## Select an index for one installation

Prefer your existing uv configuration. To select a public mirror, for example Tsinghua:

```bash tab="Install script"
bash powercontext-install.sh --no-hosts --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

```bash tab="uv"
uv tool install --python ">=3.11,<4" --default-index https://pypi.tuna.tsinghua.edu.cn/simple "powercontext[cli,server]==0.2.0"
```

```bash tab="pip"
python -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple "powercontext[cli,server]==0.2.0"
```

Download the script as described in [Install and run](install-and-run.md). Run pip in an activated Python 3.11+ virtual environment.
These options do not rewrite global configuration. uv records installation settings for the tool, so later upgrades may retain this index.

`--default-index` changes uv's default index. Existing additional indexes still take precedence; this option does not clear enterprise index configuration.
Review existing uv settings before changing the index strategy. Configure private index credentials using [uv authentication](https://docs.astral.sh/uv/concepts/indexes/#authentication); keep credentials out of public command examples.

## How the script checks indexes

When the script finds uv index environment variables or user/system configuration files, it preserves them and lets uv resolve and verify the configuration.
It does not parse TOML in shell or silently replace a private index with a public one.

Without custom configuration, the script requests the `powercontext` package index from PyPI and checks that the target version is listed.
Requests have time limits. If PyPI is unreachable, an interactive terminal offers the Tsinghua mirror. Noninteractive execution fails with instructions to retry using `--index-url`.
An explicitly selected index also fails directly if unreachable. This check covers the index response and version entry; uv still verifies dependency resolution and package downloads.

If a mirror lacks the target version, first confirm the release exists. Wait for synchronization or explicitly select PyPI:

```bash
bash powercontext-install.sh --no-hosts --version 0.2.0 --index-url https://pypi.org/simple
```

The script does not downgrade or switch to `master` to finish an installation. If PyPI is reachable but slow, select a mirror explicitly.
The script does not choose an index based on IP location or a single latency measurement.

## Set the uv default index for a terminal

Use an environment variable when running several installation commands in one terminal:

```bash tab="macOS / Linux" tab-group="install-platform"
export UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
```

```powershell tab="Windows" tab-group="install-platform"
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

uv does not read `pip.conf` or `PIP_INDEX_URL`. Configuring pip alone does not configure uv.
`uv tool` reads user and system configuration, ignoring the current project's `pyproject.toml` and `uv.toml`.

## Persist settings for uv or pip

Change persistent configuration only when future commands should keep using the same mirror. Inspect existing indexes first and preserve unrelated settings.

uv's user configuration is `$XDG_CONFIG_HOME/uv/uv.toml` on macOS/Linux, defaulting to `~/.config/uv/uv.toml`, or `%APPDATA%\uv\uv.toml` on Windows.
Add the following to `uv.toml`. If a default index already exists, edit that entry instead of defining it twice:

```toml
[[index]]
name = "mirror"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

pip uses separate configuration. To configure pip installation commands for the current user:

```bash
python -m pip config --user set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

Do not add a mirror with `--extra-index-url` to hide synchronization problems. uv checks indexes in order and does not merge versions across indexes after finding a package; pip's strategy differs.
See [uv indexes](https://docs.astral.sh/uv/concepts/indexes/), [uv configuration](https://docs.astral.sh/uv/concepts/configuration-files/), and [pip configuration](https://pip.pypa.io/en/stable/topics/configuration/) for the full rules.

## Restore previous settings

Remove the terminal variable set above:

```bash tab="macOS / Linux" tab-group="install-platform"
unset UV_DEFAULT_INDEX
```

```powershell tab="Windows" tab-group="install-platform"
Remove-Item Env:UV_DEFAULT_INDEX -ErrorAction SilentlyContinue
```

Restore previous entries in persistent configuration. If you had no custom index, remove the uv `[[index]]` block you added, or remove the pip setting:

```bash
python -m pip config --user unset global.index-url
```

Also remove any corresponding assignment from your shell startup files. If a tool retained the mirror in its installation settings, reinstall the target version with an explicit `--default-index https://pypi.org/simple`.
