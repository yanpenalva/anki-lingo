import json
from collections.abc import Sequence

from anki_lingo.application.ports import GenerationRequest
from anki_lingo.domain.flashcard import Flashcard


def generation_prompt(request: GenerationRequest) -> str:
    return (
        "Generate exactly "
        f"{request.count} advanced English flashcards for a Brazilian Portuguese "
        f"speaker at CEFR {request.cefr_level}. Return only one JSON object with "
        "key 'cards'. Each card must contain exactly 'front', 'translation', "
        "'meaning', and 'example'. The front must be either the target term alone "
        "or a natural English sentence with the target term highlighted exactly "
        "once using <b>...</b>. Put the Brazilian Portuguese translation of the "
        "term in 'translation', an English definition of that sense in 'meaning', "
        "and an English sentence that makes the sense clear in 'example'. Use "
        "natural English, natural Brazilian Portuguese, precise meanings, and "
        "examples appropriate for advanced learners. "
        "Do not include duplicate fronts, obvious false cognates, or invented "
        "facts."
    )


def review_prompt(request: GenerationRequest, cards: Sequence[Flashcard]) -> str:
    serialized = json.dumps(
        [card.as_mapping() for card in cards], ensure_ascii=False, indent=2
    )
    return (
        "Review following English flashcard batch for a Brazilian Portuguese "
        f"speaker at CEFR {request.cefr_level}. Return only one JSON object with "
        "boolean 'accepted' and array 'reasons'. Reject if any card has unnatural "
        "English, a missing or incorrect <b>...</b> highlight, unnatural Brazilian "
        "Portuguese, wrong CEFR difficulty, an English meaning or example that "
        "does not match the translated sense, false cognate risk, or contradiction. "
        "Accept only when whole batch is suitable.\n\n"
        f"Cards:\n{serialized}"
    )
