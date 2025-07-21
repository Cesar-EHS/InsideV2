import os
from flask import (
    render_template, request, redirect, url_for, flash,
    current_app, abort, send_from_directory, jsonify
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
    """Muestra la vista principal de categorías del módulo Knowledge/Recursos."""
    form = DocumentoForm()

    # Categorías actualizadas
    categorias_permitidas = [
        'Operaciones',
        'Administración', 
        'Recursos Humanos',
        'Desarrollo Organizacional',
        'Comercial & Branding'
    ]

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
            archivo=os.path.join(form.categoria.data, filename).replace('\\', '/'),
            descripcion=form.descripcion.data
        )
        db.session.add(nuevo_doc)
        db.session.commit()

        flash('Documento cargado correctamente.', 'success')
        return redirect(url_for('knowledge.index'))

    # Obtener conteo de documentos por categoría
    categoria_counts = {}
    for categoria in categorias_permitidas:
        count = Documento.query.filter_by(categoria=categoria).count()
        categoria_counts[categoria] = count

    return render_template('knowledge/index.html', 
                         form=form, 
                         usuario=current_user,
                         categorias=categorias_permitidas,
                         categoria_counts=categoria_counts)


@knowledge_bp.route('/categoria/<string:categoria>')
@login_required  
def view_categoria(categoria):
    """Muestra los documentos de una categoría específica."""
    categorias_permitidas = [
        'Operaciones',
        'Administración', 
        'Recursos Humanos',
        'Desarrollo Organizacional',
        'Comercial & Branding'
    ]
    
    if categoria not in categorias_permitidas:
        flash('Categoría no válida.', 'error')
        return redirect(url_for('knowledge.index'))
    
    # Filtros
    tipo_filter = request.args.get('tipo', '')
    search_query = request.args.get('search', '')
    order_by = request.args.get('order', 'fecha')  # abc o fecha
    
    # Query base
    query = Documento.query.filter_by(categoria=categoria)
    
    # Aplicar filtros
    if tipo_filter:
        query = query.filter_by(tipo=tipo_filter)
    
    if search_query:
        query = query.filter(Documento.nombre.ilike(f'%{search_query}%'))
    
    # Aplicar ordenamiento
    if order_by == 'abc':
        documentos = query.order_by(Documento.nombre.asc()).all()
    else:
        documentos = query.order_by(Documento.fecha_carga.desc()).all()
    
    # Obtener tipos únicos para el filtro
    tipos_disponibles = db.session.query(Documento.tipo.distinct()).filter_by(categoria=categoria).all()
    tipos_disponibles = [tipo[0] for tipo in tipos_disponibles]
    
    return render_template('knowledge/categoria.html',
                         categoria=categoria,
                         documentos=documentos,
                         tipos_disponibles=tipos_disponibles,
                         current_tipo=tipo_filter,
                         current_search=search_query,
                         current_order=order_by,
                         usuario=current_user)


@knowledge_bp.route('/delete/<int:document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    """Elimina un documento y su archivo solo si el usuario tiene puesto 7 (encargado)."""
    if not current_user.puesto_trabajo or current_user.puesto_trabajo.id != 7:
        if request.is_json:
            return jsonify({'error': 'No autorizado'}), 403
        abort(403)  # Prohibido

    doc = Documento.query.get_or_404(document_id)
    upload_folder = get_upload_folder()
    file_path = os.path.join(upload_folder, doc.archivo)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        current_app.logger.error(f"Error al eliminar archivo {file_path}: {e}")
        if request.is_json:
            return jsonify({'error': 'Error al eliminar el archivo del servidor'}), 500
        flash('Error al eliminar el archivo del servidor.', 'error')
        return redirect(url_for('knowledge.index'))

    try:
        db.session.delete(doc)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error al eliminar registro en BD: {e}")
        if request.is_json:
            return jsonify({'error': 'Error al eliminar el registro en base de datos'}), 500
        flash('Error al eliminar el registro en base de datos.', 'error')
        return redirect(url_for('knowledge.index'))

    if request.is_json:
        return jsonify({'success': True, 'message': 'Documento eliminado correctamente'})
    
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
