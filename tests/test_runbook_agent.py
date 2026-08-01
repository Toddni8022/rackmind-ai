import agents.runbook_agent as runbook_agent


def test_answer_question_skips_ai_call_when_no_docs_match(monkeypatch):
    monkeypatch.setattr(runbook_agent, "search_runbooks", lambda question: [])

    calls = []
    monkeypatch.setattr(runbook_agent, "generate", lambda prompt: calls.append(prompt))

    answer = runbook_agent.answer_question("What causes CRC errors?")

    assert "No matching runbook entries were found" in answer
    assert calls == []


def test_answer_question_builds_prompt_with_runbook_context_and_question(monkeypatch):
    monkeypatch.setattr(
        runbook_agent,
        "search_runbooks",
        lambda question: ["Replace faulty SFP optics.", "Check cable seating."],
    )

    captured = {}

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return "AI ANSWER"

    monkeypatch.setattr(runbook_agent, "generate", fake_generate)

    answer = runbook_agent.answer_question("What causes CRC errors?")

    assert answer == "AI ANSWER"
    assert "What causes CRC errors?" in captured["prompt"]
    assert "Replace faulty SFP optics." in captured["prompt"]
    assert "Check cable seating." in captured["prompt"]
