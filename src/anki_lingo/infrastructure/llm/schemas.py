from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr


class FlashcardPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    front: StrictStr = Field(min_length=1)
    translation: StrictStr = Field(min_length=1)
    meaning: StrictStr = Field(min_length=1)
    example: StrictStr = Field(min_length=1)


class GenerationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    cards: list[FlashcardPayload] = Field(min_length=1)


class QualityPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    accepted: StrictBool
    reasons: list[StrictStr] = Field(default_factory=list)
