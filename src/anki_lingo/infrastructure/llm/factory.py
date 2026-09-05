"""Provider registry and discovery for pluggable LLM adapters."""

from collections.abc import Callable
from importlib.metadata import EntryPoint, entry_points
from typing import cast

from anki_lingo.application.ports import LLMProvider
from anki_lingo.infrastructure.config import AppConfig, ConfigurationError
from anki_lingo.infrastructure.llm.opencode_provider import OpenCodeProvider

PROVIDER_ENTRY_POINT_GROUP = "anki_lingo.providers"
type ProviderBuilder = Callable[[AppConfig], LLMProvider]


class ProviderRegistry:
    """Maps provider names to infrastructure adapter builders."""

    def __init__(self) -> None:
        self._builders: dict[str, ProviderBuilder] = {}

    def register(self, name: str, builder: ProviderBuilder) -> None:
        normalized_name = name.strip().casefold()
        if not normalized_name:
            raise ConfigurationError("provider name must not be empty")
        if normalized_name in self._builders:
            raise ConfigurationError(f"duplicate provider registration: {name}")
        self._builders[normalized_name] = builder

    def create(self, name: str, config: AppConfig) -> LLMProvider:
        normalized_name = name.strip().casefold()
        try:
            builder = self._builders[normalized_name]
        except KeyError as error:
            available = ", ".join(sorted(self._builders)) or "none"
            raise ConfigurationError(
                f"unknown provider '{name}'; available providers: {available}"
            ) from error
        return builder(config)


def create_provider(config: AppConfig) -> LLMProvider:
    registry = _default_registry()
    return registry.create(config.provider_name, config)


def _default_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register("opencode", _build_opencode)
    for entry_point in entry_points(group=PROVIDER_ENTRY_POINT_GROUP):
        registry.register(entry_point.name, _lazy_entry_point(entry_point))
    return registry


def _lazy_entry_point(entry_point: EntryPoint) -> ProviderBuilder:
    def build(config: AppConfig) -> LLMProvider:
        try:
            loaded = entry_point.load()
        except (ImportError, AttributeError, TypeError) as error:
            raise ConfigurationError(
                f"could not load provider '{entry_point.name}'"
            ) from error
        if not callable(loaded):
            raise ConfigurationError(
                f"provider entry point '{entry_point.name}' is not callable"
            )
        builder = cast(ProviderBuilder, loaded)
        return builder(config)

    return build


def _build_opencode(config: AppConfig) -> LLMProvider:
    return OpenCodeProvider(config.opencode_settings)
