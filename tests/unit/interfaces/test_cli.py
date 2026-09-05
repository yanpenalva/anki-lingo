import json
from pathlib import Path

from anki_lingo.interfaces.cli import main


def test_config_check_reports_non_secret_runtime_configuration(
    monkeypatch: object, capsys: object
) -> None:
    monkeypatch.setenv("ANKI_DECK_NAME", "English")
    monkeypatch.setenv("ANKI_NOTE_TYPE", "Basic")

    exit_code = main(["config-check"])

    assert exit_code == 0
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["cefr_level"] == "C1/C2"
    assert payload["provider"] == "opencode"
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
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "ANKI_DECK_NAME=English\nANKI_NOTE_TYPE=Basic\nANKI_LINGO_CEFR_LEVEL=C2\n",
        encoding="utf-8",
    )

    assert main(["config-check"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["anki_deck"] == "English"
    assert payload["cefr_level"] == "C2"
