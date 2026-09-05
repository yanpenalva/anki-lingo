import re
from dataclasses import dataclass
from unicodedata import category, normalize

MAX_FIELD_LENGTH = 1000
_HIGHLIGHT_RE = re.compile(
    r"<(?P<tag>b|strong)>(?P<term>[^<>]+)</(?P=tag)>", re.IGNORECASE
)
_ALLOWED_TAG_RE = re.compile(r"</?(?:b|strong)>", re.IGNORECASE)


class FlashcardValidationError(ValueError):
    """Raised when flashcard field invariants fail."""


def normalize_front(value: str) -> str:
    normalized = normalize("NFKC", value)
    highlighted = _HIGHLIGHT_RE.findall(normalized)
    if highlighted:
        normalized = highlighted[0][1]
    else:
        normalized = _ALLOWED_TAG_RE.sub("", normalized)
    return " ".join(normalized.split()).casefold()


def _clean_field(field_name: str, value: object) -> str:
    if not isinstance(value, str):
        raise FlashcardValidationError(f"{field_name} must be a string")

    cleaned = value.strip()
    if not cleaned:
        raise FlashcardValidationError(f"{field_name} must not be empty")
    if len(cleaned) > MAX_FIELD_LENGTH:
        raise FlashcardValidationError(
            f"{field_name} exceeds {MAX_FIELD_LENGTH} characters"
        )
    if any(category(character) == "Cc" for character in cleaned):
        raise FlashcardValidationError(f"{field_name} contains control characters")
    return cleaned


def _clean_front(value: object) -> str:
    cleaned = _clean_field("front", value)
    highlighted = _HIGHLIGHT_RE.findall(cleaned)
    if len(highlighted) > 1:
        raise FlashcardValidationError("front must contain at most one highlight")
    allowed_tags = _ALLOWED_TAG_RE.findall(cleaned)
    if allowed_tags and (len(allowed_tags) != 2 or not highlighted):
        raise FlashcardValidationError("front highlight markup is invalid")
    without_allowed_tags = _ALLOWED_TAG_RE.sub("", cleaned)
    if "<" in without_allowed_tags or ">" in without_allowed_tags:
        raise FlashcardValidationError(
            "front may only use <b> or <strong> for highlighting"
        )
    if highlighted:
        canonical = re.sub(r"<(?:b|strong)>", "<b>", cleaned, flags=re.IGNORECASE)
        return re.sub(r"</(?:b|strong)>", "</b>", canonical, flags=re.IGNORECASE)
    return cleaned


@dataclass(frozen=True, slots=True)
class Flashcard:
    front: str
    translation: str
    meaning: str
    example: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "front", _clean_front(self.front))
        for field_name in ("translation", "meaning", "example"):
            value = _clean_field(field_name, getattr(self, field_name))
            object.__setattr__(self, field_name, value)

    @property
    def front_key(self) -> str:
        return normalize_front(self.front)

    def as_mapping(self) -> dict[str, str]:
        return {
            "front": self.front,
            "translation": self.translation,
            "meaning": self.meaning,
            "example": self.example,
        }
