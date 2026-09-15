"""Android entry point for the bundled Worm Cinema server."""

import os
import threading


def start(files_dir):
    """Start Flask on the device loopback interface and return when it is ready."""
    os.environ["WORM_CINEMA_DATABASE"] = os.path.join(files_dir, "worm_cinema.db")
    from app import app

    thread = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1", port=8765, threaded=True, use_reloader=False
        ),
        daemon=True,
    )
    thread.start()
