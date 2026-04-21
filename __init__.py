from flask import Flask
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__)
    
    file_handler = RotatingFileHandler('api.log', maxBytes=1000000, backupCount=3)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Monitoring API startup')
    
    from app.routes import main
    app.register_blueprint(main)

    return app 