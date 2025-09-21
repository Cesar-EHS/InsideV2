from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, send_from_directory
)
from flask_login import login_required, current_user
from app import db
from app.cursos.models import ( # Asegúrate de que Seccion esté importado
    ActividadDocumento, ActividadVideo, CategoriaCurso, Curso, Inscripcion, Examen, Pregunta, Seccion,
    ExamenResultado, Actividad, ActividadResultado, Archivo, TipoExamen
)
from app.cursos.forms import CursoForm, ExamenForm, PreguntaForm, ActividadForm
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import os, pytz
from flask import current_app
import json

bp_cursos = Blueprint('cursos', __name__, template_folder='templates', static_folder='static')

# Zona horaria de México
mexico_tz = pytz.timezone('America/Mexico_City')

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
    creados = request.args.get('creados')
    inactivos = request.args.get('inactivos')
    page = request.args.get('page', 1, type=int)
    
    #Verficar si el usuario es encargado de cursos
    es_encargado = current_user.puesto_trabajo_id in encargados

    query = Curso.query.filter_by(eliminado=0)

    if categoria_filtro:
        query = query.filter(Curso.categoria.has(CategoriaCurso.nombre == categoria_filtro))

    if creados and current_user.puesto_trabajo_id in encargados:
        query = query.filter(Curso.creador_id == current_user.id)

    if inactivos and current_user.puesto_trabajo_id in encargados:
        query = query.filter(Curso.estado == 'Inactivo', Curso.creador_id == current_user.id)
    
    #Cursos en los que el usuario ya está inscrito
    mis_cursos_inscrito = Curso.query.join(Inscripcion).filter(
        Inscripcion.usuario_id == current_user.id,
        Inscripcion.activo == True
    ).order_by(Curso.fecha_creacion.desc()).all()

    #Instancia del formulario para pasarla a la plantilla principal
    form_curso = CursoForm()

    catalogo_cursos = query.order_by(Curso.fecha_creacion.desc()).paginate(page=page, per_page=6)
    
    if es_encargado:
        mis_cursos_creados = Curso.query.filter_by(creador_id=current_user.id).order_by(Curso.fecha_creacion.desc()).paginate(page=page, per_page=6)
    else:
        mis_cursos_creados = None

    categorias = [
        'Protección Civil', 'Seguridad y Salud en el Trabajo', 'Soporte IT',
        'Protección del Medio Ambiente', 'Técnico EHSmart', 'Desarrollo Organizacional'
    ]

    print("Encargado:", es_encargado)

    return render_template('cursos/index.html',
                           mis_cursos_inscrito=mis_cursos_inscrito,
                           mis_cursos_creados=mis_cursos_creados,
                           catalogo_cursos=catalogo_cursos,
                           categorias=categorias, categoria_filtro=categoria_filtro,
                           es_encargado=es_encargado, form=form_curso,
                           creados=creados,
                           inactivos=inactivos)


@bp_cursos.route('/curso/<int:curso_id>')
@login_required
def curso_detalle(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    
    if curso.creador_id != current_user.id:
        #Nos traerá datos del curso que se seleccionó.
        curso = Curso.query.get_or_404(curso_id)

    return render_template('cursos/curso_detalle.html', curso=curso)


@bp_cursos.route('/agregar', methods=['GET','POST']) #Dejar solo POST (antes tambien tenia get)
@login_required
def agregar_curso():
    # Ajusta los puestos permitidos según tu lógica
    puestos_permitidos = [2, 5, 6, 7, 8, 23, 24]
    if current_user.puesto_trabajo_id not in puestos_permitidos:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Permiso denegado.'}), 403
        abort(403)
    
    form = CursoForm()
    if request.method == 'POST':
        print("\n--- DEBUG: Contenido de la solicitud ---")
    
        # 1. Imprimir todos los datos del formulario
        print("--- Form Data (request.form):")
        for key, value in request.form.items():
            print(f"  '{key}': '{value}'")
        
        # 2. Imprimir los archivos recibidos
        print("\n--- Files Data (request.files):")
        for key, file_storage in request.files.items():
            print(f"  '{key}': '{file_storage.filename}'")

        # 3. Imprimir el JSON completo de los datos del formulario (si lo envías por AJAX)
        # Esto es útil para ver la estructura de secciones[]
        try:
            data = request.json
            print("\n--- JSON Data (request.json):")
            if data:
                import json
                print(json.dumps(data, indent=2))
            else:
                print("  No JSON data.")
        except Exception:
            print("  No JSON data.")

        # Lógica para procesar el formulario cuando se envía
        if form.validate_on_submit():
            curso = Curso()
            curso.nombre = form.nombre.data
            curso.fecha_creacion = datetime.now(mexico_tz)
            curso.modalidad_id = form.modalidad.data.id
            curso.categoria_id = form.categoria.data.id
            curso.objetivo_id = form.objetivo.data.id
            curso.area_tematica_id = form.area_tematica.data.id
            curso.tipo_agente_id = form.tipo_agente.data.id
            curso.duracion = form.duracion.data
            curso.creador_id = current_user.id
            curso.video_url = form.video_url.data
            curso.eliminado = 0

            # Manejar la imagen principal
            imagen = request.files.get('imagen')
            if imagen and imagen.filename:
                filename = secure_filename(imagen.filename)
                # Define la ruta absoluta donde guardar la imagen
                static_folder = current_app.static_folder or os.path.join(current_app.root_path, 'static')
                abs_path = os.path.join(static_folder, 'cursos', 'img')

                #Crea el directorio si no existe
                os.makedirs(abs_path, exist_ok=True)
                imagen.save(os.path.join(abs_path, filename))
                curso.imagen = f'cursos/img/{filename}'
            else:
                curso.imagen = None

            try:
                db.session.add(curso)
                db.session.commit()  # Necesario para obtener el ID del curso
                print(f"--- DEBUG: Curso principal guardado con éxito. ID: {curso.id} ---")
            except Exception as e:
                print(f"--- ERROR: Falló al guardar el curso principal. Error: {e} ---")
                db.session.rollback() # Revierte cualquier cambio si hay un error
                # Si hay un error aquí, las secciones no se guardarán.
                return jsonify({'success': False, 'message': 'Error al guardar el curso principal.'}), 500

            # 2. Procesar y gaurdar los archivos adjuntos (recursos)
            archivos_guardados = 0
            print(f"--- DEBUG: Archivos procesados. Total guardados: {archivos_guardados} ---")

            # Definimos la ruat estatica de los recursos para asegurar que sea un string válido
            static_folder = current_app.static_folder or os.path.join(current_app.root_path, 'static')
            ruta_absoluta_base = os.path.join(static_folder, 'cursos', 'recursos')

            # creamos el directorio si es que aun no existe.
            os.makedirs(ruta_absoluta_base, exist_ok=True)

            for key in request.files:
                if key.startswith('archivo'):
                    archivo = request.files[key]
                    if archivo and archivo.filename:
                        filename = secure_filename(archivo.filename)

                        #Unimos las rutas seguras
                        ruta_relativa = os.path.join('cursos', 'recursos', filename)
                        ruta_absoluta = os.path.join(ruta_absoluta_base, 'cursos', 'recursos')
                        os.makedirs(ruta_absoluta, exist_ok=True)

                        # Guarda el archivo en la ruta absoluta
                        archivo.save(os.path.join(ruta_absoluta, filename))
                        nuevo_archivo = Archivo()
                        nuevo_archivo.nombre=filename
                        nuevo_archivo.ruta=ruta_relativa
                        nuevo_archivo.curso_id=curso.id
                        
                        db.session.add(nuevo_archivo)
                        archivos_guardados += 1

            # --- Guardar secciones ---
            secciones_data = {}
            for key in request.form:
                if key.startswith('secciones['):
                    try:
                        # Parsear 'secciones[0][nombre]' -> index=0, field='nombre'
                        parts = key.replace(']', '').split('[') # ['secciones', '0', 'nombre']
                        index = int(parts[1])
                        field = parts[2]
                        if index not in secciones_data:
                            secciones_data[index] = {}
                        secciones_data[index][field] = request.form[key]
                    except (IndexError, ValueError):
                        continue # Ignorar claves mal formadas
            
            secciones_guardadas = 0
            for index in sorted(secciones_data.keys()):
                data = secciones_data[index]
                if data.get('nombre'): # Solo guardar si tiene un nombre
                    seccion = Seccion()
                    seccion.curso_id=curso.id
                    seccion.nombre=data.get('nombre')
                    seccion.descripcion=data.get('descripcion', '')
                    seccion.orden = index
                    
                    db.session.add(seccion)
                    secciones_guardadas += 1
            try:
                db.session.commit() # Guardar las secciones
                print(f"--- DEBUG: Secciones guardadas con éxito. Total: {secciones_guardadas} ---")
            except Exception as e:
                print(f"--- ERROR: Falló al guardar las secciones. Error: {e} ---")
                db.session.rollback()
                return jsonify({'success': False, 'message': 'Error al guardar las secciones.'}), 500
            
            # Si todo fue exitoso, el código continuará aquí
            print("--- DEBUG: Proceso de guardado completado. ---")
            flash(f'Curso "{curso.nombre}" creado con {secciones_guardadas} sección(es) y {archivos_guardados} recurso(s).', 'success')
            return redirect(url_for('cursos.editar_curso', curso_id=curso.id))
        else:
            # Esto se ejecutará si form.validate_on_submit() devuelve False
            print("--- DEBUG: El formulario NO es válido. Mostrando errores de validación. ---")
            for field, errors in form.errors.items():
                print(f"--- ERROR de validación: Campo '{field}': {', '.join(errors)}")
            return render_template('cursos/agregar_curso.html', form=form)
        
    # Lógica para mostrar el formulario (cuando la solicitud es GET)
    return render_template('cursos/agregar_curso.html', form=form)


@bp_cursos.route('/eliminar/<int:curso_id>', methods=['DELETE'])
@login_required
def eliminar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    # Aquí antes probablemente hacías: db.session.delete(curso)
    # Cambia por soft delete, porque #prevenido
    curso.eliminado = 1
    db.session.commit()
    return jsonify({'success': True})

@bp_cursos.route('/curso/<int:curso_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if curso.creador_id != current_user.id:
        abort(403)  # Solo el creador puede editar

    #Creamos la instancia para el formulario del examen
    formExamen = ExamenForm()

    form = CursoForm(obj=curso)
    if form.validate_on_submit():
        curso.nombre = form.nombre.data
        curso.modalidad_id = form.modalidad.data.id
        curso.categoria_id = form.categoria.data.id
        curso.objetivo_id = form.objetivo.data.id
        curso.area_tematica_id = form.area_tematica.data.id
        curso.tipo_agente_id = form.tipo_agente.data.id
        curso.duracion = form.duracion.data
        curso.video_url = form.video_url.data

        # Solo si se sube una nueva imagen (no string)
        if form.imagen.data and hasattr(form.imagen.data, "filename") and form.imagen.data.filename:
            filename = secure_filename(form.imagen.data.filename)
            static_folder = current_app.static_folder
            if not static_folder:
                raise RuntimeError("La carpeta 'static_folder' no está configurada en Flask.")
            abs_path = os.path.join(static_folder, 'cursos', 'img')
            os.makedirs(abs_path, exist_ok=True)
            form.imagen.data.save(os.path.join(abs_path, filename))
            curso.imagen = f'cursos/img/{filename}'

        # Guardar archivos adjunto nuevos, NO LOS QUE YA ESTÁN
        nuevo_archivo = request.files.get('nuevo_archivo')
        
        if nuevo_archivo and nuevo_archivo.filename:
            filename = secure_filename(nuevo_archivo.filename)
            ruta_relativa = os.path.join('cursos', 'recursos', filename)
            ruta_absoluta = os.path.join(current_app.static_folder, 'cursos', 'recursos')
            os.makedirs(ruta_absoluta, exist_ok=True)
            nuevo_archivo.save(os.path.join(ruta_absoluta, filename))
            new_archivo = Archivo()
            new_archivo.nombre = filename
            new_archivo.ruta = ruta_relativa
            new_archivo.curso_id = curso.id
            db.session.add(new_archivo)

        db.session.commit()
        flash('Curso actualizado correctamente.', 'success')
        return redirect(url_for('cursos.editar_curso', curso_id=curso.id))
    
    # Para cada sección, creamos una lista de actividades en formato de diccionario
    # Esto se ejecuta solo en la petición GET, cuando se carga la página
    for seccion in curso.secciones:
        lista_de_dicts = [actividad.to_dict() for actividad in seccion.actividades]
        seccion.actividades_json_string = json.dumps(lista_de_dicts)

    return render_template('cursos/editar_curso.html', form=form, curso=curso, formExamen=formExamen)

@bp_cursos.route('/secciones/<int:seccion_id>/actividades/crear', methods=['POST'])
@login_required
def crear_actividad_en_seccion(seccion_id):
    seccion = Seccion.query.get_or_404(seccion_id)
    curso = seccion.curso

    if not seccion:
        return jsonify({'status': 'error', 'message': 'Sección no encontrada.'}), 404

    print("--- ✅ RUTA 'crear_actividad_en_seccion' ALCANZADA ---")
    
    # Solo el creador del curso puede añadir actividades
    if curso.creador_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'No tienes permiso para realizar esta acción.'}), 403
    
    print("Datos recibidos del formulario:", request.form)
    
    try:
        tipo_actividad = request.form.get('tipo_actividad')
        
        if not tipo_actividad:
            return jsonify({'status': 'error', 'message': 'No se especificó un tipo de actividad.'}), 400

        # El título se toma del campo específico del formulario que se envía
        titulo = request.form.get('titulo-video') or request.form.get('titulo-archivo') or "Examen de la sección"
        
        # Calcula el orden para la nueva actividad
        orden_actual_max = db.session.query(db.func.max(Actividad.orden)).filter_by(seccion_id=seccion.id).scalar() or 0
        
        # --- Creación del objeto Actividad paso a paso ---
        nueva_actividad = Actividad()
        nueva_actividad.titulo = titulo
        nueva_actividad.fecha_creacion = datetime.now(mexico_tz)
        nueva_actividad.tipo_actividad = tipo_actividad
        nueva_actividad.seccion = seccion
        nueva_actividad.orden = orden_actual_max + 1

        if tipo_actividad == 'video':
            video_url = request.form.get('video-url')
            if not video_url:
                raise ValueError("La URL del video es obligatoria.")
            
            # --- Creación del objeto ActividadVideo paso a paso ---
            actividad_video = ActividadVideo()
            actividad_video.url = video_url
            
            # Conecta el video a la actividad principal
            nueva_actividad.videos.append(actividad_video)

        elif tipo_actividad == 'documento':
            archivo = request.files.get('archivo')
            if not archivo or not archivo.filename:
                raise ValueError("Debe seleccionar un archivo.")
            
            filename = secure_filename(archivo.filename)
            # Usa la misma lógica que en 'agregar_curso' para la ruta
            static_folder = current_app.static_folder or os.path.join(current_app.root_path, 'static')
            ruta_absoluta_base = os.path.join(static_folder, 'cursos', 'recursos_actividades')
            os.makedirs(ruta_absoluta_base, exist_ok=True)
            
            archivo.save(os.path.join(ruta_absoluta_base, filename))
            
            # --- Creación del objeto ActividadDocumento paso a paso ---
            actividad_doc = ActividadDocumento()
            actividad_doc.nombre_documento = filename
            actividad_doc.ruta_documento = os.path.join('cursos', 'recursos_actividades', filename)

            # Conecta el documento a la actividad principal
            nueva_actividad.documentos.append(actividad_doc)
        
        elif tipo_actividad == 'examen':
            # Aquí necesitarías lógica para seleccionar un examen existente
            # o crear uno nuevo. Por ahora, lo dejamos pendiente.
            # examen_id = request.form.get('examen_id')
            # ...
            raise ValueError('La creación de exámenes aún no está implementada.')

        else:
            raise ValueError(f"Tipo de actividad no válido: {tipo_actividad}")

        # Guardar todo en la base de datos de forma atómica
        db.session.add(nueva_actividad)
        db.session.commit()
        # Respuesta de éxito: devolvemos la actividad creada
        return jsonify({
            'status': 'success',
            'message': 'Actividad creada con éxito.',
            'actividad': {
                'id': nueva_actividad.id,
                'titulo': nueva_actividad.titulo,
                'tipo': nueva_actividad.tipo_actividad,
                'orden': nueva_actividad.orden
            }
        })
    
    except ValueError as ve:
        # Errores de validación (datos faltantes)
        return jsonify({'status': 'error', 'message': str(ve)}), 400

    except Exception as e:
        # Otros errores (base de datos, etc.)
        db.session.rollback()
        # Para depuración, es útil imprimir el error real en la consola del servidor
        print(f"Error interno al crear actividad: {e}") 
        return jsonify({'status': 'error', 'message': 'Ocurrió un error interno al guardar la actividad.'}), 500

@bp_cursos.route('/recursos/view/<path:filepath>')
@login_required
def ver_recurso(filepath):
    # Define la carpeta donde están guardados los archivos de las actividades
    # ¡Asegúrate de que esta ruta sea correcta para tu proyecto!
    static_folder = current_app.static_folder or os.path.join(current_app.root_path, 'static')
    directory = os.path.join(static_folder, 'cursos', 'recursos_actividades')
    
    # send_from_directory sirve el archivo de forma segura para evitar que
    # los usuarios accedan a otros directorios del sistema.
    return send_from_directory(directory, filepath)


@bp_cursos.route('/inscribirse/<int:curso_id>', methods=['POST'])
@login_required
def inscribirse(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    inscripcion = Inscripcion.query.filter_by(
        usuario_id=current_user.id,
        curso_id=curso.id,
        activo=True
    ).first()
    # Si ya está inscrito, se debe ir a curso.inscrito
    if inscripcion:
        redirect_url = url_for('cursos.curso_inscrito', curso_id=curso.id)
        return jsonify({
            'status': 'info',
            'message': 'Ya estabas inscrito en este curso.',
            'redirect_url': redirect_url
        })
    
    #Si no esta inscrito se debe hacer una nueva inscripcion
    try:
        nueva_inscripcion = Inscripcion()
        nueva_inscripcion.usuario_id = current_user.id
        nueva_inscripcion.curso_id = curso.id
        nueva_inscripcion.avance = 0.0
        nueva_inscripcion.activo = True
        db.session.add(nueva_inscripcion)
        db.session.commit()
        # Se dirige a la página del curso inscrito
        redirect_url = url_for('cursos.curso_inscrito', curso_id=curso.id)

        return jsonify({
            'status': 'success',
            'message': f'Te has inscrito al curso "{curso.nombre}".',
            'redirect_url': redirect_url
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error al inscribirse: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Hubo un error al procesar tu inscripción.'
        }), 500
    


@bp_cursos.route('/mis-cursos/<int:curso_id>')
def curso_inscrito(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    inscripcion = Inscripcion.query.filter_by(usuario_id=current_user.id, curso_id=curso_id).first()
    avance = inscripcion.avance if inscripcion else 0.0
    mexico_tz = pytz.timezone('America/Mexico_City')
    # Actualizar la fecha del utlimo acceso
    if inscripcion:
        inscripcion.fecha_ultimo_acceso = datetime.now(mexico_tz)
        db.session.commit()
    # Formatear la hora para que salga bien
    fecha_ultimo_acceso_formateada = None
    if inscripcion and inscripcion.fecha_ultimo_acceso:
        fecha_ultimo_acceso_formateada = inscripcion.fecha_ultimo_acceso.strftime('%H:%M:%S')
    return render_template('cursos/curso_inscrito.html', curso=curso, avance=avance, fecha_utlimo_acceso=fecha_ultimo_acceso_formateada)

""" Al dar clic en el curso inscrito, te lleva a ver el desglose del curso:"""
@bp_cursos.route('/curso/<int:curso_id>/desglose')
def desglose_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    inscripcion = Inscripcion.query.filter_by(usuario_id=current_user.id, curso_id=curso_id).first()
    if not inscripcion:
        flash('No estás inscrito en este curso.', 'warning')
        return redirect(url_for('cursos.index'))
    examenes = curso.examenes
    actividades = curso.actividades
    return render_template('cursos/desglose_curso.html', curso=curso, inscripcion=inscripcion, examenes=examenes, actividades=actividades)

@bp_cursos.route('/curso/<int:curso_id>/avance', methods=['POST'])
@login_required
def avance(curso_id):
    data = request.get_json()
    avance = data.get('avance')
    inscripcion = Inscripcion.query.filter_by(
        usuario_id = current_user.id,
        curso_id = curso_id,
        activo = True
    ).first_or_404()
    inscripcion.avance = float(avance)
    db.session.commit()
    return jsonify({'success': True, 'avance': inscripcion.avance})


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

    formExamen = ExamenForm()
    if formExamen.validate_on_submit():
        examen = Examen()
        examen.curso_id=curso.id,
        examen.titulo=formExamen.titulo.data,
        examen.descripcion=formExamen.descripcion.data
        examen.duracion_minutos=formExamen.duracion.data
        examen.fecha_inicio=formExamen.fecha_inicio.data
        examen.fecha_cierre=formExamen.fecha_cierre.data

        db.session.add(examen)
        db.session.commit()
        flash('Examen agregado correctamente.', 'success')
        return redirect(url_for('cursos.examenes_curso', curso_id=curso.id))

    return render_template('cursos/agregar_examen.html', formExamen=formExamen, curso=curso)


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
        pregunta = Pregunta()
        examen_id=examen.id
        texto=form.texto.data
        tipo=form.tipo.data
        opciones=form.opciones.data if form.tipo.data == 'opcion_multiple' else None
        respuesta_correcta=form.respuesta_correcta.data
        
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
        actividad = Actividad()
        curso_id=curso.id
        titulo=form.titulo.data
        descripcion=form.descripcion.data
        
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