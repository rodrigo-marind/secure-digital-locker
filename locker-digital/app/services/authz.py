# Autorización de usuarios basada en roles (ADMIN/ESTUDIANTE)

from functools import wraps
from flask import request, redirect, url_for, abort
from flask_login import current_user

PUBLIC_ENDPOINTS = {
    "auth.login",
    "auth.register",
    "evidence.home",
    "evidence.how_it_works",
}

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):

        # Permitir acceso a endpoints públicos
        if request.endpoint is None:
            return view_func(*args, **kwargs)

        if request.endpoint.startswith("static"):
            return view_func(*args, **kwargs)

        if request.endpoint in PUBLIC_ENDPOINTS:
            return view_func(*args, **kwargs)

        # Si no hay sesion, redirige al usuario a login
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        # Evita que usuarios no admin accedan a panel admin
        if getattr(current_user, "role", None) != "admin":
            return abort(403)

        return view_func(*args, **kwargs)

    return wrapper