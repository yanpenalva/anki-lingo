import json

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
    assert payload["anki_deck"] == "English"


def test_config_check_rejects_missing_anki_target(monkeypatch: object) -> None:
    monkeypatch.delenv("ANKI_DECK_NAME", raising=False)
    monkeypatch.delenv("ANKI_NOTE_TYPE", raising=False)

    assert main(["config-check"]) == 2
