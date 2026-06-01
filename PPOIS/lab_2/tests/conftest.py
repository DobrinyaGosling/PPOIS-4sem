import atexit
import os
import tempfile


os.environ.setdefault("MODE", "TEST")

if "TEST_SQLITE_PATH" not in os.environ:
    fd, path = tempfile.mkstemp(prefix="lab2_", suffix=".sqlite3")
    os.close(fd)
    os.environ["TEST_SQLITE_PATH"] = path

    def _cleanup() -> None:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    atexit.register(_cleanup)
