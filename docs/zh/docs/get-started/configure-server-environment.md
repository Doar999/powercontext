---
title: 配置 Server 环境
description: 通过显式环境文件生成、检查、校验并运行 PowerContext。
---

# 配置 Server 环境

本页说明环境文件的生成、保护与加载。首次配置生成或 Embedding 服务时，先按[配置模型](configure-models.md)选择所需设置。

## 1. 生成文件

```bash
powercontext config init --output .env
```

命令生成可启动本地 Server 的基础设置，不会询问模型或 provider 凭据。
自动抽取需要在文件中补充生成模型、凭据和调度间隔；向量搜索还需要 Embedding model、profile ID 和 dimension。
已有 `.env` 时，直接编辑所需条目，不必重新初始化。

如果 `--force` 会删除已有的 model、embedding、推理调度或 provider 凭据配置，命令会明确提示影响，并要求一次默认选择
“否”的确认。用户确认后，命令会先创建权限为 `0600` 的备份，再替换原文件。

在 macOS 和 Linux 上，命令以 `0600` 权限写入私有文件。通过私有环境文件或 secret manager 提供 provider 凭据，不要把它们写入命令行参数或提交到 Git。

Windows 支持为 `experimental`。将文件用于个人服务前，按[部署 Server](../operate/deploy-server.md)限制其 ACL。

## 2. 检查并校验

```bash
powercontext config show --env-file .env
powercontext config validate --env-file .env
```

`config show` 会隐藏已识别的凭据。校验接受只包含 Server 设置的最小环境文件；配置 inference model 或依赖 inference
的 Runtime 功能时，还会检查 Runtime 组装，但不会输出机密。

## 3. 使用同一份配置启动

```bash
powercontext server run
```

`server run` 会发现当前目录的 `.env`。使用 `--env-file <path>` 可选择其他文件，使用 `--no-env-file` 可禁用文件加载。
配置优先级依次为 CLI 参数、进程环境变量、所选文件和默认值。命令会显示实际加载文件的绝对路径，但不会输出凭据。

Server 会按配置启动对应能力。使用 `powercontext ready` 和 `powercontext capabilities` 查看就绪状态和已启用功能。

全部变量、默认值和优先级规则见[配置](../operate/configuration.md)。
