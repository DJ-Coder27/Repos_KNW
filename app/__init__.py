from flask import Flask
import logging

def create_app():
    app = Flask(__name__)

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Monitoring API startup')

    from app.routes import main
    app.register_blueprint(main)

    return app