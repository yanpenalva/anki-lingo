import io
import time

from anki_lingo.interfaces.loading import Spinner


class FakeStream(io.StringIO):
    def isatty(self) -> bool:
        return True


def test_spinner_animates_and_clears_line_on_stop() -> None:
    stream = FakeStream()
    spinner = Spinner("working", stream=stream)

    spinner.start()
    time.sleep(0.15)
    spinner.stop()

    output = stream.getvalue()
    assert "working" in output
    assert output.endswith("\r\033[K")


def test_spinner_is_silent_when_stream_is_not_a_terminal() -> None:
    stream = io.StringIO()
    spinner = Spinner("working", stream=stream)

    spinner.start()
    time.sleep(0.05)
    spinner.stop()

    assert stream.getvalue() == ""
