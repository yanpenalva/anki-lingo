import json
from collections.abc import Sequence
from dataclasses import dataclass
from html import escape
from math import isfinite
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from anki_lingo.application.ports import (
    AnkiGatewayError,
    AnkiInsertionResult,
    AnkiTarget,
)
from anki_lingo.domain.flashcard import Flashcard


@dataclass(frozen=True, slots=True)
class AnkiConnectSettings:
    url: str = "http://127.0.0.1:8765"
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("AnkiConnect URL must use HTTP or HTTPS")
        if self.timeout_seconds <= 0 or not isfinite(self.timeout_seconds):
            raise ValueError("AnkiConnect timeout must be positive")


class AnkiConnectGateway:
    def __init__(self, settings: AnkiConnectSettings) -> None:
        self._settings = settings

    def preflight(self, target: AnkiTarget) -> None:
        self._request("version")
        decks = self._request("deckNames")
        if not isinstance(decks, list) or target.deck_name not in decks:
            raise AnkiGatewayError(f"Anki deck not found: {target.deck_name}")
        models = self._request("modelNames")
        if not isinstance(models, list) or target.note_type not in models:
            raise AnkiGatewayError(f"Anki note type not found: {target.note_type}")
        fields = self._request("modelFieldNames", {"modelName": target.note_type})
        self._validate_target_fields(target, fields)

    def existing_fronts(self, target: AnkiTarget) -> tuple[str, ...]:
        note_ids = self._request(
            "findNotes", {"query": f'deck:"{_escape_query(target.deck_name)}"'}
        )
        if not isinstance(note_ids, list) or not all(
            type(note_id) is int for note_id in note_ids
        ):
            raise AnkiGatewayError("Anki returned invalid note identifiers")
        if not note_ids:
            return ()
        notes = self._request("notesInfo", {"notes": note_ids})
        if not isinstance(notes, list):
            raise AnkiGatewayError("Anki returned invalid note information")
        fronts: list[str] = []
        for note in notes:
            front = _front_from_note(note, target.front_field)
            if front is not None:
                fronts.append(front)
        return tuple(fronts)

    def add_batch(
        self, target: AnkiTarget, cards: Sequence[Flashcard]
    ) -> AnkiInsertionResult:
        notes = [
            {
                "deckName": target.deck_name,
                "modelName": target.note_type,
                "fields": _fields_for(target, card),
            }
            for card in cards
        ]
        result = self._request("addNotes", {"notes": notes})
        if not isinstance(result, list) or not all(
            type(note_id) is int for note_id in result
        ):
            raise AnkiGatewayError("Anki returned incomplete insertion result")
        return AnkiInsertionResult(len(result), tuple(result))

    def _validate_target_fields(self, target: AnkiTarget, fields: object) -> None:
        if not isinstance(fields, list) or not all(
            isinstance(field, str) for field in fields
        ):
            raise AnkiGatewayError("Anki returned invalid note-type fields")
        required_fields = {target.front_field, target.back_field}
        missing = required_fields.difference(fields)
        if missing:
            raise AnkiGatewayError(
                "Anki note type missing fields: " + ", ".join(sorted(missing))
            )

    def _request(self, action: str, params: dict[str, object] | None = None) -> object:
        body = json.dumps(
            {"action": action, "version": 6, "params": params or {}},
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            self._settings.url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._settings.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as error:
            raise AnkiGatewayError(
                f"AnkiConnect returned HTTP status {error.code}"
            ) from error
        except (URLError, TimeoutError, OSError) as error:
            raise AnkiGatewayError(f"AnkiConnect request failed: {error}") from error
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as parse_error:
            raise AnkiGatewayError("AnkiConnect returned invalid JSON") from parse_error
        if not isinstance(payload, dict):
            raise AnkiGatewayError("AnkiConnect returned invalid response")
        api_error = payload.get("error")
        if api_error is not None:
            raise AnkiGatewayError(f"AnkiConnect error: {api_error}")
        if "result" not in payload:
            raise AnkiGatewayError("AnkiConnect response has no result")
        return payload["result"]


def _escape_query(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _fields_for(target: AnkiTarget, card: Flashcard) -> dict[str, str]:
    escaped_front = escape(card.front, quote=False)
    escaped_front = escaped_front.replace("&lt;b&gt;", "<b>").replace(
        "&lt;/b&gt;", "</b>"
    )
    back = (
        f"Meaning: {escape(card.meaning, quote=False)}<br><br>"
        f"Example: {escape(card.example, quote=False)}"
    )
    return {target.front_field: escaped_front, target.back_field: back}


def _front_from_note(note: object, front_field: str) -> str | None:
    if not isinstance(note, dict):
        raise AnkiGatewayError("Anki returned invalid note")
    fields = note.get("fields")
    if not isinstance(fields, dict):
        raise AnkiGatewayError("Anki returned note without fields")
    value = fields.get(front_field)
    if not isinstance(value, dict):
        raise AnkiGatewayError("Anki returned invalid front field")
    front = value.get("value")
    if front is None:
        return None
    if not isinstance(front, str):
        raise AnkiGatewayError("Anki returned non-string front field")
    return front
