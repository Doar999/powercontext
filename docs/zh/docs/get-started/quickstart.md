---
title: 快速开始
description: 安装 PowerContext、配置生成模型、接入 Codex，并在新会话中恢复已保存的决策。
---

# 快速开始

本页以 Codex 为例，运行一个本地 PowerContext Server，配置自动抽取，再验证跨会话的记忆读写。
准备好已安装的 Codex、Git，以及一个生成模型服务的 API Key。PowerContext Server 单独调用模型，不会自动使用 Codex 的模型或登录凭据。

## 1. 安装 PowerContext

已经安装 uv 时，可在 macOS、Linux 或 Windows 上直接使用；否则运行对应操作系统的安装脚本。Windows 支持状态为 `experimental`。
系统安装脚本会复用兼容的 uv 和 Python 3.11+，只下载缺少的组件。

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

三种方式都安装 `0.2.0`。运行 `uv tool update-shell` 后重开终端；使用脚本时，按脚本输出的命令更新 `PATH`。
使用 pip、安装其他版本或下载失败时，见[安装和运行](install-and-run.md)与[配置安装源](configure-package-index.md)。

## 2. 配置生成模型

生成本地环境文件，使用默认本地设置：

```bash
powercontext config init --output .env
```

编辑 `.env`，加入以下配置，并用自己的 API Key 替换占位值。这个示例使用 OpenAI：

```dotenv
OPENAI_API_KEY=replace-with-your-api-key
POWERCONTEXT_SERVER_INFERENCE_GENERATION_MODEL=openai-chat:gpt-4.1-mini
POWERCONTEXT_SERVER_RUNTIME_SCHEDULE_SECONDS=60
```

生成模型负责从采集的 Source 中抽取 Memory；调度器每 60 秒检查待处理 Source。模型调用会使用你的服务额度。
使用其他服务时，先按[配置模型](configure-models.md)设置模型标识、端点和凭据。
将 `.env` 保留在本机，不要提交到 Git。已有文件的加载与保护规则见[配置 Server 环境](configure-server-environment.md)。

## 3. 启动并检查 Server

```bash
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

保持这个终端运行。Server 默认监听 `http://127.0.0.1:8000`，使用本地 SQLite 持久化数据，并在 `/mcp` 提供 MCP。
个人 Dashboard 默认关闭，启用方式见[安装和运行](install-and-run.md)。`server run` 会发现当前目录的 `.env`；上面的显式参数可确保启动时加载刚刚校验的文件。

另开终端，确认 PowerContext 在 `PATH` 中，然后检查：

```bash
powercontext doctor
powercontext ready
powercontext capabilities
```

预期就绪状态为 `ready`，Memory extraction 已启用。`degraded` 表示需要检查已配置的模型服务。
仅配置生成模型时，搜索支持 `auto` 和 `fts`；如需 `vector` 和 `hybrid`，按[模型指南](configure-models.md#启用向量搜索)补充 Embedding。
配置校验不代表真实请求一定成功；[抽取验证步骤](configure-models.md#验证一次真实抽取)用于确认 Source 能生成带来源的 Memory。

## 4. 接入 Codex

在另一个终端中安装同一发布版本的集成：

```bash
powercontext setup codex --source oceanbase/powercontext --ref powercontext-v0.2.0
powercontext doctor codex
```

在项目中打开新的 Codex 会话以加载插件。连接与认证设置见 [Codex 指南](../integrations/codex.md)。
使用其他宿主时，按[对应集成指南](../integrations/index.md)接入，并让 Runtime 与集成使用同一个发布版本。

不同项目不会自动获得独立 Scope；需要隔离项目时，按[Scope 与访问控制](../workflows/scopes-and-access.md)建立边界。

## 5. 保存并恢复一条决策

请 Codex 显式保存一条不含敏感信息的决策：

```text
Remember this project decision in PowerContext: use uv for Python dependency management.
```

请它从 PowerContext 搜索该决策，核对内容和 Memory citation。随后在同一项目中打开新的 Codex 会话，询问：

```text
Search PowerContext: which tool does this project use for Python dependency management?
```

返回结果应包含同一条决策及其 citation。这一步验证记忆写入与跨会话读取；自动抽取的验证使用前面的模型指南。
数据恢复依赖相同的 Server 数据和解析后的 Scope，不依赖原会话保持打开。当前项目文件与用户指令仍优先于历史上下文。

## 继续使用

- [Memory 与上下文](../workflows/memory-and-context.md)：修订、退役已保存信息并控制召回。
- [工作连续性](../workflows/memory-and-handoff.md)：通过 Handoff 交接当前工作。
- [部署 Server](../operate/deploy-server.md)：运行持久的个人服务。
- [诊断与恢复](../operate/troubleshoot.md)：排查安装、Server 或召回问题。
