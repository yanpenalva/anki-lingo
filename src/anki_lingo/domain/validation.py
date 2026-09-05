from collections.abc import Sequence

from anki_lingo.domain.batch import BatchValidationError, FlashcardBatch
from anki_lingo.domain.flashcard import Flashcard


class CardBatchValidationError(ValueError):
    """Raised when candidate cards fail deterministic validation."""


class FlashcardValidator:
    def validate(
        self, cards: Sequence[Flashcard], requested_count: int
    ) -> FlashcardBatch:
        try:
            return FlashcardBatch.from_sequence(cards, requested_count)
        except BatchValidationError as error:
            raise CardBatchValidationError(str(error)) from error
