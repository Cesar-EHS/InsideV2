// JavaScript para helpdesk.html - Sistema de tickets con modales

// Variables globales
let ticketActual = null;
let evidenciaCount = 1;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('Helpdesk JS cargado');
    configurarEventListeners();
});

// ====== CONFIGURACIÓN DE EVENTOS ======
function configurarEventListeners() {
    // Event listeners para cerrar modales al hacer clic fuera
    window.addEventListener('click', function(event) {
        const modalVer = document.getElementById('modal-ver-ticket');
        const modalEditar = document.getElementById('modal-editar-ticket');
        
        if (event.target === modalVer) {
            modalVer.classList.add('hidden');
        }
        if (event.target === modalEditar) {
            modalEditar.classList.add('hidden');
        }
    });

    // Event listener para escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            cerrarModales();
        }
    });
}

// ====== FUNCIONES DE MODAL ======
function verTicket(ticketId) {
    console.log('Abriendo modal para ver ticket:', ticketId);
    ticketActual = ticketId;
    
    // Mostrar el modal primero
    const modal = document.getElementById('modal-ver-ticket');
    modal.classList.remove('hidden');
    
    // Llamar a la función que popula los datos
    if (window.poblarModalVerTicket) {
        window.poblarModalVerTicket(ticketId);
    } else {
        console.error('Función poblarModalVerTicket no disponible');
    }
}

function editarTicket(ticketId) {
    console.log('Abriendo modal para editar ticket:', ticketId);
    ticketActual = ticketId;
    
    // Mostrar loading en el modal
    const modal = document.getElementById('modal-editar-ticket');
    const contenido = document.getElementById('modal-editar-content');
    
    modal.classList.remove('hidden');
    contenido.innerHTML = `
        <div class="flex items-center justify-center p-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-2">Cargando...</span>
        </div>
    `;
    
    // Cargar contenido via AJAX
    fetch(`/tickets/editar/${ticketId}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        contenido.innerHTML = html;
        // Configurar eventos específicos del modal de editar
        configurarEventosModalEditar(ticketId);
        // Reset contador de evidencias
        evidenciaCount = 1;
    })
    .catch(error => {
        console.error('Error al cargar formulario de edición:', error);
        contenido.innerHTML = `
            <div class="text-center p-8">
                <div class="text-red-600 mb-2">
                    <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </div>
                <p class="text-gray-600">Error al cargar el formulario</p>
                <button onclick="cerrarModales()" class="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                    Cerrar
                </button>
            </div>
        `;
    });
}

function cerrarModales() {
    const modalVer = document.getElementById('modal-ver-ticket');
    const modalEditar = document.getElementById('modal-editar-ticket');
    
    if (modalVer) modalVer.classList.add('hidden');
    if (modalEditar) modalEditar.classList.add('hidden');
    
    ticketActual = null;
}

// ====== EVENTOS ESPECÍFICOS DE MODALES ======
function configurarEventosModalVer(ticketId) {
    // Configurar formulario de comentarios
    const formComentario = document.getElementById(`form-comentario-${ticketId}`);
    if (formComentario) {
        formComentario.addEventListener('submit', function(e) {
            e.preventDefault();
            agregarComentario(ticketId);
        });
    }
    
    // Configurar cambio de estado (solo administradores)
    const selectEstado = document.getElementById(`estado-${ticketId}`);
    if (selectEstado) {
        selectEstado.addEventListener('change', function() {
            cambiarEstadoTicket(ticketId, this.value);
        });
    }
}

function configurarEventosModalEditar(ticketId) {
    // Configurar formulario de edición
    const formEditar = document.getElementById(`form-editar-ticket-${ticketId}`);
    if (formEditar) {
        formEditar.addEventListener('submit', function(e) {
            e.preventDefault();
            guardarCambiosTicket(ticketId);
        });
    }
}

// ====== GESTIÓN DE COMENTARIOS ======
async function agregarComentario(ticketId) {
    const textarea = document.getElementById(`comentario-${ticketId}`);
    const fileInput = document.getElementById(`imagen-comentario-${ticketId}`);
    
    if (!textarea || !textarea.value.trim()) {
        mostrarMensaje('Por favor escribe un comentario', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('comentario', textarea.value.trim());
    
    if (fileInput && fileInput.files[0]) {
        formData.append('imagen', fileInput.files[0]);
    }
    
    // Agregar CSRF token
    formData.append('csrf_token', window.csrfToken);
    
    try {
        const response = await fetch(`/tickets/comentar/${ticketId}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success || response.ok) {
            // Limpiar formulario
            textarea.value = '';
            if (fileInput) fileInput.value = '';
            
            // Recargar el modal para mostrar el nuevo comentario
            verTicket(ticketId);
            
            mostrarMensaje('Comentario agregado correctamente', 'success');
        } else {
            mostrarMensaje(data.error || 'Error al agregar comentario', 'error');
        }
    } catch (error) {
        console.error('Error al agregar comentario:', error);
        mostrarMensaje('Error de conexión', 'error');
    }
}

// ====== GESTIÓN DE ESTADO ======
async function cambiarEstadoTicket(ticketId, nuevoEstado) {
    if (!nuevoEstado) return;
    
    const formData = new FormData();
    formData.append('estado', nuevoEstado);
    formData.append('csrf_token', window.csrfToken);
    
    try {
        const response = await fetch(`/tickets/cambiar-estado/${ticketId}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje(data.message, 'success');
            // Recargar el modal para mostrar el cambio
            verTicket(ticketId);
            // También recargar la página para actualizar la lista
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            mostrarMensaje(data.error || 'Error al cambiar estado', 'error');
        }
    } catch (error) {
        console.error('Error al cambiar estado:', error);
        mostrarMensaje('Error de conexión', 'error');
    }
}

// ====== GESTIÓN DE EDICIÓN ======
async function guardarCambiosTicket(ticketId) {
    const form = document.getElementById(`form-editar-ticket-${ticketId}`);
    if (!form) return;
    
    const formData = new FormData(form);
    
    try {
        const response = await fetch(`/tickets/actualizar/${ticketId}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje('Ticket actualizado correctamente', 'success');
            cerrarModales();
            // Recargar la página para mostrar los cambios
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            mostrarMensaje(data.error || 'Error al actualizar ticket', 'error');
        }
    } catch (error) {
        console.error('Error al guardar cambios:', error);
        mostrarMensaje('Error de conexión', 'error');
    }
}

// ====== OTRAS FUNCIONES ======
async function reportarTicket(ticketId) {
    if (!confirm('¿Estás seguro de que quieres reportar este ticket?')) {
        return;
    }
    
    try {
        const response = await fetch(`/tickets/reportar/${ticketId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje('Ticket reportado correctamente', 'success');
            // Recargar la página para actualizar el estado
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            mostrarMensaje(data.error || 'Error al reportar ticket', 'error');
        }
    } catch (error) {
        console.error('Error al reportar ticket:', error);
        mostrarMensaje('Error de conexión', 'error');
    }
}

async function archivarTicket(ticketId) {
    if (!confirm('¿Estás seguro de que quieres archivar este ticket?')) {
        return;
    }
    
    try {
        const response = await fetch(`/tickets/archivar/${ticketId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje('Ticket archivado correctamente', 'success');
            // Recargar la página para actualizar la lista
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            mostrarMensaje(data.error || 'Error al archivar ticket', 'error');
        }
    } catch (error) {
        console.error('Error al archivar ticket:', error);
        mostrarMensaje('Error de conexión', 'error');
    }
}

// ====== UTILIDADES ======
function mostrarMensaje(mensaje, tipo = 'info') {
    // Crear elemento de mensaje
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm ${
        tipo === 'success' ? 'bg-green-100 border border-green-400 text-green-700' :
        tipo === 'error' ? 'bg-red-100 border border-red-400 text-red-700' :
        'bg-blue-100 border border-blue-400 text-blue-700'
    }`;
    
    messageDiv.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${mensaje}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-lg">&times;</button>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(messageDiv);
    
    // Eliminar automáticamente después de 5 segundos
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, 5000);
}

// Función para agregar evidencias en el modal de edición (se llama desde el template)
function agregarEvidenciaEdit(ticketId) {
    if (evidenciaCount < 3) {
        evidenciaCount++;
        const container = document.getElementById(`evidencia-edit-container-${ticketId}`);
        if (!container) return;
        
        const div = document.createElement('div');
        div.className = 'evidencia-edit-item mb-4';
        div.innerHTML = `
            <div class="flex items-center gap-2">
                <input type="file" name="nueva_evidencia_${evidenciaCount}" accept="image/*,.pdf,.doc,.docx,.txt" 
                       class="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <button type="button" onclick="this.parentElement.parentElement.remove(); evidenciaCount--;" class="text-red-600 hover:text-red-800">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        `;
        container.appendChild(div);
        
        const btnAgregar = document.getElementById(`btn-agregar-evidencia-edit-${ticketId}`);
        if (evidenciaCount >= 3 && btnAgregar) {
            btnAgregar.style.display = 'none';
        }
    }
}

// Función para eliminar evidencias (se llama desde el template)
async function eliminarEvidencia(ticketId, numero) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta evidencia?')) {
        return;
    }
    
    try {
        const response = await fetch(`/tickets/eliminar-evidencia/${ticketId}/${numero}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.csrfToken,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Recargar el modal de edición
            editarTicket(ticketId);
            mostrarMensaje('Evidencia eliminada correctamente', 'success');
        } else {
            mostrarMensaje('Error al eliminar la evidencia: ' + (data.error || 'Error desconocido'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión', 'error');
    }
}
