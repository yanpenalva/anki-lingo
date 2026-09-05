import json
from collections.abc import Sequence

from anki_lingo.application.ports import GenerationRequest
from anki_lingo.domain.flashcard import Flashcard


def generation_prompt(request: GenerationRequest) -> str:
    return (
        "Generate exactly "
        f"{request.count} advanced English flashcards for a Brazilian Portuguese "
        f"speaker at CEFR {request.cefr_level}. Return only one JSON object with "
        "key 'cards'. Each card must contain exactly 'front', "
        "'meaning', and 'example'. The front must be either the target term alone "
        "or a natural English sentence with the target term highlighted exactly "
        "once using <b>...</b>. Put the target term followed by ': ' and its "
        "English (US) definition in 'meaning', for example 'Ephemeral: Lasting "
        "for a very short time.'. Do not return only the definition. Put an "
        "English (US) sentence that makes the sense clear in 'example'. All "
        "card fields must be in English (US); do not include "
        "Portuguese translations. Use precise meanings and examples appropriate "
        "for advanced learners. "
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
        "English, a missing or incorrect <b>...</b> highlight, non-English content, "
        "wrong CEFR difficulty, or a meaning that does not start with the target "
        "term followed by ': ' and its English definition. Reject if the meaning "
        "or example does not match the target sense. Reject false cognate risk "
        "or contradiction. "
        "Accept only when whole batch is suitable.\n\n"
        f"Cards:\n{serialized}"
    )
