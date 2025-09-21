// ==============================================
// FUNCIONES DE AYUDA (HELPERS)
// ==============================================

function showModalTab(tabId) {
    // Tu función para cambiar de pestaña. La dejamos como está.
    const datosTab = document.getElementById('modal-tab-datos');
    const actividadesTab = document.getElementById('modal-tab-actividades');
    const visualizarTab = document.getElementById('modal-tab-visualizar');
    const datosBtn = document.getElementById('tab-datos-btn');
    const actividadesBtn = document.getElementById('tab-actividades-btn');
    const visualizarBtn = document.getElementById('tab-visualizar-btn');
    
    datosTab.classList.add('hidden');
    actividadesTab.classList.add('hidden');
    visualizarTab.classList.add('hidden');
    
    const allButtons = [datosBtn, actividadesBtn, visualizarBtn];
    allButtons.forEach(btn => {
        btn.classList.remove('border-yellow-500', 'text-gray-800');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    let activeBtn;
    if (tabId === 'datos') {
        datosTab.classList.remove('hidden');
        activeBtn = datosBtn;
    } else if (tabId === 'actividades') {
        actividadesTab.classList.remove('hidden');
        activeBtn = actividadesBtn;
        if (typeof showActivityView === 'function') showActivityView('select');
    } else if (tabId === 'visualizar') {
        visualizarTab.classList.remove('hidden');
        activeBtn = visualizarBtn;
    }

    if (activeBtn) {
        activeBtn.classList.add('border-yellow-500', 'text-gray-800');
        activeBtn.classList.remove('border-transparent', 'text-gray-500');
    }
}

function getIconForActivityType(tipo) {
    // Tu función de íconos. La dejamos como está.
    const icons = {
        'video': '<span class="material-icons text-2xl text-blue-500">videocam</span>',
        'documento': '<span class="material-icons text-2xl text-yellow-600">attach_file</span>',
        'examen': '<span class="material-icons text-2xl text-purple-500">assignment</span>'
    };
    return icons[tipo] || '<span class="material-icons text-2xl text-gray-500">help_outline</span>';
}

// ==============================================
// LÓGICA PRINCIPAL (SE EJECUTA AL CARGAR LA PÁGINA)
// ==============================================

document.addEventListener('DOMContentLoaded', function () {
    const contenedorSecciones = document.getElementById('contenedor-secciones');
    const modalActividad = document.getElementById('modal-actividad');
    const cerrarModalBtn = document.getElementById('cerrar-modal-actividad');

    // --- Función para abrir y configurar el modal ---
    // La ponemos aquí adentro para que tenga acceso a todo lo demás.
    function abrirModalEdicion(id, nombre, descripcion, actividadesDataString) {
        const modalForm = modalActividad.querySelector('form');

        // Llenar datos de la sección
        modalForm.querySelector('input[name="nombre-seccion"]').value = nombre;
        modalForm.querySelector('textarea[name="descripcion-seccion"]').value = descripcion;

        // Actualizar URLs de los formularios
        const seccionId = id;
        const formArchivo = document.getElementById('form-archivo');
        if (formArchivo && formArchivo.dataset.actionTemplate) {
            const finalUrl = formArchivo.dataset.actionTemplate.replace('999999', seccionId);
            formArchivo.action = finalUrl;
        }
        // (Aquí la lógica para formVideo)

        // "Pintar" las actividades existentes
        const activitiesContainer = document.getElementById('activities-container');
        activitiesContainer.innerHTML = '';
        
        const actividadesData = JSON.parse(actividadesDataString);
        if (actividadesData && actividadesData.length > 0) {
            actividadesData.forEach(act => {
                const activityCardHTML = `
                    <div class="activity-card flex items-center justify-between p-4 bg-white rounded-xl shadow-md border border-gray-200 transition-all duration-200 cursor-pointer hover:shadow-xl hover:-translate-y-1 group" data-id="${act.id}">
                        <div class="flex items-center gap-4">
                            ${getIconForActivityType(act.tipo)}
                            <div>
                                <h4 class="font-bold text-base text-gray-800">${act.titulo}</h4>
                                <p class="text-xs text-gray-500">Tipo: ${act.tipo}</p>
                            </div>
                        </div>
                        <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button class="text-gray-600 hover:text-yellow-500 p-1" title="Editar"><span class="material-icons">edit</span></button>
                            <button class="text-gray-600 hover:text-red-500 p-1" title="Eliminar"><span class="material-icons">delete</span></button>
                        </div>
                    </div>`;
                activitiesContainer.insertAdjacentHTML('beforeend', activityCardHTML);
            });
        } else {
            activitiesContainer.innerHTML = '<p class="text-center text-gray-500">Esta sección aún no tiene actividades.</p>';
        }
        
        // Abrir el modal y mostrar la primera pestaña
        modalActividad.classList.remove('hidden');
        modalActividad.classList.add('flex');
        showModalTab('datos'); 
    }

    // --- Event Listeners ---
    if(cerrarModalBtn) {
        cerrarModalBtn.addEventListener('click', () => {
            modalActividad.classList.add('hidden');
            modalActividad.classList.remove('flex');
        });
    }
    
    if (contenedorSecciones) {
        contenedorSecciones.addEventListener('click', function(e) {
            const seccionCard = e.target.closest('.seccion-card');
            if (seccionCard) {
                // Obtenemos todos los datos, incluyendo las actividades
                const { seccionId, nombre, descripcion, actividades } = seccionCard.dataset;
                abrirModalEdicion(seccionId, nombre, descripcion, actividades);
            }
        });
    }
    
    const formArchivo = document.getElementById('form-archivo');
    if (formArchivo) {
        formArchivo.addEventListener('submit', function(event) {
            // Previene el envío normal para que no se recargue la página
            event.preventDefault(); 

            // Crea un objeto FormData para recolectar TODOS los campos del formulario
            const formData = new FormData(formArchivo);
            
            // Obtiene la URL de acción actualizada del atributo 'action' del form
            const url = formArchivo.action;

            // Usa fetch() para enviar los datos
            fetch(url, {
                method: 'POST',
                body: formData, // Envía el objeto FormData directamente
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // --- PASO 1: Creamos el nuevo elemento HTML en segundo plano ---

                    const activitiesContainer = document.getElementById('activities-container');
                    const nuevaActividad = data.actividad;

                    // Si existe un mensaje de "aún no tiene actividades", lo eliminamos
                    const emptyMessage = activitiesContainer.querySelector('p');
                    if (emptyMessage && emptyMessage.textContent.includes("aún no tiene actividades")) {
                        emptyMessage.remove();
                    }

                    // Creamos el HTML para la nueva "tarjeta" de actividad
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

                    // Insertamos la nueva tarjeta en el contenedor de visualización
                    activitiesContainer.insertAdjacentHTML('beforeend', activityCardHTML);

                    // --- PASO 2: Notificamos al usuario y cambiamos de pestaña ---

                    Swal.fire({
                        title: '¡Actividad Creada!',
                        text: data.message,
                        icon: 'success',
                        timer: 1500, // La alerta se cierra sola después de 1.5 segundos
                        showConfirmButton: false
                    }).then(() => {
                        // Esta función se ejecuta después de que se cierra la alerta
                        showModalTab('visualizar'); // Cambiamos a la pestaña deseada
                    });

                } else {
                    // Manejo de errores
                    Swal.fire({
                        title: 'Error',
                        text: data.message,
                        icon: 'error',
                        confirmButtonText: 'Entendido'
                    });
                }
            })
            .catch(error => {
                console.error('Error de red:', error);
                alert('Ocurrió un error de conexión. Inténtalo de nuevo.');
            });
        });
    }
});