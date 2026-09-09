---
title: 配置安装源
description: 排查 PowerContext 下载失败，临时切换 PyPI 镜像，或配置 uv 和 pip 的持久索引。
---

# 配置安装源

安装超时或找不到版本时，先确认失败的是哪个下载服务。PyPI 镜像只影响 Python 包下载，不会同时改变 uv、Python 解释器、GitHub 或 Agent 插件的下载地址。

| 失败位置 | 检查内容 |
| --- | --- |
| 获取 `install.sh` | 到 `powercontext.oceanbase.io` 的连接、代理和 TLS 证书 |
| 获取 uv | 到 `astral.sh` 及其 GitHub release 下载地址的连接 |
| 获取 Python | uv 错误中给出的 Python 下载地址；可预装 Python 3.11+ 后重试 |
| 解析 Python 包或下载 wheel | 生效的包索引、包文件下载地址、目标版本、平台兼容性 |
| 安装 Agent 集成 | GitHub、宿主的 marketplace，以及宿主所用包管理器的源 |

## 只为本次安装换源

优先沿用已有 uv 配置。需要指定公共镜像时，例如使用清华镜像：

```bash tab="安装脚本"
bash powercontext-install.sh --no-hosts --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

```bash tab="uv"
uv tool install --python ">=3.11,<4" --default-index https://pypi.tuna.tsinghua.edu.cn/simple "powercontext[cli,server]==0.2.0"
```

```bash tab="pip"
python -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple "powercontext[cli,server]==0.2.0"
```

脚本来自[安装指南](install-and-run.md)；pip 命令在已激活的 Python 3.11+ 虚拟环境中执行。
这些参数不改写全局配置。uv 会在工具的安装记录中保留安装设置，之后升级仍可能沿用该索引。

`--default-index` 设置 uv 的默认索引。已经配置的附加索引仍有更高优先级，不要把它当成清除企业索引配置的开关。
如果需要完全不同的索引策略，先检查已有 uv 配置。私有源认证按 [uv 认证文档](https://docs.astral.sh/uv/concepts/indexes/#authentication)设置；不要把凭据放进公开命令示例。

## 安装脚本如何检测

脚本发现 uv 索引环境变量或用户级、系统级配置文件时，会保留配置，由 uv 解析和验证。
它不会用 shell 解析 TOML，也不会将已有的私有源静默换成公共源。

没有自定义配置时，脚本访问 PyPI 的 `powercontext` 包索引，检查目标版本是否列出。请求有超时限制；默认源不可达时，交互终端会询问是否使用清华镜像。
非交互模式会报错并提示使用 `--index-url` 重试。显式选择的索引不可达时也直接报错。
该检查只能确认索引响应与版本条目，后续依赖解析和文件下载仍由 uv 验证。

镜像缺少目标版本时，先确认版本已经发布，再等待同步或明确改用 PyPI：

```bash
bash powercontext-install.sh --no-hosts --version 0.2.0 --index-url https://pypi.org/simple
```

脚本不会为了完成安装而降级或切换到 `master`。如果默认源可达但速度较慢，可直接指定镜像；脚本不会根据 IP 地理位置或一次测速自动换源。

## 为当前终端设置 uv 默认源

环境变量适合在当前终端中多次安装：

```bash tab="macOS / Linux" tab-group="install-platform"
export UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
```

```powershell tab="Windows" tab-group="install-platform"
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

uv 不读取 `pip.conf` 或 `PIP_INDEX_URL`。如果你只配置过 pip，uv 不会自动使用该源。
`uv tool` 读取用户级和系统级配置，忽略当前项目的 `pyproject.toml` 与 `uv.toml`。

## 持久配置 uv 或 pip

需要让后续命令持续使用同一镜像时，再修改所用工具的配置。先检查文件中的已有索引，保留其他设置。

uv 用户配置位于 macOS/Linux 的 `$XDG_CONFIG_HOME/uv/uv.toml`（未设置时为 `~/.config/uv/uv.toml`），或 Windows 的 `%APPDATA%\uv\uv.toml`。
在 `uv.toml` 中添加以下内容；如果已有默认索引，修改该条目，避免重复定义：

```toml
[[index]]
name = "mirror"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

pip 使用自己的配置。需要对当前用户的 pip 安装命令生效时运行：

```bash
python -m pip config --user set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

不要通过 `--extra-index-url` 加一个镜像来掩盖同步问题。uv 的多个索引按顺序解析，找到同名包后不会合并所有源的版本；pip 的策略也不同。
完整规则见 [uv 索引](https://docs.astral.sh/uv/concepts/indexes/)、[uv 配置文件](https://docs.astral.sh/uv/concepts/configuration-files/)及 [pip 配置](https://pip.pypa.io/en/stable/topics/configuration/)。

## 恢复原有设置

清除本轮设置的终端变量：

```bash tab="macOS / Linux" tab-group="install-platform"
unset UV_DEFAULT_INDEX
```

```powershell tab="Windows" tab-group="install-platform"
Remove-Item Env:UV_DEFAULT_INDEX -ErrorAction SilentlyContinue
```

持久配置需要恢复原条目；如果此前没有自定义源，删除本次添加的 uv `[[index]]` 块，或移除本次写入的 pip 设置：

```bash
python -m pip config --user unset global.index-url
```

如果环境变量还在 shell 启动文件中设置，也要移除对应行。工具已经记录了镜像设置时，可以显式用 `--default-index https://pypi.org/simple` 重装目标版本。
