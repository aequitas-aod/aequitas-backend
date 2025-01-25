import subprocess

from flask import Flask
from flask_cors import CORS

from infrastructure.ws.resources.projects import projects_bp
from infrastructure.ws.resources.questionnaires import questionnaires_bp
from infrastructure.ws.resources.questions import questions_bp


def setup_db():
    subprocess.run(["echo", "Launching setup script"])
    subprocess.Popen(["./setup-db.sh"], shell=True)
    subprocess.run(["echo", "Script started"])


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(questions_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(questionnaires_bp)
    setup_db()
    return app
