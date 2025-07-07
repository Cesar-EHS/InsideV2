import os
from flask import (
    render_template, request, redirect, url_for, flash,
    current_app, abort, send_from_directory
)
from werkzeug.utils import secure_filename
from . import knowledge_bp
from app.knowledge.forms import DocumentoForm
from app.knowledge.models import Documento
from app import db
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf


def get_upload_folder():
    """Devuelve la ruta absoluta donde se guardan los archivos subidos."""
    return os.path.join(current_app.root_path, 'knowledge', 'static', 'uploads')


@knowledge_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Muestra la lista de documentos y permite subir nuevos si el usuario está autorizado."""
    form = DocumentoForm()
    documentos = Documento.query.order_by(Documento.fecha_carga.desc()).all()

    # Las categorías válidas deben coincidir con las del modelo y el form
    categorias_permitidas = [c[0] for c in form.categoria.choices]

    if form.validate_on_submit():
        if form.categoria.data not in categorias_permitidas:
            flash('Categoría inválida.', 'error')
            return redirect(url_for('knowledge.index'))

        file = form.archivo.data
        filename = secure_filename(file.filename)

        # Carpeta por categoría
        categoria_folder = os.path.join(get_upload_folder(), form.categoria.data)
        os.makedirs(categoria_folder, exist_ok=True)
        filepath = os.path.join(categoria_folder, filename)

        if os.path.exists(filepath):
            flash('Ya existe un archivo con ese nombre en esta categoría.', 'error')
            return redirect(url_for('knowledge.index'))

        try:
            file.save(filepath)
        except Exception as e:
            current_app.logger.error(f"Error al guardar archivo: {e}")
            flash('Error al guardar el archivo en el servidor.', 'error')
            return redirect(url_for('knowledge.index'))

        nuevo_doc = Documento(
            nombre=form.nombre.data,
            tipo=form.tipo.data,
            categoria=form.categoria.data,
            archivo=os.path.join(form.categoria.data, filename).replace('\\', '/')
        )
        db.session.add(nuevo_doc)
        db.session.commit()

        flash('Documento cargado correctamente.', 'success')
        return redirect(url_for('knowledge.index'))

    return render_template('knowledge.html', form=form, documentos=documentos, usuario=current_user)


@knowledge_bp.route('/delete/<int:document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    """Elimina un documento y su archivo solo si el usuario tiene puesto 7 (encargado)."""
    if not current_user.puesto_trabajo or current_user.puesto_trabajo.id != 7:
        abort(403)  # Prohibido

    doc = Documento.query.get_or_404(document_id)
    upload_folder = get_upload_folder()
    file_path = os.path.join(upload_folder, doc.archivo)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        current_app.logger.error(f"Error al eliminar archivo {file_path}: {e}")
        flash('Error al eliminar el archivo del servidor.', 'error')
        return redirect(url_for('knowledge.index'))

    try:
        db.session.delete(doc)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error al eliminar registro en BD: {e}")
        flash('Error al eliminar el registro en base de datos.', 'error')
        return redirect(url_for('knowledge.index'))

    flash('Documento eliminado correctamente.', 'success')
    return redirect(url_for('knowledge.index'))


@knowledge_bp.route('/archivo/<path:archivo>')
@login_required
def descargar_archivo(archivo):
    """Sirve archivos subidos a knowledge, usando rutas seguras y cross-platform."""
    upload_folder = get_upload_folder()
    # Normaliza la ruta para evitar problemas de barra invertida y seguridad
    archivo = archivo.replace('..', '').replace('\\', '/').replace('//', '/')
    return send_from_directory(upload_folder, archivo)


@knowledge_bp.context_processor
def inject_csrf_token():
    """Inyecta csrf_token para los formularios Jinja2, evitando errores de CSRF."""
    return dict(csrf_token=generate_csrf)
