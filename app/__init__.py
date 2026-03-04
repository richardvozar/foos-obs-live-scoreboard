from flask import Flask
from .routes import bp
from .team_source import start_team_fetcher

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)

    # háttérben futó teamname fetcher (daemon thread)
    start_team_fetcher()

    return app