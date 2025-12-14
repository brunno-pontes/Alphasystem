import logging
from logging.handlers import RotatingFileHandler
import os
from flask import request
from flask_login import current_user

def setup_logger(app):
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/alphasystem.log',
                                         maxBytes=10240000, 
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Alphasystem startup')

def log_user_activity(action, details=""):
    """Registra atividades dos usuários"""
    user_id = current_user.id if current_user.is_authenticated else 'Anonymous'
    ip_address = request.remote_addr
    endpoint = request.endpoint
    user_agent = str(request.user_agent)
    
    log_message = f"User {user_id} performed '{action}' at {endpoint}. " \
                  f"IP: {ip_address}, User Agent: {user_agent}"
    
    if details:
        log_message += f", Details: {details}"
    
    from app import create_app
    app = create_app()
    with app.app_context():
        app.logger.info(log_message)