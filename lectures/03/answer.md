# 第3回 解答

## 演習
- 第1回（素のLLM）とエージェントの回答の違い：素のLLMは「基礎・中級・発展」と回答し、中級を含む課題内容も一般論で説明していた。一方、エージェントは用語集を参照し、正しい「基礎・実装・発展」の内容に加えて、どれか1つで宿題完了となることや原則採点されないことも回答した。
- `--trace` で見えたツール呼び出し（ツール名と引数）：`search_glossary({'query': 'LoRA'})`、`search_glossary({'query': 'QLoRA'})`
- 1つの質問での LLM 呼び出し回数（`requests`）：2回
- 追加したツールと、docstring に書いた説明：`make_quiz(lecture: int) -> str` を追加・登録。docstring：「指定回の確認問題を求められたとき、用語集から問題と答えを作る。」

## 宿題

- 取り組んだレベル：基礎・実装・発展（b）
- やったこと：`app/tools.py` の `search_glossary` の docstring を変更し、検索語を1つずつではなく、関連する用語をまとめて指定してよいと説明した。同じ質問「LoRAとQLoRAの違いは？」を変更前後に `--trace` 付きで実行した。また、`save_learning_log(content)` を追加して `learning_log/` に Markdown で保存するようにし、`app/agent.py` で `requires_approval=True` を付けて登録した。CLI で呼び出し内容を表示して利用者に確認し、承認結果と会話履歴を使ってエージェントを再実行するようにした。
- 結果：基礎では、変更前は `search_glossary({'query': 'LoRA'})` と `search_glossary({'query': 'QLoRA'})` の2回、変更後は `search_glossary({'query': 'LoRA QLoRA'})` の1回になった。`tool_calls` は2回から1回に減ったが、LLM の `requests` は変更前後とも2回だった。実装では、承認待ちの間はファイルが作られず、承認すると保存され、拒否すると保存されないことをテストした。`uv run pytest -q` は15件成功した。
- 気づき・疑問：ツールの docstring はモデルへの説明として働き、検索の回数や引数に影響した。また、保存処理を承認待ちにすることで、ツール呼び出しとファイルへの副作用を分離できた。

### 発展（b）

- やったこと：Codespaces に `npm install -g --ignore-scripts @earendil-works/pi-coding-agent` で Pi をインストールした。公式リポジトリの `packages/coding-agent/src/core/system-prompt.ts` を確認し、Pi を `google/gemini-3.5-flash-lite` で実行して、公開 system prompt の要点と現在の `INSTRUCTIONS` を比較した。比較時は Pi のツール・プロジェクトコンテキスト・skills を無効にし、質問への比較回答だけを行わせた。
- 比較：Pi の標準 prompt は汎用コーディングアシスタントとしての役割、read/bash/edit/write などのツール、簡潔さやパス表記のルールを持つ。設定に応じて project context、skills、作業ディレクトリ、追加指示も含む。一方、AIE2026 の `INSTRUCTIONS` は用語集や講義要約など講座固有ツールの使い方、用語集にない内容を推測しないこと、関連回の明記、宿題へのヒント、学習記録の保存前承認を指示している。
- 気づき・疑問：Pi はコーディング作業を広く支援するための汎用 prompt で、AIE2026 は学習支援の対象・知識源・回答方針を定めた特化型の指示だと分かった。Pi では標準 prompt に加えて環境ごとの project context や skills が組み合わさる。
