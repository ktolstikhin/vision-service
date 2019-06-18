import logging


def init_logger(app):
    level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO
    app.logger.setLevel(level)

