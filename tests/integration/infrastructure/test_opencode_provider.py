import json
from pathlib import Path

import pytest

from anki_lingo.application.ports import GenerationRequest, ProviderError
from anki_lingo.infrastructure.llm.opencode_provider import (
    OpenCodeProvider,
    OpenCodeSettings,
    parse_structured_output,
)


def test_parser_accepts_json_text_event() -> None:
    event = json.dumps({"type": "text", "text": '{"cards": []}'})

    assert parse_structured_output(event) == {"cards": []}


def test_parser_rejects_unstructured_output() -> None:
    with pytest.raises(ProviderError, match="no valid structured JSON"):
        parse_structured_output("model prose without JSON")


def test_provider_uses_structured_subprocess_output(tmp_path: Path) -> None:
    executable = tmp_path / "fake-opencode"
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "prompt = __import__('sys').argv[-1]\n"
        "if prompt.startswith('Review'):\n"
        "    print(json.dumps({'accepted': True, 'reasons': []}))\n"
        "else:\n"
        "    print(json.dumps({'cards': [{'front': '<b>figure out</b>', "
        "'translation': 'descobrir', 'meaning': 'To understand or solve something.', "
        "'example': 'I figured it out.'}]}))\n"
    )
    executable.chmod(0o755)
    provider = OpenCodeProvider(OpenCodeSettings(executable=str(executable)))

    cards = provider.generate(GenerationRequest(1))
    report = provider.review(GenerationRequest(1), cards)

    assert cards[0].front == "<b>figure out</b>"
    assert report.accepted is True
