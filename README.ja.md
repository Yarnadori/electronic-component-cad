# 電子部品3Dモデル作成スキル

[English](README.md) · [共通指示](SKILL.md) · [MITライセンス](LICENSE)

商品URL・型番・寸法図を指定し、**CadQuery＋uv**で電子部品の色付きSTEPを作成・修正するためのスキルです。資料確認、形状の作り込み、STEP再読込・寸法検証、最終画像の確認までを扱います。

特定のAI専用APIを使わず、[Agent Skills形式](https://agentskills.io/specification)の`SKILL.md`を入口にしています。空のプロジェクト用に、生成・検証・描画の共通コードとロック済み環境も同梱しています。部品形状そのものは、AIが対象資料を確認して実装します。

## 導入

[skills CLI](https://github.com/vercel-labs/skills)で、利用するAIツールを選んでインストールできます。Node.js 22.20以降とGitが必要です。

```sh
npx skills add Yarnadori/electronic-component-cad
```

標準では現在のプロジェクトに導入します。どのプロジェクトでも使う個人用インストールには`-g`を付けてください。対象をまとめて指定する場合は、次のように実行できます。

```sh
npx skills add Yarnadori/electronic-component-cad -a codex claude-code gemini-cli cursor github-copilot windsurf
```

| AIツール | `--agent`の指定値 |
| --- | --- |
| Codex | `codex` |
| Claude Code | `claude-code` |
| Gemini CLI | `gemini-cli` |
| Cursor | `cursor` |
| GitHub Copilot | `github-copilot` |
| Windsurf | `windsurf` |

ほかの対応先は[skills CLIの対応ツール一覧](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)を参照してください。CLIが各ツールの保存先を選び、一部では共通の`.agents/skills`を使います。`--list`でインストール前の一覧確認、`--copy`でシンボリックリンクを使わないコピー方式を選べます。このリポジトリはルートの`SKILL.md`から検出でき、スクリプト・ひな形も一緒に導入されます。GitHubからの導入に別途パッケージ登録は不要です。[更新・削除などのCLI仕様](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)も参照できます。

### 手動で導入する場合

各ツールでは導入方法を1つ選んでください。手動配置ではフォルダ名を`electronic-component-cad`にし、`assets`なども含めて丸ごと配置します。

| AI環境 | 導入方法 |
| --- | --- |
| Codex | 通常は`~/.codex/skills/electronic-component-cad/`。`CODEX_HOME`を変更している場合はその配下の`skills/` |
| Claude Code | `~/.claude/skills/electronic-component-cad/`。[公式説明](https://code.claude.com/docs/en/skills) |
| Gemini CLI | `gemini skills install https://github.com/Yarnadori/electronic-component-cad.git`。[公式説明](https://geminicli.com/docs/cli/skills/) |
| その他のAI | 対応するスキル検索先へ配置するか、`SKILL.md`を明示的に読ませる |

例えばCodexの標準の個人用フォルダへは、PowerShellやPOSIXシェルで次のように取得できます。

```sh
git clone https://github.com/Yarnadori/electronic-component-cad.git "$HOME/.codex/skills/electronic-component-cad"
```

既存の同名フォルダには上書きせず、内容を確認して更新してください。新しいスキルが見つからない場合は、AI環境を再読み込み・再起動します。`agents/openai.yaml`はCodexの表示用情報であり、他のAIで使う際に必須ではありません。

## 依頼例

Codexでは次のように指定します。

```text
$electronic-component-cad
この商品のKiCad用3Dモデルを作成して：商品URL
```

Claude Codeでは`/electronic-component-cad`と商品URLを渡します。スキルを自動読込しないAIには「このフォルダのSKILL.mdを読み、指定した部品の3Dモデルを作成して」と依頼できます。既存モデルの修正にも使えます。

成果物は色付きSTEP、編集できるPythonソース、STEPから描いた画像、検証JSON、寸法・座標・近似範囲の説明です。新規プロジェクトの標準保存先は`models/<部品型番>/`、資料は`references/<部品型番>/`です。

## 必要な環境と確認範囲

ファイル操作・シェル実行・画像を見る機能、uv、Python 3.11、PDF画像化用のPoppler等が必要です。同梱ロックはCadQuery 2.8.0を使います。初回依存導入や資料取得には通信が必要ですが、手元の資料・キャッシュも利用できます。環境側の通信・書込み制限を解除するスキルではありません。

Windows上でひな形の生成・STEP検証・描画を確認しています。他OSやClaude Code・Gemini CLIでの一連の実行は未検証です。KiCad上の実配置や造形可能性、ねじのかみ合い、熱・電気特性も別途確認が必要です。

メーカーのPDF・商品写真・既存の部品モデルは配布物に含めていません。MITライセンスは本パッケージの手順・コードに適用され、依存ソフトや別途取得する資料にはそれぞれの条件が適用されます。

## 空のプロジェクトで始める

```text
python スキルフォルダ/scripts/init_project.py 新しい空の作業フォルダ
```

既存ファイルのある保存先には書き込みません。作成後は[APIと実行手順](references/project-api.md)に従ってください。すでに部品ライブラリがある場合は、その生成・検証処理を再利用します。

検証コマンドは[英語README](README.md#development-checks)、実施範囲は[VALIDATION.md](VALIDATION.md)にあります。
