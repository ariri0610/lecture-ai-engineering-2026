from types import SimpleNamespace

import app.ask as ask_module
import pytest


def test_chat_keeps_session_across_questions(monkeypatch, capsys):
    questions = iter(["最初の質問", "続けて質問", "/exit"])
    clock = iter([10.0, 10.25, 20.0, 20.5])
    sent = []

    class FakeChat:
        def send_message(self, question):
            sent.append(question)
            return SimpleNamespace(
                text=f"回答{len(sent)}",
                usage_metadata=SimpleNamespace(
                    prompt_token_count=3,
                    candidates_token_count=2,
                ),
            )

    fake_chat = FakeChat()
    fake_client = SimpleNamespace(
        chats=SimpleNamespace(create=lambda model: fake_chat)
    )
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: fake_client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module, "perf_counter", lambda: next(clock))
    monkeypatch.setattr("builtins.input", lambda _: next(questions))

    ask_module.run_chat()

    output = capsys.readouterr().out
    assert sent == ["最初の質問", "続けて質問"]
    assert "回答1" in output
    assert "回答2" in output
    assert output.count("[usage]") == 2
    assert "[latency] elapsed_seconds=0.250" in output
    assert "[latency] elapsed_seconds=0.500" in output


def test_timed_request_reports_duration_when_request_fails(monkeypatch, capsys):
    clock = iter([1.0, 1.375])
    monkeypatch.setattr(ask_module, "perf_counter", lambda: next(clock))

    def fail_request():
        raise RuntimeError("request failed")

    with pytest.raises(RuntimeError, match="request failed"):
        ask_module.timed_request(fail_request)

    assert "[latency] elapsed_seconds=0.375" in capsys.readouterr().out