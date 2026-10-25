"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --chat     # 会話履歴を保って対話する

通常モードはツールも会話履歴も持たない「素の」単発呼び出し。
--chat モードでは、同じセッションで会話履歴を保って続けて質問する。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
from time import perf_counter

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = timed_request(
        lambda: client.models.generate_content(model=MODEL, contents=question)
    )

    print_usage(response)
    return response.text


def timed_request(request):
    started_at = perf_counter()
    try:
        return request()
    finally:
        elapsed = perf_counter() - started_at
        print(f"[latency] elapsed_seconds={elapsed:.3f}")


def print_usage(response) -> None:
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else "不明"
    output_tokens = usage.candidates_token_count if usage else "不明"
    print(f"[usage] input_tokens={input_tokens} output_tokens={output_tokens}")


def run_chat() -> None:
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    print("対話モードです。/exit または /quit で終了します。")

    while True:
        try:
            question = input("あなた> ")
        except EOFError:
            break
        if question.strip().lower() in {"/exit", "/quit"}:
            break
        if not question.strip():
            continue

        response = timed_request(lambda: chat.send_message(question))
        print(response.text)
        print_usage(response)


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--chat", action="store_true", help="会話履歴を保って対話する")
    args = parser.parse_args()
    if args.chat and args.question:
        parser.error("--chat と質問の位置引数は同時に指定できません")

    print(f"[model] {MODEL}")
    try:
        if args.chat:
            run_chat()
        else:
            question = args.question or DEFAULT_QUESTION
            print(f"[質問] {question}\n")
            print(ask(question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
