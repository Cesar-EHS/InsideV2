from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, send_from_directory
)
from flask_login import login_required, current_user
from app import db
from app.cursos.models import ( # Asegúrate de que Seccion esté importado
    ActividadDocumento, ActividadVideo, CategoriaCurso, Curso, ExamenRespuestaUsuario, Inscripcion, Examen, Pregunta, Seccion,
    ExamenResultado, Actividad, ActividadResultado, Archivo, ActividadExamen, PreguntaOpcion
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

#Diccionario con los tipos de pregunta.
TIPO_PREGUNTA_MAP = {
    'opcion_multiple': 1,
    'verdadero_falso': 2,
    'abierta': 3
}

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
        # titulo = request.form.get('titulo-video') or request.form.get('titulo-archivo') or "Examen de la sección"
        
        # Calcula el orden para la nueva actividad
        orden_actual_max = db.session.query(db.func.max(Actividad.orden)).filter_by(seccion_id=seccion.id).scalar() or 0
        
        # --- Creación del objeto Actividad paso a paso ---
        nueva_actividad = Actividad()
        nueva_actividad.fecha_creacion = datetime.now(mexico_tz)
        nueva_actividad.tipo_actividad = tipo_actividad
        nueva_actividad.seccion = seccion
        nueva_actividad.orden = orden_actual_max + 1

        if tipo_actividad == 'video':
            titulo = request.form.get('titulo-video')
            video_url = request.form.get('video-url')
            if not titulo or not video_url:
                raise ValueError("El título y la URL del video son obligatorios.")
            
            nueva_actividad.titulo = titulo
            
            # --- Creación del objeto ActividadVideo paso a paso ---
            actividad_video = ActividadVideo()
            actividad_video.titulo = titulo
            actividad_video.url = video_url
            
            # Conecta el video a la actividad principal
            nueva_actividad.videos.append(actividad_video)

        elif tipo_actividad == 'documento':
            titulo = request.form.get('titulo-archivo')
            archivo = request.files.get('archivo')
            if not archivo or not archivo or not archivo.filename:
                raise ValueError("El título y el archivo son obligatorios.")
            
            filename = secure_filename(archivo.filename)
            # Usa la misma lógica que en 'agregar_curso' para la ruta
            static_folder = current_app.static_folder or os.path.join(current_app.root_path, 'static')
            ruta_absoluta_base = os.path.join(static_folder, 'cursos', 'recursos_actividades')
            os.makedirs(ruta_absoluta_base, exist_ok=True)
            
            archivo.save(os.path.join(ruta_absoluta_base, filename))

            nueva_actividad.titulo = titulo
            
            # --- Creación del objeto ActividadDocumento paso a paso ---
            actividad_doc = ActividadDocumento()
            actividad_doc.nombre_documento = filename
            actividad_doc.ruta_documento = os.path.join('cursos', 'recursos_actividades', filename)

            # Conecta el documento a la actividad principal
            nueva_actividad.documentos.append(actividad_doc)
        
        elif tipo_actividad == 'examen':
            # Ya tengo todas las vistas jeje, solo falta el bakcend
            examen_id = request.form.get('examen_id')
            examen_titulo = request.form.get('titulo')
            if not examen_id or not examen_titulo:
                raise ValueError("Faltan datos para la actividad de tipo examen.")
            
            nueva_actividad.titulo = examen_titulo

            # Enlace entre Actividad y Examen
            enlace = ActividadExamen()
            enlace.examen_id = int(examen_id)
            nueva_actividad.examenes.append(enlace)

        else:
            raise ValueError(f"Tipo de actividad no válido: {tipo_actividad}")
        
        db.session.add(nueva_actividad)
        # Guardar todo en la base de datos de forma atómica
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
        db.session.rollback()
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

@bp_cursos.route('/actividad/<int:actividad_id>/realizar')
@login_required
def realizar_actividad(actividad_id):
    # Buscamos la actividad
    actividad = Actividad.query.get_or_404(actividad_id)
    curso = actividad.seccion.curso

    # Verificamos que la actividad sea un video
    video_url = None
    if actividad.tipo_actividad == 'video' and actividad.videos:
        # Obtenemos el unico video asociado a esta actividad
        video_url = actividad.videos[0].url
    else:
        abort(404, description="La actividad no es un video o no tiene video asociado.")

    # Renderizamos la plantilla, pasando todos los datos de actividad y curso.
    return render_template('cursos/realizar_actividad.html', actividad=actividad, curso=curso, video_url=video_url)
    


# ---------- EXÁMENES ----------

@bp_cursos.route('examenes/crear', methods=['POST'])
@login_required
def crear_examen_completo():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON.'}), 400
    
    try:
        # Convertimos los datos a la forma en que están en la DB
        duracion_str = data.get('duracion')
        duracion_int = int(duracion_str) if duracion_str and duracion_str.isdigit() else None
        print(f"Duración convertida: {duracion_int}")

        # Obtenemos el tipo de examen y lo convertimos a entero.
        tipo_examen = data.get('tipo_examen')
        tipo_examen_id_int = int(tipo_examen) if tipo_examen else None

        # Obtenemos fechas y las convertimos a objetos datetime
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_cierre_str = data.get('fecha_cierre')

        fecha_inicio_obj  = datetime.fromisoformat(fecha_inicio_str) if fecha_inicio_str else None
        fecha_cierre_obj  = datetime.fromisoformat(fecha_cierre_str) if fecha_cierre_str else None


        nuevo_examen = Examen()
        nuevo_examen.titulo = data.get('titulo')
        nuevo_examen.descripcion = data.get('descripcion')
        nuevo_examen.fecha_creacion = datetime.now(mexico_tz)
        nuevo_examen.fecha_inicio = fecha_inicio_obj
        nuevo_examen.fecha_cierre = fecha_cierre_obj
        nuevo_examen.duracion_minutos = duracion_int
        nuevo_examen.tipo_examen_id = tipo_examen_id_int
        
        db.session.add(nuevo_examen)
        db.session.flush() # Esto le pide a la DB un ID para nuevo_examen ANTES de continuar

        # Código para guardar las preguntas por tipo
        for pregunta_data in data.get('preguntas', []):
            tipo_pregunta_str = pregunta_data.get('tipo')
            tipo_pregunta_id = TIPO_PREGUNTA_MAP.get(tipo_pregunta_str)
            if not tipo_pregunta_id: continue # Tipo no válido, saltar

            nueva_pregunta = Pregunta()
            nueva_pregunta.texto = pregunta_data.get('texto')
            nueva_pregunta.tipo_pregunta_id = tipo_pregunta_id
            nueva_pregunta.examen_id = nuevo_examen.id
            
            db.session.add(nueva_pregunta)
            db.session.flush() # Esto le pide a la DB un ID para nueva_pregunta

            # Pasamos con las de opcion multilple
            if tipo_pregunta_str == 'opcion_multiple':
                for opcion_data in pregunta_data.get('opciones', []):
                    nueva_opcion = PreguntaOpcion()
                    nueva_opcion.texto = opcion_data.get('texto')
                    nueva_opcion.es_correcta = opcion_data.get('es_correcta', False)
                    nueva_opcion.pregunta_id = nueva_pregunta.id
                    db.session.add(nueva_opcion)
            
            elif tipo_pregunta_str == 'verdadero_falso':
                # Obtenemos la respuesta correcta que indicó quien creo el examen
                respuesta_correcta = pregunta_data.get('respuesta_correcta_vf')

                # Creamos las dos opciones de Verdadero y Falso en la DB
                opcion_verdadero = PreguntaOpcion()
                opcion_verdadero.texto = 'Verdadero'
                opcion_verdadero.es_correcta = (respuesta_correcta == 'verdadero')
                opcion_verdadero.pregunta_id = nueva_pregunta.id

                opcion_falso = PreguntaOpcion()
                opcion_falso.texto = 'Falso'
                opcion_falso.es_correcta = (respuesta_correcta == 'falso')
                opcion_falso.pregunta_id = nueva_pregunta.id

                # Las añadimos a la sesión para guardarlas
                db.session.add_all([opcion_verdadero, opcion_falso])

        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Examen creado con éxito.',
            'examen_id': nuevo_examen.id,
            'examen_titulo': nuevo_examen.titulo
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear examen: {e}")
        return jsonify({'status': 'error', 'message': 'Error interno al guardar el examen.'}), 500

@bp_cursos.route('/actividad/<int:actividad_id>/tomar_examen', methods=['GET'])
@login_required
def tomar_examen(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    enlace_examen = ActividadExamen.query.filter_by(actividad_id=actividad.id).first_or_404()
    examen = Examen.query.get_or_404(enlace_examen.examen_id)
    curso = actividad.seccion.curso

    # ===============================================================
    # 👇 AÑADE ESTA VERIFICACIÓN DE INSCRIPCIÓN 👇
    # ===============================================================
    # Verificamos la inscripción
    inscripcion = Inscripcion.query.filter_by(usuario_id=current_user.id, curso_id=curso.id).first()
    if not inscripcion:
        flash('No estás inscrito en este curso.', 'warning')
        return redirect(url_for('cursos.detalle_curso', curso_id=curso.id))

    # --- LÓGICA DE INTENTOS ---
    # 1. Contamos cuántos resultados ya existen para este usuario y este examen
    intentos_realizados = ExamenResultado.query.filter_by(
        inscripcion_id=inscripcion.id,
        examen_id=examen.id
    ).count()

    # 2. Comparamos con los intentos permitidos
    if intentos_realizados >= examen.intentos_permitidos:
        flash(f'Ya has utilizado todos tus {examen.intentos_permitidos} intentos para este examen.', 'danger')
        return redirect(url_for('cursos.ver_curso', curso_id=curso.id)) # Lo mandamos de vuelta al curso

    # 3. Pasamos el número de intento actual a la plantilla
    intento_actual = intentos_realizados + 1

    return render_template('cursos/tomar_examen.html', 
                           examen=examen, 
                           actividad=actividad, 
                           intento_actual=intento_actual)

@bp_cursos.route('/actividad/<int:actividad_id>/entregar_examen', methods=['POST'])
@login_required
def entregar_examen(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    examen = ActividadExamen.query.filter_by(actividad_id=actividad.id).first_or_404().examen
    inscripcion = Inscripcion.query.filter_by(usuario_id=current_user.id, curso_id=actividad.seccion.curso_id).first_or_404()
    
    # --- Lógica de Intentos ---
    intentos_previos = ExamenResultado.query.filter_by(
        inscripcion_id=inscripcion.id,
        examen_id=examen.id
    ).count()

    if intentos_previos >= examen.intentos_permitidos:
        flash('Ya has utilizado todos tus intentos para este examen.', 'danger')
        return redirect(url_for('cursos.ver_curso', curso_id=actividad.seccion.curso_id))

    # --- Procesamiento de Respuestas ---
    respuestas_form = request.form
    total_preguntas_calificables = 0
    respuestas_correctas = 0
    tiene_preguntas_abiertas = False

    # 1. Creamos el ExamenResultado para este intento
    nuevo_resultado_examen = ExamenResultado()
    nuevo_resultado_examen.inscripcion_id = inscripcion.id
    nuevo_resultado_examen.fecha_realizado = datetime.now(mexico_tz)
    nuevo_resultado_examen.examen_id = examen.id
    nuevo_resultado_examen.numero_intento=intentos_previos + 1
    
    db.session.add(nuevo_resultado_examen)
    db.session.flush()

    # 2. Guardamos y calificamos cada respuesta del usuario
    for pregunta in examen.preguntas:
        llave_form = f'pregunta-{pregunta.id}'
        respuesta_usuario_str = respuestas_form.get(llave_form)
        if not respuesta_usuario_str:
            continue

        respuesta = ExamenRespuestaUsuario()
        respuesta.examen_resultado_id=nuevo_resultado_examen.id
        respuesta.pregunta_id=pregunta.id
        
        # Calificación para opción multiple y v/f
        if pregunta.tipo_pregunta_id == 1 or pregunta.tipo_pregunta_id == 2: # Opción Múltiple
            total_preguntas_calificables += 1
            opcion_seleccionada = None # Inicializamos como None por seguridad
            try: #Intenamos buscar la opción que el usuario seleccionó
                opcion_id_int = int(respuesta_usuario_str)
                opcion_seleccionada = PreguntaOpcion.query.get(opcion_id_int)
                if opcion_seleccionada:
                    respuesta.pregunta_opcion_id = opcion_seleccionada.id
                    if opcion_seleccionada.es_correcta:
                        respuestas_correctas += 1
            except (ValueError, TypeError):
                pass
        
        elif pregunta.tipo_pregunta_id == 3: # Abierta
            tiene_preguntas_abiertas = True
            respuesta.respuesta_texto = respuesta_usuario_str
        
        db.session.add(respuesta)

    # 3. Calculamos la calificación y definimos el estado
    calificacion_final = 0.0
    if total_preguntas_calificables > 0:
        calificacion_final = (respuestas_correctas / total_preguntas_calificables) * 100
    
    nuevo_resultado_examen.calificacion = calificacion_final
    
    # 4. Creamos el ActividadResultado para marcar la actividad como completada
    nuevo_resultado_actividad = ActividadResultado()
    nuevo_resultado_actividad.inscripcion_id=inscripcion.id
    nuevo_resultado_actividad.actividad_id=actividad.id
    nuevo_resultado_actividad.entregado=True
    nuevo_resultado_actividad.fecha_entregado=datetime.now(mexico_tz)
    nuevo_resultado_actividad.calificacion=calificacion_final
    # Enlazamos con el resultado del examen específico
    nuevo_resultado_actividad.examen_resultado_id=nuevo_resultado_examen.id
    
    if tiene_preguntas_abiertas:
        nuevo_resultado_actividad.retroalimentacion = "Pendiente de revisión."
        # Podrías añadir un campo "status" a ActividadResultado también si quisieras
    
    db.session.add(nuevo_resultado_actividad)
    db.session.commit()

    flash('¡Examen entregado con éxito!', 'success')
    # Redirigimos al usuario a una página de resultados
    return redirect(url_for('cursos.ver_resultado', resultado_id=nuevo_resultado_examen.id))

@bp_cursos.route('/examenes/resultados/<int:resultado_id>')
@login_required
def ver_resultado(resultado_id):
    # BUscamos el resultado del examen mediante el id
    resultado = ExamenResultado.query.get_or_404(resultado_id)

    # Evidentemente solo el mismo ususario puede ver sus resultados
    if resultado.inscripcion.usuario_id != current_user.id:
        abort(403)
    
    # Facilitamos el proceso creando un diccionario de respuestas
    respuestas_dict = {r.pregunta_id: r for r in resultado.respuestas}

    return render_template('cursos/ver_resultados_examen.html', resultado=resultado, examen=resultado.examen, respuestas_dict=respuestas_dict)

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

@bp_cursos.route('/actividad/<int:actividad_id>/dashboard_examen')
@login_required
def dashboard_examen(actividad_id):
    # Extraemos la info de la actividad
    actividad = Actividad.query.get_or_404(actividad_id)

    # Por seguridad: solo el creador del curso puede ver el dashboard
    if actividad.seccion.curso.creador_id != current_user.id:
        abort(403)
    
    # FIltramos el examen
    examen = actividad.examenes[0].examen

    resultados = ExamenResultado.query.filter_by(examen_id=examen.id).order_by(ExamenResultado.fecha_realizado.desc()).all()

    # Contamos cuantas tienen la marca de Pendiente
    pendientes_revision = [r for r in resultados if r.actividad_resultado and r.actividad_resultado.retroalimentacion == "Pendiente de revisión."]

    # Calculo de estadisticas
    resultados_calificados = [r for r in resultados if not (r.actividad_resultado and r.actividad_resultado.retroalimentacion == "Pendiente de revisión.")]
    calificaciones = [r.calificacion for r in resultados_calificados if r.calificacion is not None]

    if calificaciones:
        promedio_final = round(sum(calificaciones) / len(calificaciones), 1)
    else:
        promedio_final = 0

    estadisticas = {
        'presentaron': len(resultados),
        'promedio': promedio_final,
        'pendientes': len(pendientes_revision)
    }

    return render_template('cursos/dashboard_examen.html', actividad=actividad, examen=examen, resultados=resultados, estadisticas=estadisticas)

@bp_cursos.route('/examenes/resultados/<int:resultado_id>/revisar', methods=['GET', 'POST'])
@login_required
def revisar_intento(resultado_id):
    resultado = ExamenResultado.query.get_or_404(resultado_id)
    curso = resultado.inscripcion.curso

    # Seguridad: solo el creador del curso puede calificar
    if curso.creador_id != current_user.id:
        abort(403)
    
    # Si el método es POST, el instructor está guardando la calificación
    if request.method == 'POST':
        calificacion_final = request.form.get('calificacion_final')
        retroalimentacion = request.form.get('retroalimentacion', '')

        if calificacion_final:
            # Actualizamos el resultado del examen
            resultado.calificacion = float(calificacion_final)
            resultado.status = 'completado'
            
            # Buscamos y actualizamos el resultado de la actividad asociado
            actividad_resultado = ActividadResultado.query.filter_by(examen_resultado_id=resultado.id).first()
            if actividad_resultado:
                actividad_resultado.calificacion = float(calificacion_final)
                actividad_resultado.retroalimentacion = retroalimentacion

            db.session.commit()
            flash('La calificación ha sido guardada con éxito.', 'success')
            # Redirigimos de vuelta al dashboard del examen
            return redirect(url_for('cursos.dashboard_examen', actividad_id=actividad_resultado.actividad_id))

    # Si es GET, simplemente mostramos la página de revisión
    respuestas_dict = {r.pregunta_id: r for r in resultado.respuestas}
    return render_template(
        'cursos/revisar_intento.html', 
        resultado=resultado,
        examen=resultado.examen,
        respuestas_dict=respuestas_dict
    )

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