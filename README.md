# Polyglot CP (PoC)

行ごとに使用言語が変わる競技プログラミングジャッジの **概念実証 (PoC)**。

1 つの提出コードの **各行が別々の言語の独立したプログラム** として実行され、
**ある行の標準出力が次の行の標準入力になる** パイプラインを構成します。
最初の入力は問題の input、最後の行の出力が解答としてジャッジされます。

## コンセプト

- **行ごとの言語ローテーション**: 言語リスト（既定 `python, javascript`）を上から順に各行へ割り当て、リストの最後まで行くと先頭へ循環します（例: 1 行目 Python -> 2 行目 JavaScript -> 3 行目 Python ...）。空行はスロットを消費しません。各行にはエディタ左の gutter に言語バッジが表示されます。
- **独立プロセスのパイプライン**: 各行はその言語の完結した 1 プログラムです。行 N の stdout がそのまま行 N+1 の stdin に渡されます。行間で変数は共有されません（プロセスが別々）。
- **ジャッジ**: バンドルされたサンプル問題 1 問について、最終出力が期待値と一致すれば `AC`、違えば `WA`、ランタイムエラーは `RE`、5 秒超過は `TLE` を表示します。

### サンプル問題 "Double N"

整数 N を受け取り 2 倍して出力する。`input = "5\n"` -> `expected = "10"`。

既定コード（3 行・rotation が Python に戻るところまで見せる）:

- 行 1 (Python): N を読んでそのまま流す
- 行 2 (JavaScript): N を読んで 2 倍して出力
- 行 3 (Python): 値を読んで最終解答として出力

## 実行基盤（2 つのエンジン）

| エンジン | 既定 | 内容 |
|---|---|---|
| local | 有効 | キー不要。この PC の `python3` / `node` を、各行ごとに短命プロセスとして起動。各行 5 秒タイムアウト。 |
| judge0 | 無効 | `.env` で有効化。各行を Judge0 API へ委譲（python=71 / javascript=63）。 |

### セキュリティ注記

local エンジンは **自分のコードを自分の PC で動かす前提** の PoC 限定機能です。
タイムアウトはありますが OS レベルのサンドボックスではありません。
**信頼できない入力を流さないでください。** 本番運用では Judge0 やコンテナ等の
サンドボックスを必須としてください（次段の課題）。

## セットアップ / 起動

```
cd ~/dev/polyglot-cp
npm install
npm run dev
```

- dev server は `http://localhost:5173` で起動します。
- ブラウザで開き、左にコード（各行 = 1 プログラム）・右に結果。「実行 ▶」を押すと各行が順に別言語で実行され、verdict と各行の中間出力（stdin / stdout / stderr / 実行時間）が表示されます。
- 言語ローテーションは画面上部のチェックボックスで切り替えできます。

実行エンジンはローカル実行のため **dev server でのみ動作** します（`npm run preview` の静的配信では `/api/run` は動きません）。

### Judge0 を使う場合

1. `env.example` を `.env` にコピー（このリポジトリは権限制約のため例ファイルを `env.example`(ドット無し) として同梱。手元では `cp env.example .env` してください）。
2. `USE_JUDGE0=true` と `JUDGE0_URL`（必要なら `JUDGE0_KEY` / `JUDGE0_HOST`）を設定。
3. `.env` は gitignore 済みでコミットされません。

## ビルド

```
npm run build
```

`tsc`（型チェック）+ `vite build` が通れば成功です。`build` の前段で
`tools/build_static_problems.py` が走り、問題を静的 JSON 化します（Python 標準ライブラリのみ）。

## 静的サイト構成（バックエンドなし）

495 問の問題集と採点を **完全にフロントだけ** で動かします。

### 問題集 = 静的アセット

`tools/build_static_problems.py` が `problems/<id>/`（statement.md / meta.json / tests）を読み、

- `public/problems/index.json` … ピッカー用の軽量リスト（id / title / topic / difficulty / tags）
- `public/problems/<id>.json` … 問題全体（問題文 + 全テストケース。公開 2 + 非公開 5）

に変換します。`public/` は Vite が `dist/` へそのままコピーするので、`dist/` を
Vercel や GitHub Pages に置くだけで動きます。問題はピッカーで一覧・topic / difficulty / 検索で絞り込み、
選択時に当該 `<id>.json` を遅延 fetch します（重い d4 問題のテスト入力を最初に読み込まないため）。

注: 完全静的のため **非公開テストの入出力もクライアントに配信されます**（devtools で見えます）。
自作練習サイトでは許容範囲ですが、本番のコンテストでは非公開テストはジャッジ API 側に隠してください。

### コード実行 = どこまでブラウザだけで動くか

| 実行系 | 対象言語 | 静的サイトで動くか |
|---|---|---|
| **Pyodide**（WASM 版 CPython・CDN から遅延ロード） | python | ○ 完全クライアント実行 |
| **Web Worker**（ブラウザネイティブ JS） | javascript | ○ 完全クライアント実行 |
| **Judge0 外部 API**（UI で URL/キーを設定・自前バックエンドではない） | ruby / perl / bash / swift / dart / go / c / cpp / rust / java / php / typescript / kotlin / scala / lua / csharp | △ 外部 Judge0 が必要 |
| dev サーバー（`server/runner.ts`）のみ | zig | × Judge0 CE に Zig ランタイムが無く WASM も無いため、`npm run dev` のローカル実行専用 |

つまり **python / javascript はホスティング先がどこでも追加サービス無しで完全に動き**（既定の rotation も
この 2 言語なので、デプロイ直後から A+B などが採点できます）、それ以外は外部 Judge0 を UI で繋ぐと動きます。
Judge0 設定（URL / RapidAPI キー / ホスト）は **localStorage のみに保存**され、バンドルにもコミットにも含まれません。

### 実行エンジンの切り替え

画面右上のセレクタで 2 モード:

- **ブラウザ実行（静的・既定）**: Pyodide + JS Worker + Judge0。`dist` 配信でそのまま動く。
- **ローカル dev サーバー**: `/api/run`（`server/runner.ts`）へ委譲。`npm run dev` 時のみ有効で、
  この PC のツールチェーンを使って 13 言語をローカル実行できる（静的配信では `/api/run` が無いので動かない）。

### GitHub Pages のサブパス対応

ユーザー/組織サイトや Vercel は既定（`base='/'`）でそのまま。プロジェクトサイト
（`https://user.github.io/<repo>/`）に置くときは `BASE_PATH=/<repo>/ npm run build` でビルドしてください。

## 構成

```
polyglot-cp/
  index.html
  vite.config.ts          # react + dev 実行エンジンプラグイン登録・base/.env を読む
  tools/
    build_static_problems.py  # problems/ -> public/problems/*.json （静的化・stdlibのみ）
  server/
    runner.ts             # dev サーバー実行エンジン: /api/run, local/judge0 パイプライン
  src/
    App.tsx               # 画面全体・ピッカー/問題表示・rotation・エンジン切替・提出
    problem.ts            # 既定コード・既定 rotation
    problems.ts           # 静的カタログの fetch（index + 問題遅延ロード）
    types.ts              # 共有型（Verdict / CaseResult / JudgeResult）+ rotation 計算
    engine/
      langs.ts            # 言語表（色/バッジ/担当エンジン/judge0Id）= 唯一の真実
      index.ts            # 採点オーケストレータ（パイプライン + 全ケース判定）
      pyodide.ts          # python: WASM ブラウザ実行
      jsWorker.ts / js.ts # javascript: Web Worker 実行（TLE で terminate）
      judge0.ts           # 外部 Judge0 への直接 fetch + 設定の localStorage 保存
    components/
      ProblemPicker.tsx   # 一覧 + topic/difficulty/検索フィルタ
      ProblemView.tsx     # 問題文（軽量 markdown レンダラ）
      CodeEditor.tsx      # gutter(行番号+言語バッジ) + textarea
      ResultPanel.tsx     # overall verdict + ケースチップ + 各行中間出力
      Judge0Settings.tsx  # Judge0 接続設定パネル
      LangBadge.tsx       # 言語バッジ
    index.css
```

## 実装範囲（できること）

- 495 問の問題ピッカー（topic / difficulty / 検索フィルタ）+ 問題文・サンプル表示
- 提出を **全テストケース（公開 2 + 非公開 5）** に対して採点し、全 AC で AC（途中失敗で打ち切り）
- 行ごとの言語ローテーション割り当て + 行単位の言語バッジ表示
- 独立プロセスの stdout -> stdin パイプライン実行（python=Pyodide / javascript=JS Worker / その他=Judge0）
- stderr / exit code / 実行時間・ケースごとの verdict 可視化
- 完全静的ビルド（`vite build` -> `dist`）で Vercel / GitHub Pages にデプロイ可

## 次段に残したこと

- Judge0 の実接続テスト（キー未設定のため未検証。CORS 許可が前提）
- Python の TLE 強制中断（Pyodide はメインスレッド実行で hard-kill 不可。JS は Worker terminate 済み）
- 非公開テストをクライアントに出さない構成（完全静的とのトレードオフ）
- 提出履歴・順位表・複数ユーザー
- エディタ強化（シンタックスハイライト・行ごとの言語手動上書き）
