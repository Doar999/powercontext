# PowerContext

人と Agent が作業を引き継ぎ、継続するためのコンテキスト。

[![PyPI version](https://img.shields.io/pypi/v/powercontext)](https://pypi.org/project/powercontext/)
[![License Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-community-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/74cF8vbNEs)

*[English](README.md) · [中文](README_CN.md) · [日本語](README_JP.md)*

作業を始めた人や Agent が、そのまま最後まで終えるとは限りません。あなたが Agent にタスクを渡し、Agent が途中まで進めた後、あなたや別の誰かが引き継ぐことがあります。そのとき、判断の理由や現在の状態は、その会話に置き去りになりがちです。

PowerContext は、会話をまたいでもコンテキストを作業とともに保持します。あなたが戻ったときは、これまでの経緯を確認して現在の状態から続けられます。新しい Agent も同じところから引き継げます。

![あなたと Agent が作業を引き継ぎ、保存されたコンテキストから継続する流れ](docs/assets/readme-workflow.svg)

[公式サイト](https://powercontext.oceanbase.io/en/) · [ドキュメントを読む](https://powercontext.oceanbase.io/en/docs/)

## 作業の続きをそのまま引き継ぐ

作業を引き継ぐと、確認済みの判断、制約、進捗、根拠、次の手順など、その時点で必要なコンテキストを確認できます。履歴をすべて読み返さずに、そのまま続けることも、別の人や Agent に渡すこともできます。

後から何を残すか、次の担当者に何を渡すかは、あなたが決めます。PowerContext は長く使う情報を Memory として保存し、現在の目標と状態を Handoff にまとめます。再利用できる手順は、Experience または Skill として残せます。PowerContext は各項目を対象となる作業の範囲内に保ち、元の情報源と過去の版を残します。

## 利用中の Agent と接続する

macOS/Linux では、インストーラーが既存の uv と Python 3.11+ を再利用し、不足しているものだけをダウンロードします：

```bash
curl -fsSL https://powercontext.oceanbase.io/install.sh -o powercontext-install.sh
bash powercontext-install.sh --no-hosts
export PATH="$HOME/.local/bin:$PATH"
```

uv がすでにインストールされている場合は、macOS、Linux、Windows で次のコマンドを使用できます：

```console
uv tool install --python ">=3.11,<4" "powercontext[cli,server]==0.2.0"
uv tool update-shell
```

どちらもリリース `0.2.0` をインストールします。スクリプト方式では Python や uv の事前インストールは不要です。`uv tool update-shell` の実行後はターミナルを開き直してください。スクリプトでカスタムディレクトリを使う場合は、表示されたコマンドで `PATH` を設定します。Windows インストーラー（`experimental`）と pip については[インストールガイド](https://powercontext.oceanbase.io/en/docs/get-started/install-and-run/)を参照してください。

Server の環境ファイルを作成します：

```console
powercontext config init --output .env
```

Server を起動する前に `.env` を編集し、生成モデルと認証情報を追加します。以下は OpenAI の例です：

```dotenv
OPENAI_API_KEY=replace-with-your-api-key
POWERCONTEXT_SERVER_INFERENCE_GENERATION_MODEL=openai-chat:gpt-4.1-mini
POWERCONTEXT_SERVER_RUNTIME_SCHEDULE_SECONDS=60
```

Server はこのモデルを使って、収集した Source から Memory を抽出します。Agent のモデル設定やログイン情報は自動的に引き継ぎません。`.env` を Git にコミットしないでください。他のサービスやベクトル検索の設定は[モデル設定ガイド](https://powercontext.oceanbase.io/en/docs/get-started/configure-models/)を参照してください。

設定を検証し、専用のターミナルで Server を起動します：

```bash
powercontext config validate --env-file .env
powercontext server run --env-file .env
```

Server はデフォルトでローカルの SQLite にコンテキストを保存します。別のターミナルで、同じリリースの Agent 連携を設定します。以下はインストール済みの Codex を使う例です（Git が必要です）：

```bash
powercontext setup codex --ref powercontext-v0.2.0
powercontext doctor codex
```

[Quick start](https://powercontext.oceanbase.io/en/docs/get-started/quickstart/)でモデルの準備状態とセッション間の記憶を確認してください。ダウンロードに失敗した場合は[パッケージインデックスの設定](https://powercontext.oceanbase.io/en/docs/get-started/configure-package-index/)を参照してください。

Codex は `official`、他のホストと Python Agent フレームワークは `community`、Bub は評価専用の `evaluation` です。
これらは PowerContext 連携のメンテナンス主体と用途を示すタグです。対応機能と利用可能なバージョンは
[機能一覧](https://powercontext.oceanbase.io/en/docs/integrations/capabilities/)を参照してください。

<table>
<tr>
<td align="center" width="120"><a href="docs/en/docs/integrations/codex.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/codex-color.png?size=120" alt="Codex" width="48" height="48" /><br /><sub><b>Codex</b></sub></a></td>
<td align="center" width="120"><a href="docs/en/docs/integrations/claude-code.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/claudecode-color.png?size=120" alt="Claude Code" width="48" height="48" /><br /><sub><b>Claude Code</b></sub></a></td>
<td align="center" width="120"><a href="docs/en/docs/integrations/dsh.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/deepseek-color.png?size=120" alt="DeepSeek Harness" width="48" height="48" /><br /><sub><b>DeepSeek Harness</b></sub></a></td>
<td align="center" width="120"><a href="integrations/hermes/README.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/hermesagent.png?raw=true&size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/hermesagent.png?raw=true&size=120" alt="Hermes Agent" width="48" height="48" /></picture><br /><sub><b>Hermes Agent</b></sub></a></td>
<td align="center" width="120"><a href="docs/en/docs/integrations/pi.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/pi.png?size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/pi.png?size=120" alt="Pi Coding Agent" width="48" height="48" /></picture><br /><sub><b>Pi Coding Agent</b></sub></a></td>
<td align="center" width="120"><a href="docs/en/docs/integrations/openclaw.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/openclaw-color.png?size=120" alt="OpenClaw" width="48" height="48" /><br /><sub><b>OpenClaw</b></sub></a></td>
</tr>
<tr>
<td align="center" width="120"><a href="docs/en/docs/integrations/opencode.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/opencode.png?size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/opencode.png?size=120" alt="OpenCode" width="48" height="48" /></picture><br /><sub><b>OpenCode</b></sub></a></td>
<td align="center" width="120"><a href="integrations/workbuddy/README.md"><img src="https://thesvg.org/icons/workbuddy/default.svg?size=120" alt="WorkBuddy" width="48" height="48" /><br /><sub><b>WorkBuddy</b></sub></a></td>
<td align="center" width="120"><a href="integrations/bub/README.md"><img src="https://github.com/bubbuild.png?size=120" alt="Bub" width="48" height="48" /><br /><sub><b>Bub</b></sub></a></td>
<td align="center" width="120"><a href="docs/en/docs/integrations/pydantic-ai.md"><img src="https://thesvg.org/icons/pydantic/default.svg?size=120" alt="Pydantic AI" width="48" height="48" /><br /><sub><b>Pydantic AI</b></sub></a></td>
<td align="center" width="120"><a href="docs/en/docs/integrations/langchain.md"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/langchain-color.png?size=120" alt="LangChain" width="48" height="48" /><br /><sub><b>LangChain</b></sub></a></td>
<td align="center" width="120"><a href="docs/en/docs/integrations/langgraph.md"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/dark/langgraph.png?size=120"><img src="https://raw.githubusercontent.com/lobehub/lobe-icons/refs/heads/master/packages/static-png/light/langgraph.png?size=120" alt="LangGraph" width="48" height="48" /></picture><br /><sub><b>LangGraph</b></sub></a></td>
</tr>
</table>

アプリケーションは、非同期 Python クライアント、HTTP API、MCP、または同一プロセス内の Core SDK から PowerContext を利用できます。入口を選ぶには[インターフェースリファレンス](https://powercontext.oceanbase.io/en/docs/develop/interfaces/)を参照してください。

Python で段階的に試すには、チーム作業の一連の流れも学べる [22 本の Jupyter チュートリアル（中国語）](examples/jupyter/README.md)をご覧ください。Memory、コンテキストの準備、Handoff、Experience、Skill、実際の Agent を動かしながら学べます。最初の 7 本はモデルや API キーなしで実行できます。

## PowerContext で何が変わるか

![LoCoMo と SWE-bench Pro における PowerContext の結果をまとめた比較図](docs/assets/readme-benchmark-summary.svg)

比較に用いた評価方法、詳細な結果、適用範囲は[公式ベンチマークページ](https://powercontext.oceanbase.io/en/benchmarks/)を参照してください。

## PowerContext を開発する

```bash
make install
make check
make test
```

開発ワークフロー全体については [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## さらに詳しく

- [はじめる](https://powercontext.oceanbase.io/en/docs/get-started/)
- [Agent と接続する](https://powercontext.oceanbase.io/en/docs/integrations/)
- [コンテキストの管理](https://powercontext.oceanbase.io/en/docs/workflows/)
- [デプロイと運用](https://powercontext.oceanbase.io/en/docs/operate/)
- [開発と API](https://powercontext.oceanbase.io/en/docs/develop/)

PowerContext は [PowerMem](https://www.powermem.ai/) の後継プロジェクトです。

## ライセンス

PowerContext は [Apache License 2.0](LICENSE) のもとで提供されています。
