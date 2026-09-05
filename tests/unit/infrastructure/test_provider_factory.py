from collections.abc import Sequence

import pytest

from anki_lingo.application.ports import (
    GenerationRequest,
    QualityReport,
)
from anki_lingo.domain.flashcard import Flashcard
from anki_lingo.infrastructure.config import AppConfig, ConfigurationError
from anki_lingo.infrastructure.llm.factory import ProviderRegistry, create_provider
from anki_lingo.infrastructure.llm.opencode_provider import OpenCodeProvider


class FakeProvider:
    def generate(self, request: GenerationRequest) -> tuple[Flashcard, ...]:
        return ()

    def review(
        self, request: GenerationRequest, cards: Sequence[Flashcard]
    ) -> QualityReport:
        return QualityReport(accepted=True)


def test_registry_builds_a_registered_provider() -> None:
    provider = FakeProvider()
    registry = ProviderRegistry()
    registry.register("fake", lambda config: provider)

    config = AppConfig.from_environment(require_anki=False)

    assert registry.create("FAKE", config) is provider


def test_default_provider_is_opencode(monkeypatch: object) -> None:
    monkeypatch.setenv("ANKI_LINGO_PROVIDER", "opencode")
    config = AppConfig.from_environment(require_anki=False)

    assert isinstance(create_provider(config), OpenCodeProvider)


def test_registry_rejects_unknown_provider() -> None:
    registry = ProviderRegistry()
    registry.register("fake", lambda config: FakeProvider())
    config = AppConfig.from_environment(require_anki=False)

    with pytest.raises(ConfigurationError, match="unknown provider"):
        registry.create("missing", config)


def test_custom_provider_does_not_require_opencode_settings(
    monkeypatch: object,
) -> None:
    monkeypatch.setenv("ANKI_LINGO_PROVIDER", "custom")
    monkeypatch.setenv("OPENCODE_BIN", "")
    monkeypatch.setenv("OPENCODE_TIMEOUT_SECONDS", "invalid")

    config = AppConfig.from_environment(require_anki=False)

    assert config.provider_name == "custom"
