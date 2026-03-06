# Blueprint para manejar rutas relacionadas con evidencia

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask import send_from_directory
from app import db
from app.models import Evidence
from app.services.crypto import (
    sha256_file,
    generate_ed25519_keypair,
    sign_hash_hex,
    verify_hash_hex,
    b64e,
    b64d,
)
from app.services.audit import log_action
from app.services.ai import evaluate_evidence  #  IA 

evidence_bp = Blueprint("evidence", __name__)

@evidence_bp.route("/")
def home():
    return render_template("home.html", title="Inicio")

@evidence_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No se envió archivo.", "error")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("Archivo vacío.", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)

        # Validar extensión permitida
        allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "docx", "zip"})
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in allowed:
            flash("Formato no permitido. Solo PDF, DOCX o ZIP.", "error")
            return redirect(request.url)

        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)

        # Guardar archivo
        stored_name = f"{current_user.id}_{filename}"
        path = os.path.join(upload_dir, stored_name)
        file.save(path)

        size_bytes = os.path.getsize(path)
        sha256 = sha256_file(path)

        # IA / Automatización: comparar contra evidencias existentes del usuario
        existing = Evidence.query.filter_by(owner_id=current_user.id).all()
        score, flags, similar_to_id = evaluate_evidence(
            new_sha256=sha256,
            new_filename=filename,
            new_size=size_bytes,
            existing_evidences=existing
        )
        ai_flags_text = ",".join(flags)

        # Firmar hash con Ed25519
        private_key, public_key = generate_ed25519_keypair()
        signature = sign_hash_hex(private_key, sha256)

        # Guardar en DB
        evidence = Evidence(
            owner_id=current_user.id,
            original_filename=filename,
            stored_filename=stored_name,
            mimetype=file.mimetype,
            size_bytes=size_bytes,
            sha256=sha256,
            signature_b64=b64e(signature),
            public_key_b64=b64e(public_key),
            ai_duplicate_score=score,
            ai_flags=ai_flags_text,
        )
        db.session.add(evidence)
        db.session.commit()

        # Auditoría
        log_action(
            current_user.id,
            "UPLOAD",
            target_type="Evidence",
            target_id=evidence.id,
            details=f"SHA256={sha256}; score={score:.2f}; flags={ai_flags_text}; similar_to={similar_to_id}",
        )

        # Alertas automáticas
        flash("Evidencia subida y firmada correctamente", "success")
        if "DUPLICATE_HASH" in flags:
            flash("Archivo duplicado detectado (mismo hash).", "warning")
        elif "HIGH_SIMILARITY" in flags:
            flash("Alta similitud detectada con un archivo anterior.", "warning")
        elif "MEDIUM_SIMILARITY" in flags:
            flash("Similaridad media detectada con un archivo anterior.", "info")

        return redirect(url_for("evidence.dashboard"))

    return render_template("upload.html", title="Subir evidencia")

@evidence_bp.route("/verify/<int:evidence_id>")
@login_required
def verify(evidence_id):
    e = Evidence.query.get_or_404(evidence_id)

    # Solo el dueño puede verificar
    if e.owner_id != current_user.id:
        flash("No autorizado.", "error")
        return redirect(url_for("evidence.dashboard"))

    path = os.path.join(current_app.config["UPLOAD_FOLDER"], e.stored_filename)
    if not os.path.exists(path):
        flash("El archivo físico no existe en el servidor.", "error")
        return redirect(url_for("evidence.dashboard"))

    current_hash = sha256_file(path)

    valid_hash = (current_hash == e.sha256)
    valid_signature = verify_hash_hex(
        b64d(e.public_key_b64),
        current_hash,
        b64d(e.signature_b64),
    )

    log_action(
        current_user.id,
        "VERIFY",
        target_type="Evidence",
        target_id=e.id,
        details=f"hash_ok={valid_hash}; sig_ok={valid_signature}",
    )
    return render_template(
        "verify.html",
        title="Verificación",
        evidence=e,
        current_hash=current_hash,
        valid_hash=valid_hash,
        valid_signature=valid_signature,
    )

# RUTA PARA VER Y DESCARGAR ARCHIVOS
@evidence_bp.route("/view/<int:evidence_id>")
@login_required
def view_file(evidence_id):
    e = Evidence.query.get_or_404(evidence_id)

    # Solo el dueño puede ver
    if e.owner_id != current_user.id:
        flash("No autorizado.", "error")
        return redirect(url_for("evidence.dashboard"))

    upload_dir = current_app.config["UPLOAD_FOLDER"]


    log_action(
        current_user.id,
        "VIEW_FILE",
        target_type="Evidence",
        target_id=e.id,
        details=e.original_filename,
    )

    
    return send_from_directory(
        upload_dir,
        e.stored_filename,
        as_attachment=False
    )

# RUTA ELIMINAR ARCHIVOS

@evidence_bp.route("/delete/<int:evidence_id>", methods=["POST"])
@login_required
def delete_file(evidence_id):
    e = Evidence.query.get_or_404(evidence_id)

    if e.owner_id != current_user.id:
        flash("No autorizado.", "error")
        return redirect(url_for("evidence.dashboard"))

    path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        e.stored_filename
    )

    # Borrar archivo físico
    if os.path.exists(path):
        os.remove(path)

    # Auditoría antes de borrar el registro
    log_action(
        current_user.id,
        "DELETE",
        target_type="Evidence",
        target_id=e.id,
        details=e.original_filename,
    )

    
    db.session.delete(e)
    db.session.commit()

    flash("Archivo eliminado correctamente.", "success")
    return redirect(url_for("evidence.dashboard"))

@evidence_bp.route("/dashboard")
@login_required
def dashboard():
    evidences = (
        Evidence.query
        .filter_by(owner_id=current_user.id)
        .order_by(Evidence.created_at.desc())
        .all()
    )

    total = len(evidences)
    with_alerts = sum(1 for e in evidences if (e.ai_flags and e.ai_flags.strip()))
    duplicates = sum(1 for e in evidences if (e.ai_flags and "DUPLICATE_HASH" in e.ai_flags))

    return render_template(
        "evidences.html",
        title="Evidencias",
        evidences=evidences,
        total=total,
        with_alerts=with_alerts,
        duplicates=duplicates
    )

@evidence_bp.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html", title="Cómo funciona")