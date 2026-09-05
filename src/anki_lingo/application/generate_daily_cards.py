from collections.abc import Sequence
from dataclasses import dataclass, replace

from anki_lingo.application.ports import (
    AnkiGateway,
    AnkiInsertionResult,
    AnkiTarget,
    ApplicationError,
    GenerationRequest,
    LLMProvider,
    ProviderError,
)
from anki_lingo.domain.flashcard import Flashcard, normalize_front
from anki_lingo.domain.validation import CardBatchValidationError, FlashcardValidator


class DailyGenerationError(ApplicationError):
    """Raised when a complete daily batch cannot be prepared safely."""


@dataclass(frozen=True, slots=True)
class DailyGenerationResult:
    cards: tuple[Flashcard, ...]
    attempts: int
    inserted: bool
    note_ids: tuple[int, ...] = ()


class DailyFlashcardGenerator:
    def __init__(
        self,
        provider: LLMProvider,
        anki: AnkiGateway,
        validator: FlashcardValidator,
        target: AnkiTarget,
        max_attempts: int = 3,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max attempts must be positive")
        self._provider = provider
        self._anki = anki
        self._validator = validator
        self._target = target
        self._max_attempts = max_attempts

    def run(
        self, request: GenerationRequest, dry_run: bool = False
    ) -> DailyGenerationResult:
        existing_fronts = self._prepare_anki(dry_run)
        accepted: list[Flashcard] = []
        failures: list[str] = []
        attempts = 0

        for attempt in range(1, self._max_attempts + 1):
            attempts = attempt
            if len(accepted) == request.count:
                break
            remaining = request.count - len(accepted)
            self._collect_candidates(
                replace(request, count=remaining),
                existing_fronts,
                accepted,
                failures,
            )

        if len(accepted) != request.count:
            detail = "; ".join(failures[-3:]) or "provider returned insufficient cards"
            raise DailyGenerationError(
                f"could not prepare {request.count} cards after "
                f"{self._max_attempts} attempts: {detail}"
            )

        cards = tuple(accepted)
        if dry_run:
            return DailyGenerationResult(cards, attempts, False)

        insertion = self._insert(cards, request.count)
        return DailyGenerationResult(cards, attempts, True, insertion.note_ids)

    def _prepare_anki(self, dry_run: bool) -> frozenset[str]:
        if dry_run:
            return frozenset()
        self._anki.preflight(self._target)
        return frozenset(
            normalize_front(front) for front in self._anki.existing_fronts(self._target)
        )

    def _collect_candidates(
        self,
        request: GenerationRequest,
        existing_fronts: frozenset[str],
        accepted: list[Flashcard],
        failures: list[str],
    ) -> None:
        try:
            candidate_cards = self._provider.generate(request)
            batch = self._validator.validate(candidate_cards, request.count)
            report = self._provider.review(request, batch.cards)
            if not report.accepted:
                failures.extend(report.reasons)
                return
            known = existing_fronts | {card.front_key for card in accepted}
            accepted.extend(card for card in batch.cards if card.front_key not in known)
        except (CardBatchValidationError, ProviderError) as error:
            failures.append(str(error))

    def _insert(
        self, cards: Sequence[Flashcard], requested_count: int
    ) -> AnkiInsertionResult:
        result = self._anki.add_batch(self._target, cards)
        if (
            result.added_count != requested_count
            or len(result.note_ids) != requested_count
        ):
            raise DailyGenerationError("Anki insertion returned an incomplete result")
        return result
