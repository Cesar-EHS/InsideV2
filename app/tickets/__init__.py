from flask import Blueprint

from .routes import bp_tickets

def init_app(app):
    app.register_blueprint(bp_tickets, url_prefix='/tickets')