import re
from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from os import environ
from pathlib import Path
from types import MappingProxyType

from anki_lingo.application.ports import AnkiTarget, GenerationRequest
from anki_lingo.infrastructure.anki.ankiconnect_gateway import AnkiConnectSettings
from anki_lingo.infrastructure.llm.opencode_provider import OpenCodeSettings


class ConfigurationError(ValueError):
    """Raised when runtime configuration is incomplete or invalid."""


_ENV_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class AppConfig:
    generation_request: GenerationRequest
    anki_target: AnkiTarget
    anki_settings: AnkiConnectSettings
    provider_name: str
    provider_environment: Mapping[str, str]
    opencode_settings: OpenCodeSettings
    max_attempts: int

    @classmethod
    def from_environment(cls, require_anki: bool = True) -> "AppConfig":
        environment = _environment_with_dotenv()
        try:
            count = _positive_int("ANKI_LINGO_COUNT", "10", environment)
            max_attempts = _positive_int("ANKI_LINGO_MAX_ATTEMPTS", "3", environment)
            anki_timeout = _positive_float(
                "ANKI_CONNECT_TIMEOUT_SECONDS", "10", environment
            )
            provider_name = _value(
                "ANKI_LINGO_PROVIDER", "opencode", environment
            ).casefold()
            opencode_timeout = (
                _positive_float("OPENCODE_TIMEOUT_SECONDS", "120", environment)
                if provider_name == "opencode"
                else 120.0
            )
            deck_name = _required_or_dry_run(
                "ANKI_DECK_NAME", require_anki, environment
            )
            note_type = _required_or_dry_run(
                "ANKI_NOTE_TYPE", require_anki, environment
            )
            target = AnkiTarget(
                deck_name=deck_name,
                note_type=note_type,
                front_field=_value("ANKI_FIELD_FRONT", "Front", environment),
                back_field=_value("ANKI_FIELD_BACK", "Back", environment),
            )
            return cls(
                generation_request=GenerationRequest(
                    count=count,
                    cefr_level=_value("ANKI_LINGO_CEFR_LEVEL", "C1/C2", environment),
                    native_language=_value(
                        "ANKI_LINGO_NATIVE_LANGUAGE", "pt-BR", environment
                    ),
                ),
                anki_target=target,
                anki_settings=AnkiConnectSettings(
                    url=_value(
                        "ANKI_CONNECT_URL", "http://127.0.0.1:8765", environment
                    ),
                    timeout_seconds=anki_timeout,
                ),
                provider_name=provider_name,
                provider_environment=MappingProxyType(environment),
                opencode_settings=(
                    _opencode_settings(environment, opencode_timeout)
                    if provider_name == "opencode"
                    else OpenCodeSettings()
                ),
                max_attempts=max_attempts,
            )
        except (TypeError, ValueError) as error:
            raise ConfigurationError(str(error)) from error


def _environment_with_dotenv() -> dict[str, str]:
    environment = dict(environ)
    dotenv_path = Path.cwd() / ".env"
    if not dotenv_path.is_file():
        return environment
    try:
        lines = dotenv_path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ConfigurationError(f"could not read {dotenv_path}") from error
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[7:].lstrip()
        name, separator, raw_value = stripped.partition("=")
        name = name.strip()
        if not separator or not _ENV_KEY_RE.fullmatch(name):
            raise ConfigurationError(
                f"invalid .env entry at {dotenv_path}:{line_number}"
            )
        if name in environment:
            continue
        environment[name] = _parse_dotenv_value(raw_value.strip())
    return environment


def _parse_dotenv_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if " #" in value:
        return value.split(" #", maxsplit=1)[0].rstrip()
    return value


def _opencode_settings(
    environment: Mapping[str, str], timeout_seconds: float
) -> OpenCodeSettings:
    return OpenCodeSettings(
        executable=_value("OPENCODE_BIN", "opencode", environment),
        model=_optional_value("OPENCODE_MODEL", environment),
        timeout_seconds=timeout_seconds,
        working_directory=_optional_value("OPENCODE_WORKING_DIRECTORY", environment),
    )


def _value(name: str, default: str, environment: Mapping[str, str]) -> str:
    value = environment.get(name, default).strip()
    if not value:
        raise ConfigurationError(f"{name} must not be empty")
    return value


def _optional_value(name: str, environment: Mapping[str, str]) -> str | None:
    value = environment.get(name)
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _required_or_dry_run(
    name: str, required: bool, environment: Mapping[str, str]
) -> str:
    if not required:
        return environment.get(name, "Dry Run").strip() or "Dry Run"
    value = environment.get(name)
    if value is None or not value.strip():
        raise ConfigurationError(f"{name} is required")
    return value.strip()


def _positive_int(name: str, default: str, environment: Mapping[str, str]) -> int:
    try:
        value = int(_value(name, default, environment))
    except ValueError as error:
        raise ConfigurationError(f"{name} must be an integer") from error
    if value < 1:
        raise ConfigurationError(f"{name} must be positive")
    return value


def _positive_float(name: str, default: str, environment: Mapping[str, str]) -> float:
    try:
        value = float(_value(name, default, environment))
    except ValueError as error:
        raise ConfigurationError(f"{name} must be a number") from error
    if value <= 0 or not isfinite(value):
        raise ConfigurationError(f"{name} must be positive")
    return value
