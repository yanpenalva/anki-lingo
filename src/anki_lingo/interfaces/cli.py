import argparse
import json
import sys
from argparse import Namespace
from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import cast

from anki_lingo.application.generate_daily_cards import (
    DailyFlashcardGenerator,
    DailyGenerationResult,
)
from anki_lingo.application.ports import ApplicationError
from anki_lingo.domain.validation import FlashcardValidator
from anki_lingo.infrastructure.anki.ankiconnect_gateway import AnkiConnectGateway
from anki_lingo.infrastructure.config import AppConfig, ConfigurationError
from anki_lingo.infrastructure.llm.factory import create_provider


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    if arguments.command is None:
        parser.print_help()
        return 0
    try:
        handler = cast(Callable[[Namespace], int], arguments.handler)
        return handler(arguments)
    except ConfigurationError as error:
        _print_error(str(error))
        return 2
    except ApplicationError as error:
        _print_error(str(error))
        return 1
    except ValueError as error:
        _print_error(str(error))
        return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anki-lingo",
        description="Generate C1/C2 English flashcards and synchronize Anki.",
    )
    commands = parser.add_subparsers(dest="command")
    config_command = commands.add_parser("config-check")
    config_command.set_defaults(handler=_config_check)
    generate_command = commands.add_parser("generate")
    generate_command.add_argument("--count", type=_positive_count)
    generate_command.add_argument("--cefr-level")
    generate_command.add_argument("--native-language")
    generate_command.add_argument("--dry-run", action="store_true")
    generate_command.add_argument("--output", choices=("text", "json"), default="text")
    generate_command.set_defaults(handler=_generate)
    return parser


def _config_check(_: Namespace) -> int:
    config = AppConfig.from_environment()
    payload = {
        "count": config.generation_request.count,
        "cefr_level": config.generation_request.cefr_level,
        "native_language": config.generation_request.native_language,
        "anki_connect_url": config.anki_settings.url,
        "provider": config.provider_name,
        "anki_deck": config.anki_target.deck_name,
        "anki_note_type": config.anki_target.note_type,
        "max_attempts": config.max_attempts,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _generate(arguments: Namespace) -> int:
    config = AppConfig.from_environment(require_anki=not arguments.dry_run)
    request = replace(
        config.generation_request,
        count=arguments.count or config.generation_request.count,
        cefr_level=arguments.cefr_level or config.generation_request.cefr_level,
        native_language=(
            arguments.native_language or config.generation_request.native_language
        ),
    )
    generator = DailyFlashcardGenerator(
        provider=create_provider(config),
        anki=AnkiConnectGateway(config.anki_settings),
        validator=FlashcardValidator(),
        target=config.anki_target,
        max_attempts=config.max_attempts,
    )
    result = generator.run(request, dry_run=arguments.dry_run)
    _print_result(result, arguments.output)
    return 0


def _print_result(result: DailyGenerationResult, output: str) -> None:
    if output == "json":
        payload = {
            "cards": [card.as_mapping() for card in result.cards],
            "attempts": result.attempts,
            "inserted": result.inserted,
            "note_ids": list(result.note_ids),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    action = "prepared for Anki" if result.inserted else "prepared in dry-run"
    print(f"{len(result.cards)} cards {action}; attempts={result.attempts}")
    for index, card in enumerate(result.cards, start=1):
        print(f"{index}. {card.front} — {card.meaning}")


def _positive_count(value: str) -> int:
    count = int(value)
    if count < 1:
        raise argparse.ArgumentTypeError("count must be positive")
    return count


def _print_error(message: str) -> None:
    print(f"anki-lingo: {message}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
