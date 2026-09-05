from collections.abc import Sequence

from anki_lingo.application.generate_daily_cards import (
    DailyFlashcardGenerator,
    DailyGenerationError,
)
from anki_lingo.application.ports import (
    AnkiGateway,
    AnkiInsertionResult,
    AnkiTarget,
    GenerationRequest,
    LLMProvider,
    QualityReport,
)
from anki_lingo.domain.flashcard import Flashcard
from anki_lingo.domain.validation import FlashcardValidator


def card(front: str) -> Flashcard:
    return Flashcard(front, f"To {front}.", f"I {front}.")


class FakeProvider:
    def __init__(self, batches: Sequence[Sequence[Flashcard]]) -> None:
        self.batches = [tuple(batch) for batch in batches]
        self.requests: list[GenerationRequest] = []

    def generate(self, request: GenerationRequest) -> tuple[Flashcard, ...]:
        self.requests.append(request)
        return self.batches.pop(0)

    def review(
        self, request: GenerationRequest, cards: Sequence[Flashcard]
    ) -> QualityReport:
        return QualityReport(accepted=True)


class FakeAnki:
    def __init__(self, fronts: Sequence[str] = ()) -> None:
        self.fronts = tuple(fronts)
        self.preflight_calls = 0
        self.inserted: tuple[Flashcard, ...] = ()

    def preflight(self, target: AnkiTarget) -> None:
        self.preflight_calls += 1

    def existing_fronts(self, target: AnkiTarget) -> tuple[str, ...]:
        return self.fronts

    def add_batch(
        self, target: AnkiTarget, cards: Sequence[Flashcard]
    ) -> AnkiInsertionResult:
        self.inserted = tuple(cards)
        return AnkiInsertionResult(
            len(self.inserted), tuple(range(100, 100 + len(self.inserted)))
        )


def generator(provider: LLMProvider, anki: AnkiGateway) -> DailyFlashcardGenerator:
    return DailyFlashcardGenerator(
        provider=provider,
        anki=anki,
        validator=FlashcardValidator(),
        target=AnkiTarget("English", "Basic"),
        max_attempts=3,
    )


def test_generator_retries_for_cards_filtered_by_anki() -> None:
    provider = FakeProvider(
        (
            (card("figure out"), card("carry out")),
            (card("boil down"),),
        )
    )
    anki = FakeAnki(("I need to <b>figure out</b> why.",))

    result = generator(provider, anki).run(GenerationRequest(2))

    assert [item.front for item in result.cards] == ["carry out", "boil down"]
    assert provider.requests == [GenerationRequest(2), GenerationRequest(1)]
    assert anki.preflight_calls == 1
    assert [item.front for item in anki.inserted] == ["carry out", "boil down"]
    assert result.inserted is True


def test_generator_dry_run_never_calls_anki() -> None:
    provider = FakeProvider(((card("figure out"),),))
    anki = FakeAnki(("figure out",))

    result = generator(provider, anki).run(GenerationRequest(1), dry_run=True)

    assert result.inserted is False
    assert anki.preflight_calls == 0
    assert anki.inserted == ()


def test_generator_fails_without_insertion_after_bounded_invalid_batches() -> None:
    duplicate_batch = (card("figure out"), card("FIGURE OUT"))
    provider = FakeProvider((duplicate_batch, duplicate_batch, duplicate_batch))
    anki = FakeAnki()

    try:
        generator(provider, anki).run(GenerationRequest(2))
    except DailyGenerationError as error:
        assert "after 3 attempts" in str(error)
    else:
        raise AssertionError("expected bounded generation failure")
    assert anki.inserted == ()
