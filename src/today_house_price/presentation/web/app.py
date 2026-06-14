"""Flask application factory."""

from __future__ import annotations

from flask import Flask

from today_house_price.presentation.web.config import WebConfig
from today_house_price.presentation.web.routes import web_bp


def create_app(config: WebConfig | None = None) -> Flask:
    web_config = config or WebConfig.from_env()
    web_dir = __import__("pathlib").Path(__file__).resolve().parent

    app = Flask(
        __name__,
        template_folder=str(web_dir / "templates"),
        static_folder=str(web_dir / "static"),
    )
    app.config["SECRET_KEY"] = web_config.secret_key
    app.config["WEB_CONFIG"] = web_config
    app.config["MAX_CONTENT_LENGTH"] = web_config.max_upload_mb * 1024 * 1024

    web_config.upload_folder.mkdir(parents=True, exist_ok=True)

    app.register_blueprint(web_bp)
    return app
