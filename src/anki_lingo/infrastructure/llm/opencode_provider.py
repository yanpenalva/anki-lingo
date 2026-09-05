import json
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite

from pydantic import ValidationError

from anki_lingo.application.ports import (
    GenerationRequest,
    ProviderError,
    QualityReport,
)
from anki_lingo.domain.flashcard import Flashcard, FlashcardValidationError
from anki_lingo.infrastructure.llm.prompts import generation_prompt, review_prompt
from anki_lingo.infrastructure.llm.schemas import GenerationPayload, QualityPayload


@dataclass(frozen=True, slots=True)
class OpenCodeSettings:
    executable: str = "opencode"
    model: str | None = None
    timeout_seconds: float = 120.0
    working_directory: str | None = None

    def __post_init__(self) -> None:
        if not self.executable.strip():
            raise ValueError("OpenCode executable must not be empty")
        if self.timeout_seconds <= 0 or not isfinite(self.timeout_seconds):
            raise ValueError("OpenCode timeout must be positive")


class OpenCodeProvider:
    def __init__(self, settings: OpenCodeSettings) -> None:
        self._settings = settings

    def generate(self, request: GenerationRequest) -> tuple[Flashcard, ...]:
        payload = self._run(generation_prompt(request))
        try:
            result = GenerationPayload.model_validate(payload)
        except ValidationError as error:
            raise ProviderError("OpenCode returned invalid card schema") from error
        try:
            return tuple(
                Flashcard(
                    front=card.front,
                    meaning=card.meaning,
                    example=card.example,
                )
                for card in result.cards
            )
        except FlashcardValidationError as error:
            raise ProviderError("OpenCode returned invalid card fields") from error

    def review(
        self, request: GenerationRequest, cards: Sequence[Flashcard]
    ) -> QualityReport:
        payload = self._run(review_prompt(request, cards))
        try:
            result = QualityPayload.model_validate(payload)
        except ValidationError as error:
            raise ProviderError("OpenCode returned invalid quality schema") from error
        try:
            return QualityReport(result.accepted, tuple(result.reasons))
        except ValueError as error:
            raise ProviderError("OpenCode returned invalid quality report") from error

    def _run(self, prompt: str) -> object:
        command = [self._settings.executable, "run", "--format", "json"]
        if self._settings.model:
            command.extend(["--model", self._settings.model])
        command.append(prompt)
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                cwd=self._settings.working_directory,
                text=True,
                timeout=self._settings.timeout_seconds,
            )
        except FileNotFoundError as error:
            raise ProviderError("OpenCode executable not found") from error
        except subprocess.TimeoutExpired as error:
            raise ProviderError("OpenCode timed out") from error
        except OSError as error:
            raise ProviderError("OpenCode process could not start") from error
        if completed.returncode != 0:
            raise ProviderError(f"OpenCode exited with status {completed.returncode}")
        return parse_structured_output(completed.stdout)


def parse_structured_output(output: str) -> object:
    direct = _parse_json(output)
    if direct is not None:
        event_payload = _event_payload(direct)
        return event_payload if event_payload is not None else direct
    for line in output.splitlines():
        event = _parse_json(line)
        payload = _event_payload(event)
        if payload is not None:
            return payload
    raise ProviderError("OpenCode returned no valid structured JSON")


def _parse_json(value: str) -> object | None:
    try:
        parsed: object = json.loads(value)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict | list):
        return parsed
    return None


def _event_payload(event: object) -> object | None:
    if not isinstance(event, dict):
        return None
    if "cards" in event or "accepted" in event:
        return event
    if event.get("type") == "text":
        payload = _text_payload(event.get("text"))
        if payload is not None:
            return payload
    part = event.get("part")
    if not isinstance(part, dict):
        properties = event.get("properties")
        if not isinstance(properties, dict):
            return None
        part = properties.get("part")
    if not isinstance(part, dict) or part.get("type") != "text":
        return None
    return _text_payload(part.get("text"))


def _text_payload(value: object) -> object | None:
    if not isinstance(value, str):
        return None
    return _parse_json(value)
