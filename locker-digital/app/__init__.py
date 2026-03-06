# LO QUE INICIALIZA FLASK

import os
from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from werkzeug.exceptions import RequestEntityTooLarge
from flask import Flask, flash, redirect, url_for

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("instance", exist_ok=True)
    os.makedirs(app.config["KEYS_DIR"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.blueprints.auth import auth_bp
    from app.blueprints.evidence import evidence_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(evidence_bp)

    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    with app.app_context():
        from app import models
        db.create_all()

        @app.errorhandler(RequestEntityTooLarge)
        def handle_file_too_large(e):
            flash(" El archivo es demasiado grande para el límite permitido.", "error")
            return redirect(url_for("evidence.upload"))
    
    return app