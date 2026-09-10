---
title: 安装和运行
description: 安装 PowerContext、选择发布版本和安装方式，并管理本地 Server。
---

# 安装和运行

首次接入 Agent 时，请按[快速开始](quickstart.md)完成安装、模型配置和验证。本页用于选择安装方式、版本、平台和可选数据库。

## 平台与前置条件

| 平台 | 状态 | 安装入口 |
| --- | --- | --- |
| macOS、Linux | 支持 | Bash 安装脚本或 uv |
| Windows | `experimental` | PowerShell 安装脚本或 uv |

使用脚本只需 Bash、curl 或 wget，以及能访问安装站点和包下载服务的网络。脚本复用已有的 uv 和 Python 3.11+；只有缺少 uv 时才安装 uv，找不到兼容的本地 Python 时才下载 Python 3.12。
你不需要预先安装 Python，也不需要修改系统 Python。

安装 Agent 集成还需要 Git，以及对应宿主要求的工具。脚本不会安装 Agent 应用；缺少 Git 时，可先用 `--no-hosts` 安装 Runtime。
Windows 的宿主与数据库支持取决于各自的平台要求，嵌入式 seekDB 不支持 Windows。

## 安装应用

在 macOS、Linux 或 Windows 上使用 uv 安装。尚未安装 uv 时，选择对应操作系统的脚本。每种方式都会安装 CLI、Server 和默认 SQLite 后端。

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

运行 `uv tool update-shell` 后重开终端。使用 Bash 脚本和自定义目录时，按脚本输出的命令设置 `PATH`。
Windows 命令在缺少 uv 时通过其官方 `install.ps1` 安装 uv，再安装 PowerContext。Windows 支持状态为 `experimental`。

uv 的其他安装方式见[官方安装说明](https://docs.astral.sh/uv/getting-started/installation/)。如果 uv/Python 下载或 PyPI 访问失败，按[配置安装源](configure-package-index.md)区分故障位置。

### pip + venv

如果已有 Python 3.11+ 和 venv 支持，也可以使用 pip。以下以 macOS/Linux 为例：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install "powercontext[cli,server]==0.2.0"
```

### 自动脚本的行为

可以先查看下载的脚本，或阅读[脚本源码](https://github.com/oceanbase/powercontext/blob/master/website/public/install.sh)。
脚本先检查 `PATH` 和 `~/.local/bin` 中的 uv，再通过 uv 查找本地兼容的 Python，包括 uv 已下载的解释器。找到后使用该解释器并禁止额外下载 Python；不会升级已有 uv。
随后在用户级工具环境安装 PowerContext，检查 CLI 能否启动，并输出模型配置入口。
它保留现有 uv 配置，不写入全局包索引配置、模型凭据或 Server 环境文件，也不注册个人服务。

需要同时安装集成时显式选择宿主，例如：

```bash
bash powercontext-install.sh --version 0.2.0 --host codex --host claude-code
```

省略宿主参数会在交互终端中打开 `powercontext setup select`。自动化必须传入 `--host` 或 `--no-hosts`。
下载后执行的形式保留了交互输入；通过管道执行时，请显式传入这些参数。
宿主集成的安装与验证沿用现有 `setup` 命令。某个宿主失败会返回非零状态并报告结果，已安装的 Runtime 会保留。
修复宿主前置条件后，用相同发布 tag 重试该宿主的 `powercontext setup`。

## 选择版本

正常使用选择正式版。Runtime 包与 Agent 集成使用相同的发布版本；下面以 Codex 展示两条命令的对应关系。
先安装并配置 Codex，再执行其 setup 命令。

```bash tab="正式版"
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
powercontext setup codex --ref powercontext-v0.2.0
```

```bash tab="预发布版"
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==<version>"
powercontext setup codex --ref "powercontext-v<version>"
```

```bash tab="源码开发版"
POWERCONTEXT_REF="$(git ls-remote https://github.com/oceanbase/powercontext.git refs/heads/master | cut -f1)"
uv tool install --python ">=3.11,<4" --force "powercontext[cli,server] @ git+https://github.com/oceanbase/powercontext.git@${POWERCONTEXT_REF}"
powercontext setup codex --ref "$POWERCONTEXT_REF"
```

预发布示例中的两个 `<version>` 都要替换成同一个已发布版本，例如 `0.3.0rc1`。
该名称仅说明格式，不表示该版本已经发布。没有预发布版本时，使用正式版；不要退回 `master`。
源码示例使用 Bash，将 `master` 解析成一个 commit 后用于两处安装。源码能力可能尚未发布，见[能力矩阵](../integrations/capabilities.md)。

脚本也接受 `--version`，使用匹配的 `powercontext-v<version>` 集成 tag；它支持从 `0.1.0` 起采用该 tag 命名的发行版本。
安装找不到的版本会报错，不会自动降级。镜像同步延迟的处理见[配置安装源](configure-package-index.md)。

## 配置并启动 Server

完成[模型配置](configure-models.md)后，使用同一环境文件校验和启动：

```bash
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

Server 默认监听 `127.0.0.1:8000`，在 `/mcp` 提供 MCP，创建默认 Scope，并在用户数据目录保存 SQLite 数据。
按 `Ctrl-C` 停止 Server，使用同一数据目录重启会恢复已有数据。

只需要显式 Memory 写入和全文搜索时，可以运行 `powercontext server run`，不配置模型。
这种运行方式不会启用模型抽取或向量搜索。自动抽取需要生成模型和调度配置，向量搜索还需要 Embedding。

在另一个终端检查服务：

```bash
powercontext doctor
powercontext ready
powercontext capabilities
```

`doctor` 检查包、Server 存活和就绪状态。Runtime 或数据库故障返回 `not_ready`；已配置推理服务的故障返回 `degraded`。
状态解释见[诊断与恢复](../operate/troubleshoot.md)。长期运行、Docker、鉴权和远程访问见[部署 Server](../operate/deploy-server.md)。

### 启用 Dashboard

Dashboard 是个人使用和演示的可选内容查看器，默认关闭。它不需要单独安装前端或配置模型。
需要使用时，在受保护的环境文件中设置以下值，并将 token 示例替换为自己的长随机凭据：

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

打开 `http://127.0.0.1:8000/dashboard/home`，输入同一个 token。更改端口后使用实际端口。
该 token 同时用于 Server API 和 MCP，已连接的 Agent 也需配置它。`server run` 会发现当前目录的 `.env`；
使用 `--env-file <path>` 可选择其他文件，使用 `--no-env-file` 可禁用文件加载。

首次登录选择 Server 默认 Scope，未保存内容时显示空状态。通过 Agent 或公开 API 保存一条 Memory，
再刷新同一 Scope 的记忆页即可查看。经验、技能、交接和用量也来自实际保存记录；页面不采集会话、不运行生成，
也不批准候选。Dashboard 和 Agent 必须连接同一个 Server、使用同一个 Scope。

所有 token 持有者使用同一个身份。多成员 RBAC 部署应保持 Dashboard 关闭，通过 API、MCP 或宿主集成访问内容。
网络与凭据配置见[部署 Server](../operate/deploy-server.md)。

## 使用嵌入式 seekDB

在有兼容 `pylibseekdb` wheel 的 Linux/macOS 系统上，将 seekDB extra 加入当前安装：

```bash
uv tool install --python ">=3.11,<4" "powercontext[cli,server,seekdb]==0.2.0"
```

在 `.env` 中设置 `POWERCONTEXT_SERVER_DATABASE_KIND=seekdb`，并移除 `POWERCONTEXT_SERVER_DATABASE_URL`。
seekDB 不接受显式 SQLAlchemy 数据库 URL，固定使用其内置 `test` 数据库。
默认路径为用户数据目录下的 `seekdb`，或设置了 `POWERCONTEXT_HOME` 时的 `$POWERCONTEXT_HOME/seekdb`。
自定义路径使用 `POWERCONTEXT_SERVER_DATABASE_PATH`。更换数据库后端不会自动迁移已有 SQLite 数据。

## 更新安装

先阅读目标版本的发行说明，然后将 Runtime 和使用中的集成一起更新到明确版本：

```bash
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==<version>"
powercontext setup codex --ref "powercontext-v<version>"
```

替换两个 `<version>` 后执行，重启 Server，再开启新的 Agent 会话。
固定版本的 uv tool 安装会保留版本约束，`uv tool upgrade powercontext` 不会自行跨过这个约束。
脚本可用新的 `--version` 重复安装；指定的宿主仍需要一起更新。
更新包不会自行删除数据，但数据库兼容性与迁移要求应以目标版本的发行说明为准。

## 为 Python 项目安装 SDK

应用需要导入异步 Client SDK 时，将依赖加入应用自己的环境：

```bash
uv add "powercontext[client]==0.2.0"
```

`client` 用于 Python SDK，`builtin` 用于进程内组合，`server` 用于服务，`cli` 用于命令行。
uv tool 隔离环境中的包不能直接被其他 Python 项目导入。更多用法见[接口说明](../develop/interfaces.md)。
