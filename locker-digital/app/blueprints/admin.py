# Blueprint para panel de administración

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.authz import admin_required
from app.models import AuditLog, User, Evidence
from app import db
from app.services.audit import log_action
from flask_login import current_user

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@admin_required
def panel():
    
    total_users = User.query.count()
    total_evidences = Evidence.query.count()
    total_logs = AuditLog.query.count()
    return render_template(
        "admin_panel.html",
        title="Admin",
        total_users=total_users,
        total_evidences=total_evidences,
        total_logs=total_logs
    )

@admin_bp.route("/logs")
@admin_required
def logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(300).all()
    log_action(current_user.id, "ADMIN_VIEW_LOGS", target_type="AuditLog", target_id=None, details="limit=300")
    return render_template("admin_logs.html", title="Admin · Logs", logs=logs)

@admin_bp.route("/users")
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    log_action(current_user.id, "ADMIN_VIEW_USERS", target_type="User", target_id=None, details=f"count={len(users)}")
    return render_template("admin_users.html", title="Admin · Usuarios", users=users)

@admin_bp.route("/repos")
@admin_required
def repos():
    rows = (
        db.session.query(Evidence, User.email)
        .outerjoin(User, Evidence.owner_id == User.id)  
        .order_by(Evidence.created_at.desc())
        .all()
    )

   
    print("ADMIN REPOS rows:", len(rows))

    log_action(current_user.id, "ADMIN_VIEW_REPOS", target_type="Evidence", target_id=None, details=f"count={len(rows)}")
    return render_template("admin_repos.html", title="Admin · Repositorio", rows=rows)

@admin_bp.route("/users/set-role", methods=["POST"])
@admin_required
def set_role():
    # Cambiar rol desde panel admin
    user_id = request.form.get("user_id")
    new_role = request.form.get("new_role")

    if new_role not in ("admin", "student"):
        flash("Rol inválido.", "error")
        return redirect(url_for("admin.users"))

    u = User.query.get(user_id)
    if not u:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.users"))

    old_role = u.role
    u.role = new_role
    db.session.commit()

    log_action(current_user.id, "ADMIN_SET_ROLE", target_type="User", target_id=u.id, details=f"{old_role} -> {new_role}")
    flash(f"Rol actualizado: {u.email} ahora es {new_role}.", "success")
    return redirect(url_for("admin.users"))