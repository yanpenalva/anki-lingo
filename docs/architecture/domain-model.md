# Domain model

## Flashcard

The initial domain object has exactly four required fields:

| Field | Meaning | Required invariant |
| --- | --- | --- |
| `front` | English word, phrase, or expression being learned | non-empty; identity source for deduplication |
| `back` | concise Brazilian Portuguese meaning(s) | non-empty |
| `example` | natural English usage example | non-empty |
| `translation` | Brazilian Portuguese translation of `example` | non-empty |

CEFR, category, topic, tags, provider, and timestamps are not part of the
initial domain card unless a concrete use case proves they are required.
Generation and run metadata must not be smuggled into the four learning fields.

## Value and equality rules

- Field values are strings after boundary normalization.
- Empty or whitespace-only values are invalid.
- Newlines, control characters, and oversized values are policy decisions for
  the implementation spec; the limits must be explicit before coding.
- Front identity is computed from Unicode-normalized, whitespace-collapsed,
  case-folded text. Punctuation handling must be decided and tested before
  deduplication is implemented.
- The original display text remains unchanged after identity normalization.

The proposed identity function is:

```text
NFKC → trim → collapse Unicode whitespace → casefold
```

This is a proposed default, not yet an approved user-facing rule.

## Batch

A batch is an ordered collection of cards plus a requested count. A valid batch
has:

- exactly the requested number of cards;
- no duplicate normalized fronts;
- every card passing deterministic field validation;
- no partial or placeholder card.

The batch is not considered synchronized merely because it passed local
validation. Anki availability, target configuration, existing-card lookup,
and insertion response are separate application concerns.

## Quality validation

Deterministic validation must cover:

- field presence and non-empty values;
- exact batch count;
- duplicate fronts inside the batch;
- malformed control/content boundaries selected by the approved policy;
- explicit rejection reasons that can be shown in logs without logging full
  card content.

Semantic validation must cover naturalness, CEFR suitability, Portuguese
naturalness, example/translation equivalence, false cognates, and contradictory
meaning. The plan therefore includes a structured, bounded quality-review
boundary. A model review is evidence for acceptance, not permission to bypass
deterministic rules.

## Failure semantics

Invalid data produces typed failure information at the application boundary.
The CLI maps failures to non-zero exit codes. No invalid card is converted to
an empty value, silently dropped while claiming success, or sent to Anki.

Retries operate on the generation/quality stage only, have a configured upper
bound, and request the deficit when a candidate batch is unusable. If the
application cannot form the exact requested final batch within the bound, the
run fails without insertion.
