import json
from datetime import datetime
from pathlib import Path

from anki_lingo.application.generate_daily_cards import DailyGenerationResult
from anki_lingo.domain.flashcard import Flashcard
from anki_lingo.interfaces.cli import _print_result, main


def test_config_check_reports_non_secret_runtime_configuration(
    monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setenv("ANKI_DECK_NAME", "English")
    monkeypatch.setenv("ANKI_NOTE_TYPE", "Basic")
    monkeypatch.setenv("OPENCODE_MODEL", "opencode/test-model")

    exit_code = main(["config-check"])

    assert exit_code == 0
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["cefr_level"] == "C1/C2"
    assert payload["provider"] == "opencode"
    assert payload["provider_model"] == "opencode/test-model"
    assert payload["anki_deck"] == "English"


def test_config_check_rejects_missing_anki_target(
    monkeypatch: object, tmp_path: Path
) -> None:
    monkeypatch.delenv("ANKI_DECK_NAME", raising=False)
    monkeypatch.delenv("ANKI_NOTE_TYPE", raising=False)
    monkeypatch.chdir(tmp_path)

    assert main(["config-check"]) == 2


def test_config_check_loads_dotenv_from_working_directory(
    monkeypatch: object, capsys: object, tmp_path: Path
) -> None:
    monkeypatch.delenv("ANKI_DECK_NAME", raising=False)
    monkeypatch.delenv("ANKI_NOTE_TYPE", raising=False)
    monkeypatch.delenv("ANKI_LINGO_CEFR_LEVEL", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "ANKI_DECK_NAME=English\nANKI_NOTE_TYPE=Basic\nANKI_LINGO_CEFR_LEVEL=C2\n",
        encoding="utf-8",
    )

    assert main(["config-check"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["anki_deck"] == "English"
    assert payload["cefr_level"] == "C2"


def test_generate_text_output_prints_run_summary(capsys: object) -> None:
    card = Flashcard(
        "The mayor's promise proved <b>ephemeral</b>.",
        "Ephemeral: Lasting for a very short time.",
        "Fame is often ephemeral.",
    )
    result = DailyGenerationResult((card,), attempts=1, inserted=True, note_ids=(1,))
    started_at = datetime(2026, 9, 16, 14, 30, 5)

    _print_result(result, "text", started_at, 12.34)

    output = capsys.readouterr().out
    assert "Cards generated: 1" in output
    assert "Started at:      2026-09-16 14:30:05" in output
    assert "Duration:        12.3s" in output
    assert "Inserted:        yes" in output


def test_generate_json_output_includes_run_summary(capsys: object) -> None:
    card = Flashcard(
        "The mayor's promise proved <b>ephemeral</b>.",
        "Ephemeral: Lasting for a very short time.",
        "Fame is often ephemeral.",
    )
    result = DailyGenerationResult((card,), attempts=1, inserted=False)
    started_at = datetime(2026, 9, 16, 14, 30, 5)

    _print_result(result, "json", started_at, 3.25)

    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["cards"] == 1
    assert payload["summary"]["started_at"] == "2026-09-16T14:30:05"
    assert payload["summary"]["duration_seconds"] == 3.25
