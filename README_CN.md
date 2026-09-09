# PowerContext

为人和 Agent 交接并继续工作而生的上下文。

[![PyPI version](https://img.shields.io/pypi/v/powercontext)](https://pypi.org/project/powercontext/)
[![License Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-community-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/74cF8vbNEs)

*[English](README.md) · [中文](README_CN.md) · [日本語](README_JP.md)*

工作很少会由开始它的人或 Agent 独自完成。你把任务交给 Agent，Agent 推进一部分，之后可能由你或其他人接手。推理过程和当前状态却常常留在那段对话里。

PowerContext 让上下文跟随工作，跨越不同的对话。你回来时，可以看到已经发生了什么，并从当前进展继续。新的 Agent 也能从同一处接手。

![你和 Agent 交接工作，并基于已存储的上下文继续推进](docs/assets/readme-workflow.svg)

[官方网站](https://powercontext.oceanbase.io/zh/) · [阅读文档](https://powercontext.oceanbase.io/zh/docs/)

## 从当前进展继续

你接手时，会先看到当前工作需要的上下文：已经确认的决定、约束、进展、证据和下一步。你可以从这里继续，也可以把工作交给其他人或 Agent，不需要重新翻阅全部记录。

你决定哪些信息以后仍然有用，哪些内容需要随任务交给下一位接手者。PowerContext 把长期信息保存为 Memory，把当前目标和状态组织成 Handoff。你可以把能够复用的做法记录为 Experience 或 Skill。PowerContext 将每项内容限定在对应的工作范围内，并保留它的来源和历史版本。

## 与你使用的 Agent 一起工作

在 macOS/Linux 上，安装脚本会复用已有的 uv 和 Python 3.11+，只下载缺少的组件：

```bash
curl -fsSL https://powercontext.oceanbase.io/install.sh -o powercontext-install.sh
bash powercontext-install.sh --no-hosts
export PATH="$HOME/.local/bin:$PATH"
```

如果已经安装 uv，可在 macOS、Linux 或 Windows 上直接执行：

```console
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
uv tool update-shell
```

两种方式都安装发布版 `0.2.0`。脚本方式无需预装 Python 或 uv。运行 `uv tool update-shell` 后重开终端；脚本使用自定义目录时，按其输出设置 `PATH`。Windows 安装脚本（`experimental`）和 pip 方式见[安装指南](https://powercontext.oceanbase.io/zh/docs/get-started/install-and-run/)。

生成 Server 环境文件：

```console
powercontext config init --output .env
```

启动 Server 前，编辑 `.env`，加入生成模型与凭据。以下示例使用 OpenAI：

```dotenv
OPENAI_API_KEY=replace-with-your-api-key
POWERCONTEXT_SERVER_INFERENCE_GENERATION_MODEL=openai-chat:gpt-4.1-mini
POWERCONTEXT_SERVER_RUNTIME_SCHEDULE_SECONDS=60
```

Server 使用这个模型从采集的 Source 中抽取 Memory，不会自动使用 Agent 的模型配置或登录凭据。不要将 `.env` 提交到 Git。其他服务与向量搜索设置见[配置模型](https://powercontext.oceanbase.io/zh/docs/get-started/configure-models/)。

校验文件，在单独的终端中启动 Server：

```bash
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

Server 默认使用本地 SQLite 保存上下文。在另一个终端中接入同一发布版本的 Agent 集成，例如已安装的 Codex（需要 Git）：

```bash
powercontext setup codex --ref powercontext-v0.2.0
powercontext doctor codex
```

按[快速开始](https://powercontext.oceanbase.io/zh/docs/get-started/quickstart/)验证模型就绪状态和跨会话记忆。下载失败时，参考[配置安装源](https://powercontext.oceanbase.io/zh/docs/get-started/configure-package-index/)。

Codex 标为 `official`，其他宿主及 Python Agent 框架标为 `community`，Bub 标为 `evaluation`，仅用于评测。
这些标签表示 PowerContext 集成的维护归属和用途，具体功能及可用状态见
[能力矩阵](https://powercontext.oceanbase.io/zh/docs/integrations/capabilities/)。

<table>
<tr>
<td align="center" width="120"><a href="docs/zh/docs/integrations/codex.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/codex-color.png?size=120" alt="Codex" width="48" height="48" /><br /><sub><b>Codex</b></sub></a></td>
<td align="center" width="120"><a href="docs/zh/docs/integrations/claude-code.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/claudecode-color.png?size=120" alt="Claude Code" width="48" height="48" /><br /><sub><b>Claude Code</b></sub></a></td>
<td align="center" width="120"><a href="docs/zh/docs/integrations/dsh.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/deepseek-color.png?size=120" alt="DeepSeek Harness" width="48" height="48" /><br /><sub><b>DeepSeek Harness</b></sub></a></td>
<td align="center" width="120"><a href="integrations/hermes/README.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/hermesagent.png?raw=true&size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/hermesagent.png?raw=true&size=120" alt="Hermes Agent" width="48" height="48" /></picture><br /><sub><b>Hermes Agent</b></sub></a></td>
<td align="center" width="120"><a href="docs/zh/docs/integrations/pi.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/pi.png?size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/pi.png?size=120" alt="Pi Coding Agent" width="48" height="48" /></picture><br /><sub><b>Pi Coding Agent</b></sub></a></td>
<td align="center" width="120"><a href="docs/zh/docs/integrations/openclaw.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/openclaw-color.png?size=120" alt="OpenClaw" width="48" height="48" /><br /><sub><b>OpenClaw</b></sub></a></td>
</tr>
<tr>
<td align="center" width="120"><a href="docs/zh/docs/integrations/opencode.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/opencode.png?size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/opencode.png?size=120" alt="OpenCode" width="48" height="48" /></picture><br /><sub><b>OpenCode</b></sub></a></td>
<td align="center" width="120"><a href="integrations/workbuddy/README.md"><img src="https://thesvg.org/icons/workbuddy/default.svg?size=120" alt="WorkBuddy" width="48" height="48" /><br /><sub><b>WorkBuddy</b></sub></a></td>
<td align="center" width="120"><a href="integrations/bub/README.md"><img src="https://github.com/bubbuild.png?size=120" alt="Bub" width="48" height="48" /><br /><sub><b>Bub</b></sub></a></td>
<td align="center" width="120"><a href="docs/zh/docs/integrations/pydantic-ai.md"><img src="https://thesvg.org/icons/pydantic/default.svg?size=120" alt="Pydantic AI" width="48" height="48" /><br /><sub><b>Pydantic AI</b></sub></a></td>
<td align="center" width="120"><a href="docs/zh/docs/integrations/langchain.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/langchain-color.png?size=120" alt="LangChain" width="48" height="48" /><br /><sub><b>LangChain</b></sub></a></td>
<td align="center" width="120"><a href="docs/zh/docs/integrations/langgraph.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/langgraph.png?size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/langgraph.png?size=120" alt="LangGraph" width="48" height="48" /></picture><br /><sub><b>LangGraph</b></sub></a></td>
</tr>
</table>

应用还可以通过异步 Python Client、HTTP API、MCP 或进程内 Core SDK 使用 PowerContext。请参考[接口说明](https://powercontext.oceanbase.io/zh/docs/develop/interfaces/)选择入口。

想用 Python 逐步体验？从 [22 篇 Jupyter 教程与完整团队工作流](examples/jupyter/README.md)开始，亲手运行 Memory、上下文、交接、Experience、Skill 和真实 Agent。前七篇不需要模型或 API Key。

## 使用 PowerContext 后有什么变化

![PowerContext 在 LoCoMo 和 SWE-bench Pro 上的紧凑对比图](docs/assets/readme-benchmark-summary.svg)

这些对比的评测方法、完整结果和适用边界请见[官网评测页](https://powercontext.oceanbase.io/zh/benchmarks/)。

## 参与构建 PowerContext

```bash
make install
make check
make test
```

完整开发流程请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 进一步了解

- [开始使用](https://powercontext.oceanbase.io/zh/docs/get-started/)
- [接入 Agent](https://powercontext.oceanbase.io/zh/docs/integrations/)
- [管理上下文](https://powercontext.oceanbase.io/zh/docs/workflows/)
- [部署与运维](https://powercontext.oceanbase.io/zh/docs/operate/)
- [开发与 API](https://powercontext.oceanbase.io/zh/docs/develop/)

PowerContext 是 [PowerMem](https://www.powermem.ai/) 的后续项目。

## 许可证

PowerContext 基于 [Apache License 2.0](LICENSE) 发布。
