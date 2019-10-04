import logging


def initialize(app):
    level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO
    app.logger.setLevel(level)

