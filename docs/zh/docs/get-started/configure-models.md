---
title: 配置模型
description: 配置生成与 Embedding 服务，启用自动抽取，并验证带来源的 Memory 和向量搜索。
---

# 配置模型

PowerContext Server 使用生成模型处理 Source，使用 Embedding 模型建立和查询向量索引。
这些配置独立于 Agent 宿主的模型和登录凭据。先按[安装指南](install-and-run.md)安装，再选择适合你的服务配置。

| 配置 | 可以使用的能力 |
| --- | --- |
| 未配置模型 | 显式 Memory 写入、全文搜索、Dashboard 和 MCP |
| 生成模型与调度间隔 | 自动从 Source 抽取 Memory |
| Embedding 模型、profile ID 与 dimension | 向量搜索与混合搜索 |

## 配置生成模型

如果还没有环境文件，先生成一个：

```bash
powercontext config init --output .env
```

`config init` 生成本地 Server 的基础配置，不会询问模型和 API Key。编辑 `.env`，加入所选服务的设置；已有文件直接修改对应条目。
以下模型名称是配置示例，服务账号需要有对应模型的访问权限。

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

兼容服务应提供所选适配器需要的接口，并支持 PowerContext 使用的结构化输出；只有相同的 URL 形式不代表模型兼容。
端点需要覆盖时，设置对应的 `POWERCONTEXT_SERVER_INFERENCE_GENERATION_BASE_URL`，不要将生成端点误用为 Embedding 端点。
本地服务忽略鉴权时，可以填入其接受的非秘密占位值。

调度器每 60 秒检查待处理 Source。只有生成模型而没有该间隔时，需要显式 flush 才会处理 Source。
模型调用会使用你的服务额度。凭据放在环境文件或部署方的 secret manager 中，不要写入仓库、Memory 或分享的日志。

## 启用向量搜索

在已有生成配置之外，再加入 Embedding 配置。以下示例使用 OpenAI，并复用 `OPENAI_API_KEY`：

```dotenv
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_MODEL=openai:text-embedding-3-small
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_PROFILE_ID=openai-text-embedding-3-small-1536-unit-v1
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_DIMENSION=1536
```

模型、profile ID 和 dimension 必须同时设置。profile ID 标识模型、维度与 normalization 的组合；默认 normalization 为 `unit`。
选择其他 Embedding 模型时，按其实际输出维度修改配置，并使用对应的 profile ID。已有向量数据更换模型或维度前，阅读[向量搜索指南](../workflows/configure-vector-search.md)。

生成和 Embedding 可以使用不同端点。兼容 Embedding 服务使用 `openai:模型名` 标识和独立端点：

```dotenv
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_MODEL=openai:replace-with-your-embedding-model
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_BASE_URL=https://your-embedding-provider.example/v1
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_PROFILE_ID=your-provider-your-model-1536-unit-v1
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_DIMENSION=1536
```

上面的 `1536` 也是需要核对的示例值。两个 OpenAI-compatible 服务共用一个 Key 时可使用 `OPENAI_API_KEY`。
若它们使用不同 Key，可在私有环境文件中为 Embedding 单独设置 Authorization header：

```dotenv
POWERCONTEXT_SERVER_INFERENCE_EMBEDDING_HEADERS={"Authorization":"Bearer replace-with-your-embedding-api-key"}
```

此字段保存实际 header 值，不会自动展开 `${VARIABLE}`。Anthropic 的生成配置不会提供 Embedding 服务，需要另行选择并配置。

## 校验并启动

```bash
powercontext config show --env-file .env
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

`config show` 隐藏已识别的凭据。`config validate` 检查配置和 Runtime 组装，不能代替真实模型调用。
CLI 不会自动搜索 `.env`；校验和启动都要显式传入同一个文件。加载优先级见[配置 Server 环境](configure-server-environment.md)。

在另一个终端运行：

```bash
powercontext doctor
powercontext ready
powercontext capabilities
```

预期 readiness 为 `ready`，Memory extraction 已启用。配置 Embedding 后，search mode 还应包含 `vector` 和 `hybrid`。
这些默认连接到 `http://127.0.0.1:8000`；使用其他地址或认证时，按[配置参考](../operate/configuration.md)设置 Client。

## 验证一次真实抽取

下面使用无鉴权的本地 Server，写入一条测试 Source，再检查抽取结果。先保持 Server 运行。
命令使用 Bash；Windows 可在 Git Bash 中执行。这里通过 uv 运行 Python，解析 JSON 不要求系统提供 `python` 命令。

```bash
SCOPE_ID="$(curl -fsS http://127.0.0.1:8000/v1/scopes/default \
  | uv run --no-project --python ">=3.11,<4" python -c 'import json, sys; print(json.load(sys.stdin)["scope_id"])')"
SOURCE_ID="model-check-$(date +%s)-$$"
curl -fsS -X POST http://127.0.0.1:8000/v1/sources/content \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\",\"source_id\":\"${SOURCE_ID}\",\"content\":\"Project decision: use uv for Python dependency management. Preserve this decision for future maintainers.\"}"
```

保留响应中的 `position`。显式 flush 同一 Scope，不必等待调度间隔：

```bash
curl -fsS -X POST http://127.0.0.1:8000/v1/memory/flush \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\"}"
curl -fsS -X POST http://127.0.0.1:8000/v1/memory/entries/list \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\"}"
```

flush 的 `current_cursor` 应不小于 capture 的 `position`。调度器已经处理该 Source 时，`status: "idle"` 也是有效结果。
在 Memory 结果中找到内容对应且 `source_refs` 包含该 Source 的 entry，并记录其 `citation.entry_id`。
如果 cursor 推进但没有对应条目，继续检查模型用量和日志，不能仅凭游标认定模型抽取成功。

## 验证向量搜索

配置了 Embedding 时，继续查询同一 Scope：

```bash
curl -fsS -X POST http://127.0.0.1:8000/v1/memory/search \
  -H 'content-type: application/json' \
  -d "{\"scope_id\":\"${SCOPE_ID}\",\"query\":\"Python dependency management\",\"mode\":\"vector\",\"limit\":50}"
powercontext stats --scope-id "$SCOPE_ID"
```

搜索结果应返回 `mode: "vector"`，包含刚才的 entry，且 `matched_by` 包含 `vector`。`stats` 用于检查模型用量。
未配置 Embedding 时跳过此步骤，继续使用全文搜索。

## 常见问题

| 现象 | 处理方式 |
| --- | --- |
| readiness 为 `degraded` | 检查模型标识、Key、端点与账号权限 |
| Source 一直 pending | 检查生成模型和调度间隔，或显式 flush |
| 没有 `vector` 或 `hybrid` | 同时配置 Embedding model、profile ID 和 dimension |
| 两个模型的请求去了同一个服务 | 使用各自的 generation/embedding base URL，核对 Key 和 header |
| 重启后数据不见了 | 检查是否仍使用同一数据库 URL 或 `POWERCONTEXT_HOME` |

模型配置完成后，按[集成指南](../integrations/index.md)接入 Agent。长期运行见[部署 Server](../operate/deploy-server.md)，全部变量见[配置参考](../operate/configuration.md)。
