from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from anki_lingo.domain.flashcard import Flashcard


class ApplicationError(RuntimeError):
    """Base error exposed by application boundaries."""


class ProviderError(ApplicationError):
    """Raised when LLM generation or review cannot complete."""


class AnkiGatewayError(ApplicationError):
    """Raised when Anki preflight, lookup, or insertion fails."""


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    count: int
    cefr_level: str = "C1/C2"
    native_language: str = "pt-BR"

    def __post_init__(self) -> None:
        if self.count < 1:
            raise ValueError("count must be positive")
        if not self.cefr_level.strip():
            raise ValueError("CEFR level must not be empty")
        if not self.native_language.strip():
            raise ValueError("native language must not be empty")


@dataclass(frozen=True, slots=True)
class QualityReport:
    accepted: bool
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.accepted and not self.reasons:
            raise ValueError("rejected quality report needs at least one reason")


@dataclass(frozen=True, slots=True)
class AnkiTarget:
    deck_name: str
    note_type: str
    front_field: str = "Front"
    back_field: str = "Back"

    def __post_init__(self) -> None:
        if not self.deck_name.strip():
            raise ValueError("deck name must not be empty")
        if not self.note_type.strip():
            raise ValueError("note type must not be empty")
        if not self.front_field.strip() or not self.back_field.strip():
            raise ValueError("Anki field names must not be empty")
        if self.front_field == self.back_field:
            raise ValueError("front and back Anki fields must be different")


@dataclass(frozen=True, slots=True)
class AnkiInsertionResult:
    added_count: int
    note_ids: tuple[int, ...]


class LLMProvider(Protocol):
    def generate(self, request: GenerationRequest) -> tuple[Flashcard, ...]: ...

    def review(
        self, request: GenerationRequest, cards: Sequence[Flashcard]
    ) -> QualityReport: ...


class AnkiGateway(Protocol):
    def preflight(self, target: AnkiTarget) -> None: ...

    def existing_fronts(self, target: AnkiTarget) -> tuple[str, ...]: ...

    def add_batch(
        self, target: AnkiTarget, cards: Sequence[Flashcard]
    ) -> AnkiInsertionResult: ...
