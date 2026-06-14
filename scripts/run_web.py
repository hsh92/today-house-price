#!/usr/bin/env python3
"""Flask 웹 서버 실행."""

from __future__ import annotations

import os

from today_house_price.presentation.web.app import create_app

app = create_app()


def main() -> None:
    host = os.environ.get("WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("WEB_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
