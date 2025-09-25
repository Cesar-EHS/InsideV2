// Este evento se asegura de que todo el código se ejecute solo después de que la página HTML se haya cargado por completo.
document.addEventListener('DOMContentLoaded', function () {

    // =================================================================
    // SECCIÓN 1: REFERENCIAS A ELEMENTOS IMPORTANTES DEL HTML
    // =================================================================
    const addExamBtn = document.getElementById('btn-examen');
    const modalExamen = document.getElementById('modal-examen');
    const datosTabBtn = document.getElementById('tab-datos-btn');
    const preguntasTabBtn = document.getElementById('tab-preguntas-btn');
    const datosTab = document.getElementById('tab-datos-examen');
    const preguntasTab = document.getElementById('tab-preguntas-examen');
    const preguntasContainer = document.getElementById('preguntas-container');
    const btnOpcionMultiple = document.getElementById('btn-opcion-multiple');
    const btnVerdaderoFalso = document.getElementById('btn-verdadero-falso');
    const btnAbierta = document.getElementById('btn-abierta');
    const btnGuardarExamen = document.getElementById('btn-guardar-examen');
    const formDatosExamen = document.getElementById('formNuevoExamen');


    // =================================================================
    // SECCIÓN 2: FUNCIONES PARA MANEJAR LA INTERFAZ (UI)
    // =================================================================

    /**
     * Muestra la pestaña seleccionada ('datos' o 'preguntas') y oculta la otra.
     * @param {string} tabId - El ID de la pestaña a mostrar.
     */
    window.showTabExamen = function(tabId) {
        if (!datosTab || !preguntasTab) return;

        if (tabId === 'datos') {
            datosTab.classList.remove('hidden');
            preguntasTab.classList.add('hidden');
            datosTabBtn.classList.add('border-yellow-400');
            datosTabBtn.classList.remove('border-transparent');
            preguntasTabBtn.classList.remove('border-yellow-400');
        } else if (tabId === 'preguntas') {
            datosTab.classList.add('hidden');
            preguntasTab.classList.remove('hidden');
            datosTabBtn.classList.remove('border-yellow-400');
            preguntasTabBtn.classList.add('border-yellow-400');
        }
    };

    /**
     * Cierra el modal de creación de examen.
     */
    window.closeModalExamen = function () {
        if (modalExamen) {
            modalExamen.classList.add('hidden');

        if (typeof showActivityView === 'function') {
            showActivityView('select');
    }
        }
    };
    
    /**
     * Recorre todas las preguntas y actualiza su número (ej. 1., 2., 3., ...).
     */
    function renumerarPreguntas() {
        if (!preguntasContainer) return;
        const numeros = preguntasContainer.querySelectorAll('.numero-pregunta');
        numeros.forEach((span, idx) => {
            span.textContent = `${idx + 1}.`;
        });
    }

    // =================================================================
    // SECCIÓN 3: EVENT LISTENERS PARA INTERACCIÓN DEL USUARIO
    // =================================================================

    // --- Listener para ABRIR el modal de creación de examen ---
    if (addExamBtn) {
        addExamBtn.addEventListener('click', function() {
            // Solo abrimos el modal del examen. El de actividades se queda abajo abierto.
            if (modalExamen) {
                modalExamen.classList.remove('hidden');
                if(window.showTabExamen) window.showTabExamen('datos');
            }
        });
    }

    // --- Listener central para CREAR y BORRAR preguntas y opciones ---
    if(preguntasContainer) {
        preguntasContainer.addEventListener('click', function(e) {
            const target = e.target;
            const btnAgregarOpcion = target.closest('.btn-agregar-opcion');
            const btnBorrarOpcion = target.closest('.btn-borrar-opcion');
            const btnBorrarPregunta = target.closest('.btn-borrar-pregunta');

            if (btnAgregarOpcion) {
                const opcionesContainer = btnAgregarOpcion.previousElementSibling;
                const idPregunta = btnAgregarOpcion.dataset.preguntaId;
                const nuevaOpcionHTML = `
                    <div class="flex items-center gap-2 opcion-item">
                        <input type="radio" name="correcta-${idPregunta}" class="form-radio text-yellow-500 focus:ring-yellow-500">
                        <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2" placeholder="Texto de la opción">
                        <button type="button" class="text-red-500 hover:text-red-700 btn-borrar-opcion" title="Eliminar opción"><span class="material-icons">delete</span></button>
                    </div>`;
                opcionesContainer.insertAdjacentHTML('beforeend', nuevaOpcionHTML);
            }
            
            if (btnBorrarOpcion) {
                btnBorrarOpcion.closest('.opcion-item').remove();
            }

            if (btnBorrarPregunta) {
                btnBorrarPregunta.closest('.bg-gray-200').remove();
                renumerarPreguntas();
            }
        });
    }
    
    // --- Listeners para AÑADIR nuevos tipos de pregunta ---
    if (btnOpcionMultiple) {
        btnOpcionMultiple.addEventListener('click', function () {
            const idPregunta = Date.now();
            const preguntaHTML = `
                <div class="bg-gray-200 rounded-xl p-6 mb-6 shadow flex flex-col gap-4">
                    <div class="flex justify-between items-center">
                        <span class="numero-pregunta font-bold text-lg"></span>
                        <button title="Eliminar pregunta" class="btn-borrar-pregunta text-red-500 hover:text-red-700"><span class="material-icons">delete</span></button>
                    </div>
                    <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2 font-bold" placeholder="Escribe aquí la pregunta de opción múltiple">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 opciones-container"></div>
                    <button type="button" class="text-blue-600 font-semibold mt-2 btn-agregar-opcion self-start" data-pregunta-id="${idPregunta}">+ Agregar opción</button>
                </div>`;
            preguntasContainer.insertAdjacentHTML('beforeend', preguntaHTML);
            renumerarPreguntas();
        });
    }

    if (btnVerdaderoFalso) {
        btnVerdaderoFalso.addEventListener('click', function () {
            const preguntaHTML = `
                <div class="bg-gray-200 rounded-xl p-6 mb-6 shadow flex flex-col gap-4">
                    <div class="flex justify-between items-center">
                        <span class="numero-pregunta font-bold text-lg"></span>
                        <button title="Eliminar pregunta" class="btn-borrar-pregunta text-red-500 hover:text-red-700"><span class="material-icons">delete</span></button>
                    </div>
                    <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2 font-bold" placeholder="Escribe aquí la afirmación (verdadero/falso)">
                    <div class="flex flex-col gap-2">
                        <label class="flex items-center gap-2"><input type="radio" name="vf-${Date.now()}" class="form-radio text-yellow-500"><span>Verdadero</span></label>
                        <label class="flex items-center gap-2"><input type="radio" name="vf-${Date.now()}" class="form-radio text-yellow-500"><span>Falso</span></label>
                    </div>
                </div>`;
            preguntasContainer.insertAdjacentHTML('beforeend', preguntaHTML);
            renumerarPreguntas();
        });
    }

    if (btnAbierta) {
        btnAbierta.addEventListener('click', function () {
            const preguntaHTML = `
                <div class="bg-gray-200 rounded-xl p-6 mb-6 shadow flex flex-col gap-4">
                    <div class="flex justify-between items-center">
                        <span class="numero-pregunta font-bold text-lg"></span>
                        <button title="Eliminar pregunta" class="btn-borrar-pregunta text-red-500 hover:text-red-700"><span class="material-icons">delete</span></button>
                    </div>
                    <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2 font-bold" placeholder="Escribe aquí la pregunta abierta">
                    <textarea class="w-full border border-gray-300 rounded px-3 py-2 bg-gray-100" placeholder="El alumno escribirá su respuesta aquí..." disabled></textarea>
                </div>`;
            preguntasContainer.insertAdjacentHTML('beforeend', preguntaHTML);
            renumerarPreguntas();
        });
    }


    // =================================================================
    // SECCIÓN 4: LÓGICA PARA RECOLECTAR Y ENVIAR LOS DATOS AL BACKEND
    // =================================================================
    
    function recolectarPreguntas() {
        const preguntas = [];
        const preguntaBlocks = document.querySelectorAll('#preguntas-container > .bg-gray-200');
        
        preguntaBlocks.forEach(block => {
            let tipo = '';
            if (block.querySelector('.opciones-container')) tipo = 'opcion_multiple';
            else if (block.querySelector('input[type="radio"]')) tipo = 'verdadero_falso';
            else if (block.querySelector('textarea')) tipo = 'abierta';

            const texto = block.querySelector('input[type="text"].font-bold')?.value || '';
            const obligatoria = false; // Tu HTML no tenía el checkbox de "obligatoria", lo puedes añadir si quieres.
            
            let preguntaObjeto = {
                texto: texto,
                tipo: tipo,
                obligatoria: obligatoria,
                opciones: [] // Inicializamos opciones como un array vacío
            };
            if (tipo === 'opcion_multiple') {
                const opcionItems = block.querySelectorAll('.opciones-container .opcion-item');
                opcionItems.forEach(item => {
                    const esCorrectaRadio = item.querySelector('input[type="radio"]');
                    const textoOpcionInput = item.querySelector('input[type="text"]');
                    preguntaObjeto.opciones.push({
                        texto: textoOpcionInput ? textoOpcionInput.value : '',
                        es_correcta: esCorrectaRadio ? esCorrectaRadio.checked : false 
                    });
                });
            }
            else if (tipo === 'verdadero_falso') {
                // 1. Buscamos el radio button que está seleccionado por el creador (respuesta correcta)
                const respuestaCorrectaInput = block.querySelector('input[type="radio"]:checked');
                if (respuestaCorrectaInput) {
                    preguntaObjeto.respuesta_correcta_vf = respuestaCorrectaInput.value;
                }
            }
            preguntas.push(preguntaObjeto);
        });
        return preguntas;
    }

    function enviarFormularioExamen() {
        // 1. Recolectamos los datos del formulario y las preguntas
        const formDataExamen = new FormData(formDatosExamen);
        
        // 2. Obtenemos las preguntas
        const preguntas = recolectarPreguntas();
        
        // 3. Construimos el objeto en formato de JSON que se enviará al backend
        const examenData = {
            titulo: formDataExamen.get('titulo'),
            descripcion: formDataExamen.get('descripcion'),
            tipo_examen: formDataExamen.get('tipo_examen'),
            duracion: formDataExamen.get('duracion'),
            preguntas: preguntas
        };

        console.log("--- 📦 Datos del Examen a Enviar ---");
        console.log(examenData);
        console.log("JSON que se enviará:", JSON.stringify(examenData, null, 2));

        // 4. Inicia el PRIMER fetch para crear el examen en la base de datos
        fetch('/cursos/examenes/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formDataExamen.get('csrf_token')
            },
            body: JSON.stringify(examenData)
        })
        .then(response => response.json())
        .then(dataExamen => {
            if (dataExamen.status === 'success') {
                // 5. Si el examen se creó, inicia el SEGUNDO fetch para crear la actividad
                console.log("Examen guardado:", dataExamen);
                // SEGUNDO FETCH: Crear la actividad vinculada al examen
                const seccionId = document.getElementById('form-archivo').action.split('/').slice(-3, -2)[0];
                const urlActividad = `/cursos/secciones/${seccionId}/actividades/crear`;

                const formDataActividad = new FormData();
                formDataActividad.append('tipo_actividad', 'examen');
                formDataActividad.append('examen_id', dataExamen.examen_id);
                formDataActividad.append('titulo', dataExamen.examen_titulo);
                formDataActividad.append('csrf_token', formDataExamen.get('csrf_token'));

                return fetch(urlActividad, { method: 'POST', body: formDataActividad });
            } else {
                throw new Error(dataExamen.message || 'Error al guardar el examen.');
            }
        })
        .then(response => response.json())
        .then(dataActividad => {
            if (dataActividad.status === 'success') {
                // 6. Si todo fue exitoso, actualiza la interfaz
                console.log("Actividad creada:", dataActividad);
                const nuevaActividad = dataActividad.actividad;

                // Añadimos la nueva actividad al dom
                const activitiesContainer = document.getElementById('activities-container');
                const emptyMessage = activitiesContainer.querySelector('p');
                if (emptyMessage) emptyMessage.remove();

                const activityCardHTML = `
                    <div class="activity-card flex items-center justify-between p-4 bg-white rounded-xl shadow-md border border-gray-200" data-id="${nuevaActividad.id}">
                        <div class="flex items-center gap-4">
                            ${getIconForActivityType(nuevaActividad.tipo)} 
                            <div>
                                <h4 class="font-bold text-base text-gray-800">${nuevaActividad.titulo}</h4>
                                <p class="text-xs text-gray-500">Tipo: ${nuevaActividad.tipo}</p>
                            </div>
                        </div>
                        <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button class="text-gray-600 hover:text-yellow-500 p-1" title="Editar"><span class="material-icons">edit</span></button>
                            <button class="text-gray-600 hover:text-red-500 p-1" title="Eliminar"><span class="material-icons">delete</span></button>
                        </div>
                    </div>`;
                activitiesContainer.insertAdjacentHTML('beforeend', activityCardHTML);

                // Mostramos la notificación de éxito
                Swal.fire({
                    title: '¡Éxito!',
                    text: 'El examen ha sido añadido a la sección.',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    // 3. Cuando la alerta se cierra, ejecutamos las acciones finales:
                    
                    // a) Cerramos el modal del examen (el de encima)
                    closeModalExamen(); 
                    
                    // b) Cambiamos a la pestaña "Visualizar" en el modal de actividades (el de abajo)
                    showModalTab('visualizar'); 
                });

            } else {
                throw new Error(dataActividad.message || 'Error al crear la actividad.');
            }
        })
        .catch(error => {
            console.error('Error en el proceso:', error);
            Swal.fire({ title: '¡Oops!', text: error.message, icon: 'error' });
        });
    }

    // --- Conexión del botón de guardar a la función principal ---
    if (btnGuardarExamen) {
        btnGuardarExamen.addEventListener('click', enviarFormularioExamen);
    }
});