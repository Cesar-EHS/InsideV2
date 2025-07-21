import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from app import db
from app.home import home_bp
from app.home.models import Post, Evento, Comment, Reaction, post_proyectos
from app.home.forms import PostForm
from app.auth.models import User, Proyecto
from dateutil.relativedelta import relativedelta
from flask_wtf.csrf import CSRFProtect, CSRFError


def save_image_file(image_file):
    """Guardar imagen con nombre seguro y timestamp para evitar colisiones."""
    filename = secure_filename(image_file.filename)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    new_filename = f"{name}_{timestamp}{ext}"
    upload_folder = os.path.join(current_app.root_path, 'home', 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, new_filename)
    image_file.save(filepath)
    return new_filename


@home_bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form_post = PostForm()

    # Parámetros para publicaciones
    page = request.args.get('page', 1, type=int)
    filter_year = request.args.get('filter_year', type=int)
    filter_month = request.args.get('filter_month', type=int)
    filter_user = request.args.get('filter_user', type=int)
    filter_proyecto = request.args.get('filter_proyecto')

    # Filtrar publicaciones que el usuario puede ver
    query = Post.query.options(joinedload(Post.user), joinedload(Post.proyectos_visibles))
    
    # Filtros adicionales
    if filter_year:
        query = query.filter(db.extract('year', Post.timestamp) == filter_year)
    if filter_month:
        query = query.filter(db.extract('month', Post.timestamp) == filter_month)
    if filter_user:
        query = query.filter(Post.user_id == filter_user)
    
    # Filtro por proyecto específico
    if filter_proyecto:
        if filter_proyecto == 'publicos':
            # Solo posts públicos
            query = query.filter(Post.visible_para_todos == True)
        elif filter_proyecto.isdigit():
            # Posts de un proyecto específico
            proyecto_id = int(filter_proyecto)
            posts_proyecto = db.session.query(post_proyectos.c.post_id).filter(
                post_proyectos.c.proyecto_id == proyecto_id
            ).subquery()
            query = query.filter(Post.id.in_(db.session.query(posts_proyecto.c.post_id)))
    
    # Filtrar por proyectos visibles (solo si no hay filtro específico de proyecto)
    if not filter_proyecto:
        # 1. Posts marcados como visible_para_todos = True
        # 2. Posts asignados a su proyecto específico
        if current_user.proyecto:
            # Subquery para posts asignados al proyecto del usuario
            posts_con_proyecto = db.session.query(post_proyectos.c.post_id).filter(
                post_proyectos.c.proyecto_id == current_user.proyecto.id
            ).subquery()
            
            query = query.filter(
                db.or_(
                    Post.visible_para_todos == True,
                    Post.id.in_(db.session.query(posts_con_proyecto.c.post_id))
                )
            )
        else:
            # Si el usuario no tiene proyecto, solo ver publicaciones públicas
            query = query.filter(Post.visible_para_todos == True)
    
    pagination = query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=5, error_out=False)
    posts = pagination.items

    # Preparar datos de proyectos para el tooltip
    for post in posts:
        post.proyectos_nombres = post.get_proyectos_nombres()

    # Paginación y orden de eventos (compatibilidad SQLite)
    event_page = request.args.get('event_page', 1, type=int)
    hoy = datetime.today().date()
    eventos_proximos = Evento.query.filter(Evento.fecha >= hoy).order_by(Evento.fecha.asc()).all()
    eventos_pasados = Evento.query.filter(Evento.fecha < hoy).order_by(Evento.fecha.desc()).all()
    eventos_ordenados = eventos_proximos + eventos_pasados
    eventos_per_page = 5
    total_eventos = len(eventos_ordenados)
    start = (event_page - 1) * eventos_per_page
    end = start + eventos_per_page
    eventos = eventos_ordenados[start:end]
    
    class Pagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total // per_page) + (1 if total % per_page else 0)
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1
    eventos_pagination = Pagination(event_page, eventos_per_page, total_eventos)

    # Años disponibles para filtro de publicaciones
    años_posts = db.session.query(db.extract('year', Post.timestamp).label('year'))\
        .distinct().order_by('year').all()
    años_posts = [int(y.year) for y in años_posts]
    meses = list(range(1, 13))
    
    # Obtener usuarios y proyectos para filtros
    usuarios = User.query.filter(User.id != current_user.id).all()
    proyectos = Proyecto.query.all()

    return render_template(
        'home.html',
        form_post=form_post,
        posts=posts,
        eventos=eventos,
        usuario=current_user,
        pagination=pagination,
        filter_year=filter_year,
        filter_month=filter_month,
        filter_user=filter_user,
        filter_proyecto=filter_proyecto,
        años_posts=años_posts,
        meses=meses,
        usuarios=usuarios,
        proyectos=proyectos,
        eventos_pagination=eventos_pagination
    )


@home_bp.route('/post/create', methods=['POST'])
@login_required
def create_post():
    form = PostForm()
    if not form.validate_on_submit():
        return jsonify(success=False, message="Datos de publicación inválidos."), 400

    post = Post(content=form.content.data, user_id=current_user.id)

    # Manejar selección de proyectos
    proyectos_seleccionados = request.form.getlist('proyectos_visibles')
    
    if 'todos' in proyectos_seleccionados:
        # Si se selecciona "todos", el post es visible para todos
        post.visible_para_todos = True
    else:
        # Si se seleccionan proyectos específicos
        post.visible_para_todos = False
        proyectos_ids = [int(pid) for pid in proyectos_seleccionados if pid.isdigit()]
        if proyectos_ids:
            proyectos = Proyecto.query.filter(Proyecto.id.in_(proyectos_ids)).all()
            post.proyectos_visibles = proyectos

    if form.image.data:
        filename = save_image_file(form.image.data)
        post.image_filename = filename

    db.session.add(post)
    db.session.commit()

    return jsonify(success=True, message="Publicación creada con éxito."), 201


@home_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    try:
        content = request.form.get('comment_content')
        if not content or content.strip() == '':
            return jsonify(success=False, message='El comentario no puede estar vacío.'), 400

        comment = Comment(
            content=content.strip(),
            post_id=post_id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()

        # Usa la propiedad que tienes definida en tu modelo para la foto del usuario, por ejemplo:
        user_foto = getattr(current_user, 'foto_url', url_for('auth.static', filename='img/default_user.png'))

        timestamp_str = comment.timestamp.strftime('%d/%m/%Y %H:%M')
        puede_eliminar = (comment.user_id == current_user.id) or getattr(current_user, 'is_admin', False)
        delete_url = url_for('home.delete_comment', comment_id=comment.id)

        return jsonify({
            "success": True,
            "comment_id": comment.id,
            "comment_user": f"{current_user.nombre} {current_user.apellido_paterno}",
            "comment_user_avatar": user_foto,
            "comment_content": comment.content,
            "comment_timestamp": timestamp_str,
            "puede_eliminar": puede_eliminar,
            "delete_url": delete_url
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al agregar comentario: {e}")
        return jsonify(success=False, message='Error interno del servidor.'), 500


@home_bp.route('/add_reaction/<int:post_id>', methods=['POST'])
@login_required
def add_reaction(post_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify(success=False, message='Solicitud no válida.'), 400

    reaction_type = request.args.get('reaction_type')

    if reaction_type != 'love':
        return jsonify(success=False, message='Tipo de reacción inválido.'), 400

    post = Post.query.get_or_404(post_id)

    existing = Reaction.query.filter_by(post_id=post.id, user_id=current_user.id).first()

    if existing:
        # Si ya reaccionó, quitar reacción (alternar)
        db.session.delete(existing)
    else:
        # Si no ha reaccionado, agregar nueva
        reaction = Reaction(post_id=post.id, user_id=current_user.id, type='love')
        db.session.add(reaction)

    db.session.commit()

    # Recuento actualizado
    love_count = Reaction.query.filter_by(post_id=post.id, type='love').count()

    return jsonify(success=True, love_count=love_count), 200


@home_bp.route('/evento/delete/<int:id>', methods=['POST'])
@login_required
def delete_evento(id):
    evento = Evento.query.get_or_404(id)
    db.session.delete(evento)
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True, message='Evento eliminado correctamente.')
    flash('Evento eliminado correctamente.', 'success')
    return redirect(url_for('home.home'))


@home_bp.route('/post/<int:post_id>/comments', methods=['GET'])
@login_required
def get_comments(post_id):
    """Obtener comentarios de un post con paginación"""
    try:
        # Verificar que el post existe
        post = Post.query.get_or_404(post_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = 4  # Mostrar 4 comentarios por página
        
        comments_query = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.desc())
        comments_pagination = comments_query.paginate(page=page, per_page=per_page, error_out=False)
        comments = comments_pagination.items
        
        comments_data = []
        for comment in comments:
            try:
                # Obtener foto del usuario con manejo de errores
                if hasattr(comment.user, 'foto_url') and comment.user.foto_url:
                    user_foto = comment.user.foto_url
                else:
                    user_foto = url_for('auth.static', filename='img/default_user.png')
                
                # Verificar que el usuario tiene nombre
                if hasattr(comment.user, 'nombre') and hasattr(comment.user, 'apellido_paterno'):
                    user_name = f"{comment.user.nombre} {comment.user.apellido_paterno}"
                else:
                    user_name = "Usuario"
                
                timestamp_str = comment.timestamp.strftime('%d/%m/%Y %H:%M')
                puede_eliminar = (comment.user_id == current_user.id) or getattr(current_user, 'is_admin', False)
                delete_url = url_for('home.delete_comment', comment_id=comment.id)
                
                comments_data.append({
                    "id": comment.id,
                    "user_name": user_name,
                    "user_avatar": user_foto,
                    "content": comment.content,
                    "timestamp": timestamp_str,
                    "puede_eliminar": puede_eliminar,
                    "delete_url": delete_url
                })
            except Exception as comment_error:
                current_app.logger.error(f"Error procesando comentario {comment.id}: {comment_error}")
                continue
        
        return jsonify({
            "success": True,
            "comments": comments_data,
            "has_next": comments_pagination.has_next,
            "next_page": comments_pagination.next_num if comments_pagination.has_next else None,
            "total": comments_pagination.total
        })
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener comentarios para post {post_id}: {str(e)}")
        return jsonify(success=False, message=f'Error al cargar comentarios: {str(e)}'), 500


@home_bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    # Solo autor o administrador puede eliminar
    if comment.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        return jsonify(success=False, message='No tienes permiso para eliminar este comentario.'), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify(success=True, message='Comentario eliminado.')
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Error al eliminar el comentario.'), 500


@home_bp.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Solo autor o admin
    if post.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        return jsonify(success=False, message='No tienes permiso para eliminar esta publicación.'), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify(success=True, message='Publicación eliminada.')
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Error al eliminar la publicación.'), 500


@home_bp.route('/evento/create', methods=['POST'])
@login_required
def create_evento():
    # Solo usuarios permitidos
    puestos_permitidos = [2, 5, 7, 8, 23, 24]
    if not (current_user.puesto_trabajo and current_user.puesto_trabajo.id in puestos_permitidos):
        return jsonify(success=False, message='No tienes permiso para crear eventos.'), 403

    data = request.form
    titulo = data.get('titulo', '').strip()
    descripcion = data.get('descripcion', '').strip()
    fecha = data.get('fecha', '').strip()
    hora = data.get('hora', '').strip()
    link_teams = data.get('link_teams', '').strip()

    if not titulo or not fecha:
        return jsonify(success=False, message='Título y fecha son obligatorios.'), 400

    try:
        from datetime import datetime
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
        hora_dt = datetime.strptime(hora, '%H:%M').time() if hora else None
        from app.home.models import Evento
        evento = Evento(
            titulo=titulo,
            descripcion=descripcion,
            fecha=fecha_dt,
            hora=hora_dt,
            link_teams=link_teams or None
        )
        db.session.add(evento)
        db.session.commit()
        return jsonify(success=True, message='Evento creado correctamente.')
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message='Error al crear evento.'), 500
