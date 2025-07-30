from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
)
from flask_login import login_required, current_user
from app import db
from app.cursos.models import (
    Curso, Inscripcion, Examen, Pregunta,
    ExamenResultado, Actividad, ActividadResultado
)
from app.cursos.forms import CursoForm, ExamenForm, PreguntaForm, ActividadForm
from werkzeug.utils import secure_filename
import os
from flask import current_app

bp_cursos = Blueprint('cursos', __name__, template_folder='templates', static_folder='static')

encargados = {
    10: 'Soporte Sistemas',
    3: 'Requisición Compras',
    24: 'Desarrollo Organizacional',
    7: 'Capacitación Técnica',
    9: 'Diseño Institucional',
    2: 'Recursos Humanos',
    6: 'Soporte EHSmart'
}

# --- Utilidad para actualizar avance ---
def actualizar_avance(inscripcion):
    curso = inscripcion.curso
    total = len(curso.examenes) + len(curso.actividades)
    if total == 0:
        inscripcion.avance = 0
        db.session.commit()
        return
    completados = 0
    # Exámenes completados
    ex_ids = {r.examen_id for r in inscripcion.examenes_realizados if r.calificacion is not None}
    completados += len(ex_ids)
    # Actividades entregadas
    act_ids = {r.actividad_id for r in inscripcion.actividades_realizadas if r.entregado}
    completados += len(act_ids)
    inscripcion.avance = round((completados / total) * 100, 2)
    db.session.commit()


# ---------- CURSOS ----------

@bp_cursos.route('/')
@login_required
def index():
    categoria_filtro = request.args.get('categoria', None)
    page = request.args.get('page', 1, type=int)

    #Cursos en los que el usuario ya está inscrito
    mis_cursos_inscrito = Curso.query.join(Inscripcion).filter(
        Inscripcion.usuario_id == current_user.id,
        Inscripcion.activo == True
    ).order_by(Curso.fecha_creacion.desc()).all()

    #Instancia del formulario para pasarla a la plantilla principal
    form_curso = CursoForm()

    """ mis_cursos = Curso.query.join(Inscripcion).filter(
        Inscripcion.usuario_id == current_user.id,
        Inscripcion.activo == True
    ).limit(4).all() """

    mis_cursos_creados = Curso.query.filter_by(creador_id=current_user.id).order_by(Curso.fecha_creacion.desc()).paginate(page=page, per_page=3)

    query = Curso.query
    if categoria_filtro:
        query = query.filter(Curso.categoria == categoria_filtro)

    subq = db.session.query(Inscripcion.curso_id).filter(
        Inscripcion.usuario_id == current_user.id,
        Inscripcion.activo == True
    ).subquery()
    query = query.filter(~Curso.id.in_(subq))

    cursos = query.order_by(Curso.fecha_creacion.desc()).paginate(page=page, per_page=16)

    categorias = [
        'Protección Civil', 'Seguridad Industrial', 'Salud Ocupacional',
        'Protección Medioambiente', 'Herramientas Digitales', 'Desarrollo Humano'
    ]

    #Verficar si el usuario es encargado de cursos
    es_encargado = current_user.puesto_trabajo_id in encargados

    return render_template('cursos/index.html',
                           mis_cursos_inscrito=mis_cursos_inscrito, cursos=cursos,
                           mis_cursos_creados=mis_cursos_creados,
                           categorias=categorias, categoria_filtro=categoria_filtro,
                           es_encargado=es_encargado, form=form_curso)


@bp_cursos.route('/curso/<int:curso_id>')
@login_required
def curso_detalle(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if curso.creador_id != current_user.id:
        inscripcion = Inscripcion.query.filter_by(
            usuario_id=current_user.id,
            curso_id=curso.id,
            activo=True
        ).first()
        if not inscripcion:
            abort(403)

    return render_template('cursos/curso_detalle.html', curso=curso)


@bp_cursos.route('/agregar', methods=['POST']) #Dejar solo POST (antes tambien tenia get)
@login_required
def agregar_curso():
    # Ajusta los puestos permitidos según tu lógica
    puestos_permitidos = [2, 5, 7, 8, 23, 24]
    if current_user.puesto_trabajo_id not in puestos_permitidos:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Permiso denegado.'}), 403
        abort(403)

    form = CursoForm()
    if form.validate_on_submit():
        filename = None
        if form.imagen.data:
            filename = secure_filename(form.imagen.data.filename)
            # Define la ruta absoluta donde guardar la imagen
            abs_path = os.path.join(current_app.static_folder, 'cursos', 'img')
            os.makedirs(abs_path, exist_ok=True) # Crea el directorio si no existe
            form.imagen.data.save(os.path.join(abs_path, filename))
            ruta = os.path.join('cursos/img', filename) # Ruta relativa para guardar en la DB
        else:
            ruta = None # Si no se sube imagen, la ruta es None

        curso = Curso(
            categoria_id=form.categoria.data,
            modalidad=form.modalidad.data,
            objetivo=form.objetivo.data,
            nombre=form.nombre.data,
            contenido=form.contenido.data,
            area_tematica=form.area_tematica.data,
            duracion=form.duracion.data,
            tipo_agente=form.tipo_agente.data,
            creador_id=current_user.id,
            imagen=ruta
        )
        db.session.add(curso)
        db.session.commit()
        
        # Responde con JSON para la petición AJAX
        return jsonify({'success': True, 'message': 'Curso agregado correctamente.'})
    else:
        # Si la validación falla, devuelve JSON con los errores
        # Incluye 'errors' para que el JS pueda mostrarlos campo por campo si lo deseas
        return jsonify({'success': False, 'errors': form.errors, 'message': 'Errores de validación en el formulario.'}), 400


@bp_cursos.route('/inscribirse/<int:curso_id>', methods=['POST'])
@login_required
def inscribirse(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    inscripcion = Inscripcion.query.filter_by(
        usuario_id=current_user.id,
        curso_id=curso.id,
        activo=True
    ).first()
    if inscripcion:
        flash('Ya estás inscrito en este curso.', 'info')
        return redirect(url_for('cursos.index'))
    nueva_inscripcion = Inscripcion(
        usuario_id=current_user.id,
        curso_id=curso.id,
        avance=0.0,
        activo=True
    )
    db.session.add(nueva_inscripcion)
    db.session.commit()
    flash(f'Se inscribió al curso "{curso.nombre}".', 'success')
    return redirect(url_for('cursos.index'))


# ---------- EXÁMENES ----------

@bp_cursos.route('/curso/<int:curso_id>/examenes')
@login_required
def examenes_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if curso.creador_id != current_user.id:
        inscripcion = Inscripcion.query.filter_by(
            usuario_id=current_user.id,
            curso_id=curso.id,
            activo=True
        ).first()
        if not inscripcion:
            abort(403)

    examenes = curso.examenes
    return render_template('cursos/examenes.html', curso=curso, examenes=examenes)


@bp_cursos.route('/curso/<int:curso_id>/examen/agregar', methods=['GET', 'POST'])
@login_required
def agregar_examen(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if curso.creador_id != current_user.id:
        abort(403)

    form = ExamenForm()
    if form.validate_on_submit():
        examen = Examen(
            curso_id=curso.id,
            titulo=form.titulo.data,
            descripcion=form.descripcion.data
        )
        db.session.add(examen)
        db.session.commit()
        flash('Examen agregado correctamente.', 'success')
        return redirect(url_for('cursos.examenes_curso', curso_id=curso.id))

    return render_template('cursos/agregar_examen.html', form=form, curso=curso)


@bp_cursos.route('/examen/<int:examen_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_examen(examen_id):
    examen = Examen.query.get_or_404(examen_id)
    curso = examen.curso
    if curso.creador_id != current_user.id:
        abort(403)

    form = ExamenForm(obj=examen)
    if form.validate_on_submit():
        examen.titulo = form.titulo.data
        examen.descripcion = form.descripcion.data
        db.session.commit()
        flash('Examen actualizado correctamente.', 'success')
        return redirect(url_for('cursos.examenes_curso', curso_id=curso.id))

    return render_template('cursos/editar_examen.html', form=form, examen=examen)


# ---------- PREGUNTAS ----------

@bp_cursos.route('/examen/<int:examen_id>/pregunta/agregar', methods=['GET', 'POST'])
@login_required
def agregar_pregunta(examen_id):
    examen = Examen.query.get_or_404(examen_id)
    curso = examen.curso
    if curso.creador_id != current_user.id:
        abort(403)

    form = PreguntaForm()
    if form.validate_on_submit():
        pregunta = Pregunta(
            examen_id=examen.id,
            texto=form.texto.data,
            tipo=form.tipo.data,
            opciones=form.opciones.data if form.tipo.data == 'opcion_multiple' else None,
            respuesta_correcta=form.respuesta_correcta.data
        )
        db.session.add(pregunta)
        db.session.commit()
        flash('Pregunta agregada correctamente.', 'success')
        return redirect(url_for('cursos.editar_examen', examen_id=examen.id))

    return render_template('cursos/agregar_pregunta.html', form=form, examen=examen)


@bp_cursos.route('/pregunta/<int:pregunta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_pregunta(pregunta_id):
    pregunta = Pregunta.query.get_or_404(pregunta_id)
    examen = pregunta.examen
    curso = examen.curso
    if curso.creador_id != current_user.id:
        abort(403)

    form = PreguntaForm(obj=pregunta)
    if form.validate_on_submit():
        pregunta.texto = form.texto.data
        pregunta.tipo = form.tipo.data
        pregunta.opciones = form.opciones.data if form.tipo.data == 'opcion_multiple' else None
        pregunta.respuesta_correcta = form.respuesta_correcta.data
        db.session.commit()
        flash('Pregunta actualizada correctamente.', 'success')
        return redirect(url_for('cursos.editar_examen', examen_id=examen.id))

    return render_template('cursos/editar_pregunta.html', form=form, pregunta=pregunta)


# ---------- ACTIVIDADES ----------

@bp_cursos.route('/curso/<int:curso_id>/actividades')
@login_required
def actividades_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if curso.creador_id != current_user.id:
        inscripcion = Inscripcion.query.filter_by(
            usuario_id=current_user.id,
            curso_id=curso.id,
            activo=True
        ).first()
        if not inscripcion:
            abort(403)
    actividades = curso.actividades
    return render_template('cursos/actividades.html', curso=curso, actividades=actividades)


@bp_cursos.route('/curso/<int:curso_id>/actividad/agregar', methods=['GET', 'POST'])
@login_required
def agregar_actividad(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if curso.creador_id != current_user.id:
        abort(403)

    form = ActividadForm()
    if form.validate_on_submit():
        actividad = Actividad(
            curso_id=curso.id,
            titulo=form.titulo.data,
            descripcion=form.descripcion.data
        )
        db.session.add(actividad)
        db.session.commit()
        flash('Actividad agregada correctamente.', 'success')
        return redirect(url_for('cursos.actividades_curso', curso_id=curso.id))

    return render_template('cursos/agregar_actividad.html', form=form, curso=curso)


@bp_cursos.route('/actividad/<int:actividad_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_actividad(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    curso = actividad.curso
    if curso.creador_id != current_user.id:
        abort(403)

    form = ActividadForm(obj=actividad)
    if form.validate_on_submit():
        actividad.titulo = form.titulo.data
        actividad.descripcion = form.descripcion.data
        db.session.commit()
        flash('Actividad actualizada correctamente.', 'success')
        return redirect(url_for('cursos.actividades_curso', curso_id=curso.id))

    return render_template('cursos/editar_actividad.html', form=form, actividad=actividad)


# ---------- RESULTADOS DE EXÁMENES Y ACTIVIDADES ----------

@bp_cursos.route('/inscripcion/<int:inscripcion_id>/examen/<int:examen_id>/resultado', methods=['GET', 'POST'])
@login_required
def resultado_examen(inscripcion_id, examen_id):
    # Validar que la inscripcion pertenece al usuario
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    if inscripcion.usuario_id != current_user.id:
        abort(403)

    examen = Examen.query.get_or_404(examen_id)
    if examen.curso_id != inscripcion.curso_id:
        abort(404)

    # Aquí podrías implementar la lógica para mostrar y enviar respuestas,
    # Calcular calificación y guardar en ExamenResultado.
    # Por ahora solo mostramos un placeholder:
    return render_template('cursos/resultado_examen.html', inscripcion=inscripcion, examen=examen)


@bp_cursos.route('/inscripcion/<int:inscripcion_id>/actividad/<int:actividad_id>/resultado', methods=['GET', 'POST'])
@login_required
def resultado_actividad(inscripcion_id, actividad_id):
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    if inscripcion.usuario_id != current_user.id:
        abort(403)

    actividad = Actividad.query.get_or_404(actividad_id)
    if actividad.curso_id != inscripcion.curso_id:
        abort(404)

    # Similar a resultado_examen, para entregar archivo o respuestas
    return render_template('cursos/resultado_actividad.html', inscripcion=inscripcion, actividad=actividad)


@bp_cursos.route('/enviar_resultado_examen/<int:examen_id>', methods=['POST'])
@login_required
def enviar_resultado_examen(examen_id):
    examen = Examen.query.get_or_404(examen_id)
    curso = examen.curso
    inscripcion = Inscripcion.query.filter_by(usuario_id=current_user.id, curso_id=curso.id, activo=True).first_or_404()
    # Procesar respuestas y calificar automáticamente
    aciertos = 0
    total = len(examen.preguntas)
    for pregunta in examen.preguntas:
        respuesta = request.form.get(f'respuesta_{pregunta.id}')
        if pregunta.tipo in ['opcion_multiple', 'verdadero_falso']:
            if respuesta and respuesta.strip().lower() == (pregunta.respuesta_correcta or '').strip().lower():
                aciertos += 1
    calificacion = round((aciertos / total) * 100, 2) if total > 0 else 0
    # Registrar resultado
    resultado = ExamenResultado.query.filter_by(inscripcion_id=inscripcion.id, examen_id=examen.id).first()
    if not resultado:
        resultado = ExamenResultado(inscripcion_id=inscripcion.id, examen_id=examen.id)
        db.session.add(resultado)
    resultado.calificacion = calificacion
    db.session.commit()
    actualizar_avance(inscripcion)
    flash(f'Examen enviado. Calificación: {calificacion}', 'success')
    return redirect(url_for('cursos.curso_detalle', curso_id=curso.id))


@bp_cursos.route('/enviar_resultado_actividad/<int:actividad_id>', methods=['POST'])
@login_required
def enviar_resultado_actividad(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    curso = actividad.curso
    inscripcion = Inscripcion.query.filter_by(usuario_id=current_user.id, curso_id=curso.id, activo=True).first_or_404()
    resultado = ActividadResultado.query.filter_by(inscripcion_id=inscripcion.id, actividad_id=actividad.id).first()
    if not resultado:
        resultado = ActividadResultado(inscripcion_id=inscripcion.id, actividad_id=actividad.id)
        db.session.add(resultado)
    resultado.entregado = True
    resultado.fecha_entregado = db.func.now()
    resultado.retroalimentacion = request.form.get('comentario')
    # (Opcional: guardar archivo de entrega)
    db.session.commit()
    actualizar_avance(inscripcion)
    flash('Actividad entregada correctamente.', 'success')
    return redirect(url_for('cursos.curso_detalle', curso_id=curso.id))


@bp_cursos.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_curso():
    form = CursoForm()
    if form.validate_on_submit():
        nuevo_curso = Curso(
            categoria_id=form.categoria.data,
            modalidad=form.modalidad.data,
            objetivo=form.objetivo.data,
            nombre=form.nombre.data,
            contenido=form.contenido.data,
            area_tematica=form.area_tematica.data,
            duracion=form.duracion.data,
            tipo_agente=form.tipo_agente.data,
            creador_id=current_user.id
        )
        db.session.add(nuevo_curso)
        db.session.commit()
        flash('Curso creado exitosamente', 'success')
        return redirect(url_for('cursos.index'))
    return render_template('cursos/crear.html', form=form)

