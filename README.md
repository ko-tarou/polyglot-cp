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

`tsc`（型チェック）+ `vite build` が通れば成功です。

## 構成

```
polyglot-cp/
  index.html
  vite.config.ts          # react + 実行エンジンプラグインを登録、.env を読む
  server/
    runner.ts             # 実行エンジン: /api/run middleware, local/judge0, パイプライン, 判定
  src/
    main.tsx
    App.tsx               # 画面全体・rotation バー・実行ボタン
    problem.ts            # サンプル問題・既定言語・既定コード
    types.ts              # レスポンス型 + languageForLines (rotation 計算)
    components/
      CodeEditor.tsx      # gutter(行番号+言語バッジ) + textarea
      LangBadge.tsx       # 言語バッジ
      ResultPanel.tsx     # verdict + 各行中間出力
    index.css
```

## 実装範囲（このPoCでできること）

- 行ごとの言語ローテーション割り当て + 行単位の言語バッジ表示
- 独立プロセスによる stdout -> stdin パイプライン実行（local: python3 / node）
- 各行 5 秒タイムアウト・stderr / exit code / 実行時間の可視化
- サンプル問題 1 問の AC / WA / RE / TLE 判定
- Judge0 連携コード（`.env` でオプトイン）

## 次段に残したこと

- Judge0 の実接続テスト（本 PoC ではコードのみ・キー未設定で未検証）
- 対応言語の拡張（C / C++ / Go / Rust 等。`server/runner.ts` の `LANGS` と UI の `SUPPORTED_LANGUAGES` に追加）
- 複数問題・問題管理（DB / 問題セット）とテストケース複数化
- 本番グレードのサンドボックス（local 実行の置き換え）
- 提出履歴・順位表・複数ユーザー
- エディタ強化（シンタックスハイライト・行ごとの言語手動上書き）
