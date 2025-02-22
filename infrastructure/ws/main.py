import os
import subprocess
from time import sleep

from flask import Flask
from flask_cors import CORS

from infrastructure.ws.resources.projects import projects_bp
from infrastructure.ws.resources.questionnaires import questionnaires_bp
from infrastructure.ws.resources.questions import questions_bp
from utils.env import ENV


def setup_db():
    sleep(1)
    subprocess.run(["echo", "Launching setup script"])
    subprocess.Popen(
        [f"./setup-db.sh {os.environ.get('AEQUITAS_BACKEND_PORT')}"], shell=True
    )
    subprocess.run(["echo", "Script started"])


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(questions_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(questionnaires_bp)
    if ENV != "test":
        setup_db()
    return app
