import itertools
import sys
import threading
import time
from typing import TextIO

_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
_INTERVAL_SECONDS = 0.1


class Spinner:
    """Terminal loading indicator written to a text stream.

    The animation runs on a daemon thread and is disabled automatically when
    the stream is not a terminal, so piped or captured output stays clean.
    """

    def __init__(self, message: str, stream: TextIO | None = None) -> None:
        self._message = message
        self._stream: TextIO = stream if stream is not None else sys.stderr
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "Spinner":
        self.start()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.stop()

    def start(self) -> None:
        if self._thread is not None or not self._stream.isatty():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def update(self, message: str) -> None:
        self._message = message

    def stop(self) -> None:
        self._stop.set()
        if self._thread is None:
            return
        self._thread.join()
        self._thread = None
        self._stream.write("\r\033[K")
        self._stream.flush()

    def _spin(self) -> None:
        for frame in itertools.cycle(_FRAMES):
            if self._stop.is_set():
                break
            self._stream.write(f"\r{frame} {self._message}")
            self._stream.flush()
            time.sleep(_INTERVAL_SECONDS)
