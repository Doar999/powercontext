---
title: Configure a Server environment
description: Generate, inspect, validate, and run PowerContext from an explicit environment file.
---

# Configure a Server environment

Use this guide to generate, protect, and load an environment file. For your first generation or embedding service, start with [Configure models](configure-models.md).

## 1. Generate the file

```bash
powercontext config init --output .env
```

The command generates basic settings that can start a local Server without asking for models or provider credentials.
For automatic extraction, add a generation model, credentials, and a schedule interval. Vector search also needs an embedding model, profile ID, and dimension.
If `.env` already exists, edit the required entries rather than initializing it again.

When `--force` would remove existing model, embedding, inference schedule, or provider credential settings, the
command identifies that impact and requires an explicit confirmation that defaults to no. After confirmation, it
creates a mode-`0600` backup before replacing the file.

On macOS and Linux, the command writes a private file with mode `0600`. Provide credentials through a private environment file or secret manager. Keep them out of command-line arguments and Git.

Windows support is `experimental`. Before using the file for a personal service, restrict its ACL as described in
[Deploy the Server](../operate/deploy-server.md).

## 2. Inspect and validate it

```bash
powercontext config show --env-file .env
powercontext config validate --env-file .env
```

`config show` redacts recognized credentials. Validation accepts minimal Server-only files; when inference models or
inference-dependent runtime features are configured, it also checks the Runtime composition without printing secrets.

## 3. Run the same configuration

```bash
powercontext server run
```

`server run` discovers `.env` in the current directory. Use `--env-file <path>` to select a different file or
`--no-env-file` to disable file loading. CLI options take precedence, followed by process environment variables, the
selected file, and defaults. The command prints the resolved file path without printing credentials.

The Server starts with the configured capabilities. Use `powercontext ready` and `powercontext capabilities` to check
its readiness and enabled features.

For every variable, default, and precedence rule, see [Configuration](../operate/configuration.md).
