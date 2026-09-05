import pytest

from anki_lingo.domain.flashcard import (
    Flashcard,
    FlashcardValidationError,
    normalize_front,
)


def test_flashcard_strips_outer_whitespace_and_preserves_content() -> None:
    card = Flashcard(
        "  I need to <strong>figure out</strong> why.  ",
        " descobrir ",
        "To understand or solve something.",
        " Example. ",
    )

    assert card.front == "I need to <b>figure out</b> why."
    assert card.example == "Example."
    assert card.translation == "descobrir"
    assert card.meaning == "To understand or solve something."
    assert card.front_key == "figure out"


@pytest.mark.parametrize("field", ("front", "translation", "meaning", "example"))
def test_flashcard_rejects_empty_field(field: str) -> None:
    values = {
        "front": "front",
        "translation": "translation",
        "meaning": "meaning",
        "example": "example",
    }
    values[field] = "  "

    with pytest.raises(FlashcardValidationError, match=field):
        Flashcard(**values)


def test_flashcard_rejects_control_characters() -> None:
    with pytest.raises(FlashcardValidationError, match="control"):
        Flashcard("figure\nout", "descobrir", "To understand", "Example")


def test_flashcard_rejects_unsupported_front_markup() -> None:
    with pytest.raises(FlashcardValidationError, match="highlighting"):
        Flashcard("I <em>figure out</em> it", "descobrir", "To understand", "Example")


def test_flashcard_rejects_multiple_front_highlights() -> None:
    with pytest.raises(FlashcardValidationError, match="at most one"):
        Flashcard(
            "<b>figure out</b> and <b>carry out</b>",
            "descobrir",
            "To understand",
            "Example",
        )


def test_flashcard_rejects_mismatched_front_markup() -> None:
    with pytest.raises(FlashcardValidationError, match="markup"):
        Flashcard(
            "I <b>figure out</strong> it",
            "descobrir",
            "To understand",
            "Example",
        )


def test_normalize_front_is_case_and_unicode_whitespace_insensitive() -> None:
    assert normalize_front("  FIGURE\tOUT  ") == "figure out"
