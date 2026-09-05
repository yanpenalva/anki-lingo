from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from anki_lingo.domain.flashcard import Flashcard, normalize_front


class BatchValidationError(ValueError):
    """Raised when a card batch invariant fails."""


@dataclass(frozen=True, slots=True)
class FlashcardBatch:
    cards: tuple[Flashcard, ...]
    requested_count: int

    def __post_init__(self) -> None:
        if self.requested_count < 1:
            raise BatchValidationError("requested count must be positive")
        if len(self.cards) != self.requested_count:
            raise BatchValidationError(
                f"expected {self.requested_count} cards, received {len(self.cards)}"
            )
        keys = [card.front_key for card in self.cards]
        if len(keys) != len(set(keys)):
            raise BatchValidationError("batch contains duplicate fronts")

    @classmethod
    def from_sequence(
        cls, cards: Sequence[Flashcard], requested_count: int
    ) -> "FlashcardBatch":
        return cls(tuple(cards), requested_count)

    def excluding_fronts(self, existing_fronts: Iterable[str]) -> tuple[Flashcard, ...]:
        known = {normalize_front(front) for front in existing_fronts}
        return tuple(card for card in self.cards if card.front_key not in known)
