#MODELOS DE BASES DE DATOS

from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

# Tabla de usuarios
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(280), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tabla de evidencias

class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(120), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=False)

    sha256 = db.Column(db.String(64), nullable=False, index=True)
    signature_b64 = db.Column(db.Text, nullable=False)
    public_key_b64 = db.Column(db.Text, nullable=False)

    ai_duplicate_score = db.Column(db.Float, default=0.0)
    ai_flags = db.Column(db.Text, default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tabla de logs de auditoría
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    action = db.Column(db.String(60), nullable=False)
    target_type = db.Column(db.String(60), nullable=True)
    target_id = db.Column(db.Integer, nullable=True)

    ip = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Función para cargar el usuario por su ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))