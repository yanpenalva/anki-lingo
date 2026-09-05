from dataclasses import dataclass
from math import isfinite
from os import environ

from anki_lingo.application.ports import AnkiTarget, GenerationRequest
from anki_lingo.infrastructure.anki.ankiconnect_gateway import AnkiConnectSettings
from anki_lingo.infrastructure.llm.opencode_provider import OpenCodeSettings


class ConfigurationError(ValueError):
    """Raised when runtime configuration is incomplete or invalid."""


@dataclass(frozen=True, slots=True)
class AppConfig:
    generation_request: GenerationRequest
    anki_target: AnkiTarget
    anki_settings: AnkiConnectSettings
    opencode_settings: OpenCodeSettings
    max_attempts: int

    @classmethod
    def from_environment(cls, require_anki: bool = True) -> "AppConfig":
        try:
            count = _positive_int("ANKI_LINGO_COUNT", "10")
            max_attempts = _positive_int("ANKI_LINGO_MAX_ATTEMPTS", "3")
            anki_timeout = _positive_float("ANKI_CONNECT_TIMEOUT_SECONDS", "10")
            opencode_timeout = _positive_float("OPENCODE_TIMEOUT_SECONDS", "120")
            deck_name = _required_or_dry_run("ANKI_DECK_NAME", require_anki)
            note_type = _required_or_dry_run("ANKI_NOTE_TYPE", require_anki)
            target = AnkiTarget(
                deck_name=deck_name,
                note_type=note_type,
                front_field=_value("ANKI_FIELD_FRONT", "Front"),
                back_field=_value("ANKI_FIELD_BACK", "Back"),
            )
            return cls(
                generation_request=GenerationRequest(
                    count=count,
                    cefr_level=_value("ANKI_LINGO_CEFR_LEVEL", "C1/C2"),
                    native_language=_value("ANKI_LINGO_NATIVE_LANGUAGE", "pt-BR"),
                ),
                anki_target=target,
                anki_settings=AnkiConnectSettings(
                    url=_value("ANKI_CONNECT_URL", "http://127.0.0.1:8765"),
                    timeout_seconds=anki_timeout,
                ),
                opencode_settings=OpenCodeSettings(
                    executable=_value("OPENCODE_BIN", "opencode"),
                    model=_optional_value("OPENCODE_MODEL"),
                    timeout_seconds=opencode_timeout,
                    working_directory=_optional_value("OPENCODE_WORKING_DIRECTORY"),
                ),
                max_attempts=max_attempts,
            )
        except (TypeError, ValueError) as error:
            raise ConfigurationError(str(error)) from error


def _value(name: str, default: str) -> str:
    value = environ.get(name, default).strip()
    if not value:
        raise ConfigurationError(f"{name} must not be empty")
    return value


def _optional_value(name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _required_or_dry_run(name: str, required: bool) -> str:
    if not required:
        return environ.get(name, "Dry Run").strip() or "Dry Run"
    value = environ.get(name)
    if value is None or not value.strip():
        raise ConfigurationError(f"{name} is required")
    return value.strip()


def _positive_int(name: str, default: str) -> int:
    try:
        value = int(_value(name, default))
    except ValueError as error:
        raise ConfigurationError(f"{name} must be an integer") from error
    if value < 1:
        raise ConfigurationError(f"{name} must be positive")
    return value


def _positive_float(name: str, default: str) -> float:
    try:
        value = float(_value(name, default))
    except ValueError as error:
        raise ConfigurationError(f"{name} must be a number") from error
    if value <= 0 or not isfinite(value):
        raise ConfigurationError(f"{name} must be positive")
    return value
