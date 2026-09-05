import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from anki_lingo.application.ports import AnkiTarget
from anki_lingo.domain.flashcard import Flashcard
from anki_lingo.infrastructure.anki.ankiconnect_gateway import (
    AnkiConnectGateway,
    AnkiConnectSettings,
)


class Handler(BaseHTTPRequestHandler):
    responses: dict[str, object] = {}
    requests: list[dict[str, Any]] = []

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"] or 0)
        request = json.loads(self.rfile.read(length))
        self.requests.append(request)
        action = request["action"]
        response = {"result": self.responses[action], "error": None}
        body = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


@pytest.fixture
def server() -> Iterator[tuple[str, list[dict[str, Any]]]]:
    Handler.responses = {
        "version": 6,
        "deckNames": ["English"],
        "modelNames": ["Basic"],
        "modelFieldNames": ["Front", "Back"],
        "findNotes": [7],
        "notesInfo": [
            {"fields": {"Front": {"value": "figure out"}}},
        ],
        "addNotes": [101, 102],
    }
    Handler.requests = []
    http_server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{http_server.server_port}", Handler.requests
    finally:
        http_server.shutdown()
        thread.join()


def test_gateway_preflights_reads_and_inserts(
    server: tuple[str, list[dict[str, Any]]],
) -> None:
    url, requests = server
    gateway = AnkiConnectGateway(AnkiConnectSettings(url=url))
    target = AnkiTarget("English", "Basic")
    card = Flashcard(
        "<b>carry out</b>",
        "executar",
        "To perform or complete something.",
        "Carry out the plan.",
    )

    gateway.preflight(target)
    assert gateway.existing_fronts(target) == ("figure out",)
    result = gateway.add_batch(target, (card, card))

    assert result.note_ids == (101, 102)
    assert [request["action"] for request in requests] == [
        "version",
        "deckNames",
        "modelNames",
        "modelFieldNames",
        "findNotes",
        "notesInfo",
        "addNotes",
    ]
    fields = requests[-1]["params"]["notes"][0]["fields"]
    assert fields["Front"] == "<b>carry out</b>"
    assert fields["Back"] == (
        "Tradução: executar<br><br>"
        "Meaning: To perform or complete something.<br><br>"
        "Example: Carry out the plan."
    )
