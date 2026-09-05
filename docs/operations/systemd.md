# systemd operations

## Target

The eventual schedule uses a systemd user service plus user timer on Pop!_OS.
The service runs as the same user that owns the Anki Desktop session, so the
local AnkiConnect endpoint remains reachable without introducing a privileged
daemon.

The deployment templates are not activated by the bootstrap delivery. The
service and timer are created in the final implementation wave after the CLI
contract is stable.

## Planned behavior

- `Type=oneshot` service invokes one CLI run.
- A timer triggers it once per configured daily schedule.
- An environment file outside the repository supplies credentials, provider
  selection, Anki target settings, and local paths.
- A lock prevents overlapping runs.
- OpenCode and Anki failures return non-zero status and are visible in
  journald.
- The timer does not create an unbounded retry loop.
- Manual execution uses the same service command and configuration as the
  timer.

## Configuration boundary

The following values are expected to be user configuration, not committed
defaults containing personal or secret data:

- OpenCode executable/model options;
- AnkiConnect URL;
- Anki deck and note type;
- Anki field mapping;
- daily card count, CEFR level, and native language;
- retry/timeout limits;
- timer schedule and timezone.

AnkiConnect's loopback URL is a proposed default; all other target details are
`NOT FOUND` until confirmed.

## Operational checks

The final runbook will document:

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
