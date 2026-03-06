# Servicio para registrar acciones de auditoría en la aplicación

from flask import request
from app import db
from app.models import AuditLog


def log_action(actor_id, action, target_type=None, target_id=None, details=None):
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        user_agent=(request.headers.get("User-Agent") or "")[:255],
        details=details,
    )
    db.session.add(entry)
    db.session.commit()