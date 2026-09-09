---
title: Configure models
description: Configure generation and embedding services, enable automatic extraction, and verify Memory and vector search.
---

# Configure models

The PowerContext Server uses a generation model to process Sources and an embedding model to build and query a vector index.
These settings are independent of the Agent host's model and login credentials. [Install PowerContext](install-and-run.md), then choose your service configuration.

| Configuration | Available behavior |
| --- | --- |
| No models | Explicit Memory writes, full-text search, Dashboard, and MCP |
| Generation model and schedule interval | Automatic Memory extraction from Sources |
| Embedding model, profile ID, and dimension | Vector and hybrid search |

## Configure generation

If you do not have an environment file, create one:

```bash
powercontext config init --output .env
```

`config init` generates basic local Server settings without asking for a model or API key. Add the selected service's settings to `.env`, or edit existing entries.
The model names below are examples; your account must have access to the model you choose.

```dotenv tab="OpenAI"
OPENAI_API_KEY=replace-with-your-api-key
POWERCONTEXT_SERVER_INFERENCE_GENERATION_MODEL=openai-chat:gpt-4.1-mini
POWERCONTEXT_SERVER_RUNTIME_SCHEDULE_SECONDS=60
```

```dotenv tab="OpenAI-compatible"
OPENAI_API_KEY=replace-with-your-api-key
POWERCONTEXT_SERVER_INFERENCE_GENERATION_MODEL=openai-chat:replace-with-your-model
POWERCONTEXT_SERVER_INFERENCE_GENERATION_BASE_URL=https://your-provider.example/v1
POWERCONTEXT_SERVER_RUNTIME_SCHEDULE_SECONDS=60
```

```dotenv tab="Anthropic"
ANTHROPIC_API_KEY=replace-with-your-api-key
POWERCONTEXT_SERVER_INFERENCE_GENERATION_MODEL=anthropic:claude-sonnet-4-5
POWERCONTEXT_SERVER_RUNTIME_SCHEDULE_SECONDS=60
```

A compatible service must implement the chosen adapter's API and support the structured outputs PowerContext uses. A matching URL shape alone does not establish compatibility.
Override `POWERCONTEXT_SERVER_INFERENCE_GENERATION_BASE_URL` when needed. Do not reuse a generation endpoint as an embedding endpoint unless that service supports both.
For a local service that ignores authentication, use a non-secret placeholder accepted by that provider.

The scheduler checks pending Sources every 60 seconds. With a generation model but no interval, use an explicit flush to process Sources.
Model calls use your service quota. Keep credentials in the environment file or your deployment's secret manager, not in the repository, Memory, or shared logs.

## Enable vector search

Add embedding settings alongside your generation configuration. This example uses OpenAI and reuses `OPENAI_API_KEY`:

```dotenv
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_MODEL=openai:text-embedding-3-small
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_PROFILE_ID=openai-text-embedding-3-small-1536-unit-v1
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_DIMENSION=1536
```

Set the model, profile ID, and dimension together. The profile ID identifies the model, dimension, and normalization combination; normalization defaults to `unit`.
For another model, use its actual output dimension and a corresponding profile ID. Before changing the model or dimension for existing vectors, read the [vector search guide](../workflows/configure-vector-search.md).

Generation and embeddings can use different endpoints. For a compatible embedding service, use an `openai:model-name` identifier and a separate endpoint:

```dotenv
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_MODEL=openai:replace-with-your-embedding-model
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_BASE_URL=https://your-embedding-provider.example/v1
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_PROFILE_ID=your-provider-your-model-1536-unit-v1
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_DIMENSION=1536
```

The `1536` above is also an example to verify against the chosen model. Two OpenAI-compatible services can share `OPENAI_API_KEY` if they accept the same key.
If they use different keys, set a separate embedding Authorization header in the private environment file:

```dotenv
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_HEADERS={"Authorization":"Bearer replace-with-your-embedding-api-key"}
```

This field contains literal header values; it does not expand `${VARIABLE}`. An Anthropic generation configuration does not provide embeddings, so configure a separate embedding service.

## Validate and start

```bash
powercontext config show --env-file .env
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

`config show` redacts recognized credentials. `config validate` checks configuration and Runtime assembly; it does not replace a real model call.
The CLI does not search for `.env` automatically. Pass the same file to validation and startup. See [Configure the Server environment](configure-server-environment.md) for loading precedence.

In another terminal, run:

```bash
powercontext doctor
powercontext ready
powercontext capabilities
```

Expect readiness `ready` and Memory extraction enabled. When embeddings are configured, search modes should also include `vector` and `hybrid`.
These commands connect to `http://127.0.0.1:8000` by default. For another address or authentication, configure the Client as described in the [configuration reference](../operate/configuration.md).

## Verify a real extraction

These commands use a local Server without authentication, write one test Source, and inspect its extraction result. Keep the Server running.
The commands use Bash; on Windows, use Git Bash. JSON parsing runs Python through uv, so it does not require a system `python` command.

```bash
SCOPE_ID="$(curl -fsS http://127.0.0.1:8000/v1/scopes/default \
  | uv run --no-project --python ">=3.11,<4" python -c 'import json, sys; print(json.load(sys.stdin)["scope_id"])')"
SOURCE_ID="model-check-$(date +%s)-$$"
curl -fsS -X POST http://127.0.0.1:8000/v1/sources/content \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\",\"source_id\":\"${SOURCE_ID}\",\"content\":\"Project decision: use uv for Python dependency management. Preserve this decision for future maintainers.\"}"
```

Keep the response's `position`. Flush the same Scope explicitly without waiting for the scheduler:

```bash
curl -fsS -X POST http://127.0.0.1:8000/v1/memory/flush \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\"}"
curl -fsS -X POST http://127.0.0.1:8000/v1/memory/entries/list \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\"}"
```

The flush response's `current_cursor` should be at least the capture `position`. If the scheduler already processed the Source, `status: "idle"` is valid.
Find an entry with the matching content and the captured Source in `source_refs`, and record its `citation.entry_id`.
If the cursor advances but no matching entry appears, inspect model usage and logs. Cursor progress alone does not prove successful model extraction.

## Verify vector search

If embeddings are configured, query the same Scope:

```bash
curl -fsS -X POST http://127.0.0.1:8000/v1/memory/search \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\",\"query\":\"Python dependency management\",\"mode\":\"vector\",\"limit\":50}"
powercontext stats --scope-id "$SCOPE_ID"
```

Expect `mode: "vector"`, the entry recorded above, and `vector` in its `matched_by` list. Use `stats` to inspect model usage.
Without embeddings, skip this step and continue using full-text search.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Readiness is `degraded` | Check model identifiers, keys, endpoints, and account permissions |
| Source stays pending | Check the generation model and schedule interval, or flush explicitly |
| No `vector` or `hybrid` | Set the embedding model, profile ID, and dimension together |
| Both models call the same service | Use separate generation/embedding base URLs and check keys and headers |
| Data is missing after restart | Check that the database URL or `POWERCONTEXT_HOME` has not changed |

After configuring models, [connect an Agent](../integrations/index.md). See [Deploy the Server](../operate/deploy-server.md) for persistent services and the [configuration reference](../operate/configuration.md) for all variables.
