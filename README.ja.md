# 電子部品3Dモデル作成スキル

[English](README.md) · [共通指示](SKILL.md) · [変更履歴](CHANGELOG.md) · [MITライセンス](LICENSE)

商品URL・型番・寸法図から、AIが **CadQuery＋uv** で電子部品の色付きSTEPを作成・修正するための[Agent Skills形式](https://agentskills.io/specification)のスキルです。資料確認、形状作成、STEP再読込・寸法検証、プレビュー確認までを扱います。

作業フォルダに追加するのは`models/<部品型番>/`だけです。生成コード・資料・仮想環境・キャッシュは別の作業環境で管理します。画像から自動変換する仕組みではなく、AIが資料を読んで部品ごとの形状を実装します。

## 必要なもの

**モデル生成にはPythonとuvが必要です。** スキルのインストールだけではCADの実行環境は入りません。

| 必要なもの | 用途 |
| --- | --- |
| CPython **3.11・3.12・3.13のいずれか** | モデル生成コードの実行。3.11固定ではありません。 |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Python環境・依存関係の管理。Python本体の導入もできます。 |
| [Node.js](https://nodejs.org/en/download) **22.20以降**と[Git](https://git-scm.com/install/) | 推奨する[skills CLI](https://github.com/vercel-labs/skills)での導入に使用します。 |
| ファイル操作・シェル実行・画像確認ができるAIツール | 資料の取得・確認、モデル作成、画像による仕上がり確認に使用します。 |
| PopplerなどのPDF画像化ツール | PDFの寸法図を扱う場合に必要です。 |

同梱ロックはCadQuery **2.8.0**を使い、[この版自体がPython 3.11以上を要求します](https://pypi.org/project/cadquery/2.8.0/)。本プロジェクトの対応範囲は`>=3.11,<3.14`です。3.14以降はまだ対象に含めていません。CadQueryや描画用ライブラリは、AIがuvで専用環境へ導入します。FreeCADは不要です。

## 導入手順

### 1. uvとPythonを準備する

uvが未導入なら[公式の導入手順](https://docs.astral.sh/uv/getting-started/installation/)を参照してください。WindowsでWinGetを使う場合は次のコマンドです。

```powershell
winget install --id=astral-sh.uv -e
```

macOSでHomebrewを使う場合：

```sh
brew install uv
```

Linuxやその他の導入方法は上記の公式手順を参照してください。導入直後にコマンドが見つからない場合は、ターミナルを開き直します。

対応するPythonがまだない場合は、[uvから導入できます](https://docs.astral.sh/uv/guides/install-python/)。

```sh
uv python install 3.13
```

3.13は一例で、3.11・3.12も使えます。uvを使う場合はPythonのインストーラーを別に用意する必要はありません。準備できたかは次で確認できます。

```sh
uv --version
uv python find ">=3.11,<3.14"
node --version
git --version
```

### 2. スキルをインストールする

```sh
npx skills add Yarnadori/electronic-component-cad -g
```

利用するAIツールを選びます。`-g`は個人用の保存先へ導入する指定で、作業フォルダにスキル自体のファイルも増やしません。対象をまとめて指定する場合：

```sh
npx skills add Yarnadori/electronic-component-cad -g -a codex claude-code gemini-cli cursor github-copilot windsurf
```

| AIツール | `--agent`の指定値 |
| --- | --- |
| Codex | `codex` |
| Claude Code | `claude-code` |
| Gemini CLI | `gemini-cli` |
| Cursor | `cursor` |
| GitHub Copilot | `github-copilot` |
| Windsurf | `windsurf` |

その他は[対応ツール一覧](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)を参照してください。`--list`で導入前の一覧確認、`--copy`でコピー方式を選べます。スキルが見つからない場合はAIツールを再読み込み・再起動してください。これはインストール先の対応であり、すべてのAIによるモデル作成の品質を保証するものではありません。

### 手動で導入する場合

各ツールでは導入方法を1つ選んでください。`assets`等も含めた**フォルダ全体**を、`electronic-component-cad`という名前で配置します。

| AIツール | 個人用の手動配置先 |
| --- | --- |
| Codex | `~/.codex/skills/electronic-component-cad/`。Codexの保存先を変更している場合はその配下 |
| Claude Code | `~/.claude/skills/electronic-component-cad/`。[公式説明](https://code.claude.com/docs/en/skills) |
| Gemini CLI | `gemini skills install https://github.com/Yarnadori/electronic-component-cad.git`。[公式説明](https://geminicli.com/docs/cli/skills/) |

他のAIでは対応するスキル保存先へ配置するか、`SKILL.md`を明示的に読ませます。`agents/openai.yaml`はCodexの表示用情報で、処理自体は特定のAI専用APIに依存しません。Gitによる手動取得ならNode.jsは不要ですが、モデル生成にはPythonとuvが必要です。

## 使い方

Codexでは商品URLや型番と一緒に依頼します。

```text
$electronic-component-cad
この商品のKiCad用3Dモデルを作成して：商品URL
```

Claude Codeでは`/electronic-component-cad`を使います。既存モデルの修正にも対応します。AIが図面・写真を確認してCadQueryコードを作り、出力STEPを再読込して寸法・ソリッド・色・部材の重なりを検証し、描画画像を確認します。

成果物は`models/<部品型番>/`内のSTEP、画像、検証結果、寸法・原点・近似範囲の説明です。編集可能なソースと資料は別の作業環境に保持し、必要なときに取り出せます。同じ絶対パスのプロジェクトでは環境を再利用します。プロジェクトを別の場所へ移すと、新しい作業環境になります。

## 更新方法

**自動更新はしません。** skills CLIで個人用に導入した場合：

```sh
npx skills update electronic-component-cad -g
```

Git cloneで取得した場合は、そのフォルダ内で`git pull --ff-only`を実行します。他の方法で導入した場合は各ツールの更新方法に従ってください。[CLI仕様](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)と[変更履歴](CHANGELOG.md)も参照できます。

スキルを更新しても、編集済みの作業環境の上書き、Pythonの切替、モデルの再生成、旧版が作成したファイルの削除は行いません。既存環境に以前のPython指定が残っている場合、切替は別途明示的に行います。

## 困ったとき・確認範囲

| 症状 | 確認すること |
| --- | --- |
| `uv`等のコマンドが見つからない | 導入後にターミナル・AIツールを再起動し、PATHを反映します。 |
| 対応するPythonがない | `uv python install 3.13`で導入し、上記の対応範囲を確認します。 |
| 依存関係を取得できない | 初回は通信が必要です。`--offline`は導入済み・キャッシュ利用時の指定です。 |
| PDFの図面を確認できない | PDF画像化ツールを導入するか、読める図面画像を用意します。テキストだけで画像確認済みにはしません。 |
| プレビューを描画できない | OSや画面のない環境の描画バックエンドを確認します。[検証範囲](VALIDATION.md)も参照してください。 |

環境側の通信・書込み制限を解除するスキルではありません。メーカーのPDF・商品写真・部品モデルはこの配布物に含めていません。KiCad上の実配置、造形可能性、ねじのかみ合い、熱・電気特性は別途確認が必要です。

## 開発・貢献

不具合報告やテスト方法は[CONTRIBUTING.md](CONTRIBUTING.md)、実施した確認は[VALIDATION.md](VALIDATION.md)、内部の作業環境と独立ライブラリ作成モードは[APIガイド](references/project-api.md)にあります。

手順・コードは[MITライセンス](LICENSE)です。依存ソフトと別途取得する資料には、それぞれの利用条件が適用されます。
