import pytest

from anki_lingo.domain.batch import BatchValidationError, FlashcardBatch
from anki_lingo.domain.flashcard import Flashcard


def card(front: str) -> Flashcard:
    return Flashcard(front, "sentido", f"I can {front}.", f"Eu posso {front}.")


def test_batch_requires_exact_requested_count() -> None:
    with pytest.raises(BatchValidationError, match="expected 2"):
        FlashcardBatch.from_sequence((card("figure out"),), 2)


def test_batch_rejects_duplicate_normalized_fronts() -> None:
    with pytest.raises(BatchValidationError, match="duplicate"):
        FlashcardBatch.from_sequence((card("figure out"), card(" FIGURE OUT ")), 2)


def test_batch_excludes_existing_fronts() -> None:
    batch = FlashcardBatch.from_sequence((card("figure out"), card("carry out")), 2)

    result = batch.excluding_fronts(("FIGURE OUT",))

    assert [item.front for item in result] == ["carry out"]
