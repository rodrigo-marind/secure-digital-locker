# Blueprint para autenticación de usuarios
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User
from app.services.audit import log_action

auth_bp = Blueprint("auth", __name__)

# ----------------------------
# Registro
# ----------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email y contraseña son requeridos.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Ese email ya existe.", "error")
            return redirect(url_for("auth.register"))

        pw_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        user = User(
            email=email,
            password_hash=pw_hash,
            role="student"  # por defecto
        )

        db.session.add(user)
        db.session.commit()

        log_action(
            user.id,
            "REGISTER",
            target_type="User",
            target_id=user.id
        )

        flash("Cuenta creada correctamente. Inicia sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", title="Registro")


# ----------------------------
# Login
# ----------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8")
        ):
            flash("Credenciales inválidas.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)

        log_action(
            user.id,
            "LOGIN",
            target_type="User",
            target_id=user.id
        )

        # Redirección según rol
        if user.role == "admin":
            return redirect(url_for("admin.panel"))

        return redirect(url_for("evidence.dashboard"))

    return render_template("login.html", title="Login")


# ----------------------------
# Logout
# ----------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    log_action(
        current_user.id,
        "LOGOUT",
        target_type="User",
        target_id=current_user.id
    )

    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("auth.login"))