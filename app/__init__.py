from flask import Flask
import logging
from app.database import init_db

def create_app(testing=False):
    app = Flask(__name__)
    app.config["TESTING"] = testing

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Monitoring API startup")

    from app.routes import main
    app.register_blueprint(main)

    if not testing:
        init_db()

    return app