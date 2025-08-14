// JavaScript para helpdesk.html - Sistema de tickets con modales integrados

// Variables globales
let ticketActual = null;
let evidenciaEditCount = 1;

// Configuración de categorías por área
const categorias = {
    'Compras': ['Solicitud de compra', 'Cotizaciones', 'Reembolsos', 'Seguimiento de envíos'],
    'IT': ['Soporte técnico', 'Accesos y contraseñas', 'Red y conectividad', 'Correo electrónico', 'Impresoras y escáneres', 'Instalación de software'],
    'Diseño': ['Diseño de material impreso o digital', 'Actualización de diseño', 'Logotipos e identidad corporativa', 'Plantillas corporativas', 'Revisión de uso de marca'],
    'Soporte EHSmart': ['Acceso y usuarios', 'Errores técnicos', 'Capacitación EHSmart', 'Solicitud de soporte funcional'],
    'Recursos Humanos': ['Vacaciones y permisos', 'Nómina y pagos', 'Prestaciones y beneficios', 'Documentación y constancias'],
    'Desarrollo Organizacional': ['Asesoría individual', 'Gestión de conflictos laborales', 'Apoyo al desarrollo personal y profesional', 'Programas de desarrollo interno'],
    'Capacitación': ['Solicitud de curso', 'Alta de evento de capacitación', 'Dudas sobre plan de formación', 'Registro de constancia o diploma']
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('Helpdesk JS cargado');
    configurarEventListeners();
});

// ====== CONFIGURACIÓN DE EVENTOS ======
function configurarEventListeners() {
    // Event listeners para cerrar modales
    const btnCerrarVer = document.getElementById('btn-cerrar-modal-ver');
    const btnCerrarEditar = document.getElementById('btn-cerrar-modal-editar');
    
    if (btnCerrarVer) {
        btnCerrarVer.addEventListener('click', () => {
            document.getElementById('modal-ver-ticket').classList.add('hidden');
        });
    }
    
    if (btnCerrarEditar) {
        btnCerrarEditar.addEventListener('click', () => {
            document.getElementById('modal-editar-ticket').classList.add('hidden');
        });
    }

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

// ====== FUNCIONES DE MODAL VER TICKET ======
function verTicket(ticketId) {
    console.log('Abriendo modal para ver ticket:', ticketId);
    ticketActual = ticketId;
    
    // Mostrar modal
    const modal = document.getElementById('modal-ver-ticket');
    modal.classList.remove('hidden');
    
    // Cargar datos del ticket
    fetch(`/tickets/ver/${ticketId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarDatosVerTicket(data.ticket, data.comentarios, data.evidencias, data.es_administrador);
            } else {
                alert('Error al cargar el ticket: ' + (data.error || 'Error desconocido'));
                modal.classList.add('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error de conexión');
            modal.classList.add('hidden');
        });
}

function cargarDatosVerTicket(ticket, comentarios, evidencias, esAdministrador) {
    // Header del ticket
    document.getElementById('ver-ticket-numero').textContent = `Ticket #${String(ticket.id).padStart(3, '0')}`;
    document.getElementById('ver-ticket-titulo').textContent = ticket.titulo;
    document.getElementById('ver-ticket-fecha').textContent = formatearFecha(ticket.fecha_creacion);
    
    // Prioridad
    const prioridadSpan = document.getElementById('ver-ticket-prioridad');
    prioridadSpan.textContent = ticket.prioridad;
    prioridadSpan.className = `inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getPrioridadClass(ticket.prioridad)}`;
    
    // Información del ticket
    document.getElementById('ver-ticket-area').textContent = ticket.area || 'N/A';
    document.getElementById('ver-ticket-categoria').textContent = ticket.categoria;
    document.getElementById('ver-ticket-solicitante').textContent = ticket.nombre_solicitante || 'N/A';
    document.getElementById('ver-ticket-actualizacion').textContent = formatearFecha(ticket.fecha_actualizacion || ticket.fecha_creacion);
    
    // Estado
    const estadoSpan = document.getElementById('ver-ticket-estado');
    estadoSpan.textContent = ticket.estatus;
    estadoSpan.className = `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoClass(ticket.estatus)}`;
    
    // Descripción
    document.getElementById('ver-ticket-descripcion').textContent = ticket.descripcion;
    
    // Cambiar estado (solo administradores)
    const cambiarEstadoDiv = document.getElementById('ver-cambiar-estado');
    if (esAdministrador) {
        cambiarEstadoDiv.classList.remove('hidden');
        document.getElementById('nuevo-estatus-ticket').value = ticket.estatus;
    } else {
        cambiarEstadoDiv.classList.add('hidden');
    }
    
    // Evidencias
    cargarEvidenciasVer(evidencias);
    
    // Comentarios
    cargarComentariosVer(comentarios);
}

function cargarEvidenciasVer(evidencias) {
    const container = document.getElementById('ver-evidencias-container');
    const grid = document.getElementById('ver-evidencias-grid');
    
    if (evidencias && evidencias.length > 0) {
        container.classList.remove('hidden');
        grid.innerHTML = '';
        
        evidencias.forEach(evidencia => {
            const div = document.createElement('div');
            div.className = 'border border-gray-200 rounded-lg p-4 text-center';
            div.innerHTML = `
                <a href="${evidencia.url}" target="_blank" class="text-blue-600 hover:text-blue-800">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
                    </svg>
                    ${evidencia.nombre}
                </a>
            `;
            grid.appendChild(div);
        });
    } else {
        container.classList.add('hidden');
    }
}

function cargarComentariosVer(comentarios) {
    const lista = document.getElementById('lista-comentarios');
    lista.innerHTML = '';
    
    if (comentarios && comentarios.length > 0) {
        comentarios.forEach(comentario => {
            const div = document.createElement('div');
            div.className = 'border border-gray-200 rounded-lg p-4';
            div.innerHTML = `
                <div class="flex justify-between items-start mb-2">
                    <h5 class="font-medium text-gray-900">${comentario.usuario_nombre}</h5>
                    <span class="text-xs text-gray-500">${comentario.fecha_creacion}</span>
                </div>
                <p class="text-sm text-gray-700 whitespace-pre-wrap">${comentario.contenido}</p>
            `;
            lista.appendChild(div);
        });
    }
}

// ====== FUNCIONES DE MODAL EDITAR TICKET ======
function editarTicket(ticketId) {
    console.log('Abriendo modal para editar ticket:', ticketId);
    ticketActual = ticketId;
    
    // Mostrar modal
    const modal = document.getElementById('modal-editar-ticket');
    modal.classList.remove('hidden');
    
    // Cargar datos del ticket
    fetch(`/tickets/editar/${ticketId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarDatosEditarTicket(data.ticket, data.es_administrador);
            } else {
                alert('Error al cargar el ticket: ' + (data.error || 'Error desconocido'));
                modal.classList.add('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error de conexión');
            modal.classList.add('hidden');
        });
}

function cargarDatosEditarTicket(ticket, esAdministrador) {
    // Configurar formulario
    const form = document.getElementById('form-editar-ticket');
    form.action = `/tickets/actualizar_ticket/${ticket.id}`;
    
    // Header del ticket
    document.getElementById('editar-ticket-numero').textContent = `Editando Ticket #${String(ticket.id).padStart(3, '0')}`;
    document.getElementById('editar-ticket-fecha').textContent = `Creado: ${formatearFecha(ticket.fecha_creacion)}`;
    
    // Prioridad en header
    const prioridadSpan = document.getElementById('editar-ticket-prioridad');
    prioridadSpan.textContent = ticket.prioridad;
    prioridadSpan.className = `inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getPrioridadClass(ticket.prioridad)}`;
    
    // Llenar formulario
    document.getElementById('area-edit').value = ticket.area;
    document.getElementById('titulo-edit').value = ticket.titulo;
    document.getElementById('descripcion-edit').value = ticket.descripcion;
    document.getElementById('prioridad-edit').value = ticket.prioridad;
    
    // Actualizar categorías y seleccionar la actual
    actualizarCategoriasEdit();
    setTimeout(() => {
        document.getElementById('categoria-edit').value = ticket.categoria;
    }, 100);
    
    // Estado (solo administradores)
    const estadoContainer = document.getElementById('editar-estado-container');
    if (esAdministrador) {
        estadoContainer.classList.remove('hidden');
        document.getElementById('estatus-edit').value = ticket.estatus;
    } else {
        estadoContainer.classList.add('hidden');
    }
    
    // Evidencias actuales
    cargarEvidenciasActualesEdit(ticket);
    
    // Resetear contador de evidencias nuevas
    evidenciaEditCount = 1;
    document.getElementById('evidencia-edit-container').innerHTML = `
        <div class="evidencia-edit-item mb-4">
            <input type="file" name="nueva_evidencia_1" accept="image/*,.pdf,.doc,.docx,.txt" 
                   class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
        </div>
    `;
    document.getElementById('btn-agregar-evidencia-edit').style.display = 'inline-block';
}

function cargarEvidenciasActualesEdit(ticket) {
    const grid = document.getElementById('evidencias-actuales-grid');
    grid.innerHTML = '';
    
    for (let i = 1; i <= 3; i++) {
        const evidencia = ticket[`evidencia_${i}`];
        if (evidencia) {
            const div = document.createElement('div');
            div.className = 'border border-gray-200 rounded-lg p-4 text-center';
            div.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="text-sm text-gray-600">Evidencia ${i}</span>
                    <button type="button" onclick="eliminarEvidencia(${ticket.id}, ${i})" class="text-red-600 hover:text-red-800">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
                <a href="/tickets/uploads/${evidencia}" target="_blank" class="text-blue-600 hover:text-blue-800">
                    <svg class="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
                    </svg>
                    <span class="text-xs">${evidencia}</span>
                </a>
            `;
            grid.appendChild(div);
        }
    }
}

function actualizarCategoriasEdit() {
    const areaSelect = document.getElementById('area-edit');
    const categoriaSelect = document.getElementById('categoria-edit');
    const area = areaSelect.value;
    
    categoriaSelect.innerHTML = '<option value="">Selecciona una categoría</option>';
    
    if (area && categorias[area]) {
        categorias[area].forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categoriaSelect.appendChild(option);
        });
    }
}

function agregarEvidenciaEdit() {
    if (evidenciaEditCount < 3) {
        evidenciaEditCount++;
        const container = document.getElementById('evidencia-edit-container');
        const div = document.createElement('div');
        div.className = 'evidencia-edit-item mb-4';
        div.innerHTML = `
            <div class="flex items-center gap-2">
                <input type="file" name="nueva_evidencia_${evidenciaEditCount}" accept="image/*,.pdf,.doc,.docx,.txt" 
                       class="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <button type="button" onclick="this.parentElement.parentElement.remove(); evidenciaEditCount--;" class="text-red-600 hover:text-red-800">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        `;
        container.appendChild(div);
        
        if (evidenciaEditCount >= 3) {
            document.getElementById('btn-agregar-evidencia-edit').style.display = 'none';
        }
    }
}

function eliminarEvidencia(ticketId, numero) {
    if (confirm('¿Estás seguro de que quieres eliminar esta evidencia?')) {
        fetch(`/tickets/eliminar-evidencia/${ticketId}/${numero}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Recargar el modal de edición
                editarTicket(ticketId);
            } else {
                alert('Error al eliminar la evidencia: ' + (data.error || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error de conexión');
        });
    }
}

// ====== FUNCIONES DE COMENTARIOS ======
function mostrarFormularioComentario() {
    document.getElementById('form-comentario').classList.remove('hidden');
}

function cancelarComentario() {
    document.getElementById('form-comentario').classList.add('hidden');
    document.getElementById('contenido-comentario').value = '';
}

function guardarComentario() {
    const contenido = document.getElementById('contenido-comentario').value;
    
    if (!contenido.trim()) {
        alert('Por favor escribe un comentario');
        return;
    }
    
    fetch(`/tickets/comentar/${ticketActual}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({ contenido: contenido })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recargar el contenido del modal
            verTicket(ticketActual);
        } else {
            alert('Error al guardar el comentario: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// ====== FUNCIONES DE ESTADO ======
function actualizarEstatus() {
    const nuevoEstatus = document.getElementById('nuevo-estatus-ticket').value;
    
    fetch(`/tickets/actualizar_estatus/${ticketActual}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({ estatus: nuevoEstatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Estado actualizado exitosamente');
            document.getElementById('modal-ver-ticket').classList.add('hidden');
            window.location.reload();
        } else {
            alert('Error al actualizar el estado: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// ====== FUNCIONES AUXILIARES ======
function cerrarModales() {
    document.getElementById('modal-ver-ticket').classList.add('hidden');
    document.getElementById('modal-editar-ticket').classList.add('hidden');
}

function formatearFecha(fechaStr) {
    if (!fechaStr) return 'N/A';
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString('es-ES') + ' ' + fecha.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
}

function getPrioridadClass(prioridad) {
    switch (prioridad) {
        case 'Baja': return 'bg-green-100 text-green-800';
        case 'Media': return 'bg-yellow-100 text-yellow-800';
        case 'Alta': return 'bg-orange-100 text-orange-800';
        case 'Urgente': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function getEstadoClass(estado) {
    switch (estado) {
        case 'Abierto': return 'bg-blue-100 text-blue-800';
        case 'En Progreso': return 'bg-yellow-100 text-yellow-800';
        case 'Resuelto': return 'bg-green-100 text-green-800';
        case 'Cerrado': return 'bg-gray-100 text-gray-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

// ====== MANEJO DEL FORMULARIO DE EDICIÓN ======
function manejarSubmitEdicion(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    fetch(event.target.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Ticket actualizado exitosamente');
            document.getElementById('modal-editar-ticket').classList.add('hidden');
            window.location.reload();
        } else {
            alert('Error al actualizar el ticket: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// Event listener para cambio de área en edición
document.addEventListener('DOMContentLoaded', function() {
    const areaEdit = document.getElementById('area-edit');
    if (areaEdit) {
        areaEdit.addEventListener('change', actualizarCategoriasEdit);
    }
    
    const formEditarTicket = document.getElementById('form-editar-ticket');
    if (formEditarTicket) {
        formEditarTicket.addEventListener('submit', manejarSubmitEdicion);
    }
});
