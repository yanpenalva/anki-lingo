# Domain model

## Flashcard

The initial domain object has exactly three required fields. The two back-side
values remain separate until the Anki adapter renders them into one `Back`
field:

| Field | Meaning | Required invariant |
| --- | --- | --- |
| `front` | English term, or English sentence with the target highlighted | non-empty; bare term or one `<b>`/`<strong>` highlight |
| `meaning` | target term followed by its English (US) explanation | non-empty; `term: definition` format |
| `example` | natural English (US) sentence that gives the target sense context | non-empty |

CEFR, category, topic, tags, provider, and timestamps are not part of the
initial domain card unless a concrete use case proves they are required.
Generation and run metadata must not be smuggled into the four learning fields.

## Value and equality rules

- Field values are strings after boundary normalization.
- Empty or whitespace-only values are invalid.
- Newlines, control characters, and oversized values are policy decisions for
  the implementation spec; the limits must be explicit before coding.
- Front identity is computed from the highlighted target term when present;
  otherwise the bare front is used. The identity is Unicode-normalized,
  whitespace-collapsed, and case-folded.
- The original display text remains unchanged after identity normalization.

The identity function is:

```text
NFKC → trim → collapse Unicode whitespace → casefold
```

This is the approved implementation rule.

## Batch

A batch is an ordered collection of cards plus a requested count. A valid batch
has:

- exactly the requested number of cards;
- no duplicate normalized learning terms;
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

Semantic validation must cover English (US) naturalness, CEFR suitability,
meaning/example equivalence, false-cognate risk, and contradictory meaning. The
plan therefore includes a structured, bounded quality-review boundary. A model
review is evidence for acceptance, not permission to bypass deterministic
rules.

## Failure semantics

Invalid data produces typed failure information at the application boundary.
The CLI maps failures to non-zero exit codes. No invalid card is converted to
an empty value, silently dropped while claiming success, or sent to Anki.

Retries operate on the generation/quality stage only, have a configured upper
bound, and request the deficit when a candidate batch is unusable. If the
application cannot form the exact requested final batch within the bound, the
run fails without insertion.
