# app/logros/routes.py
from flask import render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.logros import bp_logros
from app import db
from app.logros.models import Logro, EvidenciaLogro
from app.logros.forms import LogroForm, EvidenciaForm

# Puestos autorizados para crear logros
PUESTOS_AUTORIZADOS = [2, 5, 7, 8, 23, 24]

@bp_logros.route('/')
@login_required
def index():
    logros = Logro.query.all()
    form = LogroForm()
    evidencia_form = EvidenciaForm()
    return render_template('logros.html', logros=logros, form=form, evidencia_form=evidencia_form)


@bp_logros.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_logro():
    if current_user.puesto_trabajo_id not in PUESTOS_AUTORIZADOS:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'No tienes permisos para agregar logros.'}), 403
        flash('No tienes permisos para agregar logros.', 'danger')
        return redirect(url_for('logros.index'))

    form = LogroForm()
    if form.validate_on_submit():
        imagen = form.imagen.data
        nombre_archivo = secure_filename(imagen.filename)
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_archivo)
        imagen.save(ruta)

        logro = Logro(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            imagen=nombre_archivo,
            fecha_inicio=form.fecha_inicio.data,
            fecha_fin=form.fecha_fin.data,
            creador_id=current_user.id
        )
        db.session.add(logro)
        db.session.commit()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Renderiza el HTML del nuevo logro para insertar dinámicamente
            logro_html = render_template('partials/logro_card.html', logro=logro, current_user=current_user)
            return jsonify({'success': True, 'logro_html': logro_html})
        flash('Logro agregado exitosamente.', 'success')
        return redirect(url_for('logros.index'))

    # Si es AJAX, devuelve errores en JSON
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        errors = {field: errors for field, errors in form.errors.items()}
        return jsonify({'success': False, 'errors': errors, 'message': 'Corrige los errores del formulario.'}), 400

    return render_template('logros.html', form=form)


@bp_logros.route('/eliminar/<int:logro_id>', methods=['POST'])
@login_required
def eliminar_logro(logro_id):
    logro = Logro.query.get_or_404(logro_id)
    if logro.creador_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403

    db.session.delete(logro)
    db.session.commit()
    return jsonify({'success': True})


@bp_logros.route('/evidencia/<int:logro_id>', methods=['POST'])
@login_required
def subir_evidencia(logro_id):
    form = EvidenciaForm()
    logro = Logro.query.get_or_404(logro_id)

    # No permitir si ya subió evidencia
    ya_subio = logro.evidencias.filter_by(usuario_id=current_user.id).first()
    if ya_subio:
        flash('Ya has subido evidencia para este logro.', 'danger')
        return redirect(url_for('logros.index'))

    # No permitir si la fecha de término ya pasó
    if logro.fecha_fin and logro.fecha_fin < datetime.utcnow().date():
        flash('La fecha de término del logro ya pasó. No puedes anexar evidencia.', 'danger')
        return redirect(url_for('logros.index'))

    if form.validate_on_submit():
        archivo = form.archivo.data
        nombre_archivo = secure_filename(archivo.filename)
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo.save(ruta)

        evidencia = EvidenciaLogro(
            archivo=nombre_archivo,
            logro_id=logro.id,
            usuario_id=current_user.id
        )
        db.session.add(evidencia)
        db.session.commit()
        flash('Evidencia enviada correctamente.', 'success')
    else:
        flash('Error al subir la evidencia. Verifica el archivo.', 'danger')

    return redirect(url_for('logros.index'))


@bp_logros.route('/aprobar/<int:evidencia_id>', methods=['POST'])
@login_required
def aprobar_evidencia(evidencia_id):
    evidencia = EvidenciaLogro.query.get_or_404(evidencia_id)
    logro = evidencia.logro

    if current_user.id != logro.creador_id:
        return jsonify({'error': 'No autorizado'}), 403

    evidencia.estatus = 'Aprobado'
    db.session.commit()
    return jsonify({'success': True})


@bp_logros.route('/denegar/<int:evidencia_id>', methods=['POST'])
@login_required
def denegar_evidencia(evidencia_id):
    evidencia = EvidenciaLogro.query.get_or_404(evidencia_id)
    logro = evidencia.logro

    if current_user.id != logro.creador_id:
        return jsonify({'error': 'No autorizado'}), 403

    evidencia.estatus = 'Denegado'
    db.session.commit()
    return jsonify({'success': True})


@bp_logros.route('/archivo/<filename>')
@login_required
def descargar_archivo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
