# systemd operations

## Target

The eventual schedule uses a systemd user service plus user timer on Pop!_OS.
The service runs as the same user that owns the Anki Desktop session, so the
local AnkiConnect endpoint remains reachable without introducing a privileged
daemon.

Deployment templates are versioned but not activated automatically. Activation
requires confirmed configuration and explicit user approval.

## Planned behavior

- `Type=oneshot` service invokes one CLI run.
- A timer triggers it once per configured daily schedule.
- An environment file outside the repository supplies credentials, provider
  selection, Anki target settings, and local paths.
- A lock prevents overlapping runs.
- Provider and Anki failures return non-zero status and are visible in
  journald.
- The timer does not create an unbounded retry loop.
- Manual execution uses the same service command and configuration as the
  timer.

## Configuration boundary

The following values are expected to be user configuration, not committed
defaults containing personal or secret data:

- selected provider and provider-specific options;
- AnkiConnect URL;
- Anki deck and note type;
- Anki `Front` and `Back` field names;
- daily card count, CEFR level, and native language;
- retry/timeout limits;
- timer schedule and timezone.

For interactive CLI runs, the application loads `.env` from the project working
directory. Existing exported environment variables take precedence. The
systemd template uses an external `EnvironmentFile`, which is the preferred
place for scheduled-run configuration.

AnkiConnect's loopback URL is a proposed default; all other target details are
`NOT FOUND` until confirmed.

Implemented environment variable names:

```text
ANKI_DECK_NAME
ANKI_NOTE_TYPE
ANKI_CONNECT_URL
ANKI_FIELD_FRONT
ANKI_FIELD_BACK
ANKI_LINGO_PROVIDER
ANKI_LINGO_COUNT
ANKI_LINGO_CEFR_LEVEL
ANKI_LINGO_NATIVE_LANGUAGE
ANKI_LINGO_MAX_ATTEMPTS
OPENCODE_BIN
OPENCODE_MODEL
OPENCODE_TIMEOUT_SECONDS
OPENCODE_WORKING_DIRECTORY
```

`ANKI_DECK_NAME` and `ANKI_NOTE_TYPE` are mandatory for insertion. Dry-run can
omit them. Defaults are `10`, `C1/C2`, `pt-BR`, loopback AnkiConnect,
`Front`/`Back`, and three generation attempts. The `Back` field is rendered as
the target term, English (US) meaning, and English (US) example. The complete
manual setup and verification procedure is documented in the root README's
AnkiConnect integration runbook.

## Operational checks

The operational runbook covers the interactive CLI workflow. Before enabling
the timer, use these service checks:

```text
systemctl --user status anki-lingo.service
systemctl --user status anki-lingo.timer
journalctl --user -u anki-lingo.service
systemctl --user start anki-lingo.service
systemctl --user stop anki-lingo.timer
```

Before enabling the timer, validate the unit syntax, execute a manual dry run,
confirm Anki target configuration, and record the observed result. Enabling a
timer or writing to Anki requires explicit user approval for that rollout
step.
