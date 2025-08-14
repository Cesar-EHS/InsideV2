// JavaScript para gestión de configuración y permisos

// Variables globales
let usuariosActivos = [];

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    cargarUsuariosActivos();
    cargarPermisosTickets();
    cargarPermisosHome();
});

// ====== GESTIÓN DE USUARIOS ACTIVOS ======
async function cargarUsuariosActivos() {
    try {
        const response = await fetch('/auth/api/usuarios-activos');
        const data = await response.json();
        
        if (data.success) {
            usuariosActivos = data.usuarios;
            console.log('Usuarios activos cargados:', usuariosActivos);
        } else {
            console.error('Error al cargar usuarios:', data.error);
        }
    } catch (error) {
        console.error('Error de conexión al cargar usuarios:', error);
    }
}

// ====== GESTIÓN DE PERMISOS DE TICKETS ======
async function cargarPermisosTickets() {
    try {
        const response = await fetch('/auth/api/permisos-tickets');
        const data = await response.json();
        
        if (data.success) {
            renderizarPermisosTickets(data.categorias, data.asignaciones);
        } else {
            console.error('Error al cargar permisos de tickets:', data.error);
        }
    } catch (error) {
        console.error('Error de conexión al cargar permisos de tickets:', error);
    }
}

function renderizarPermisosTickets(categorias, asignaciones) {
    const container = document.getElementById('permisos-tickets-content');
    if (!container) return;
    
    let html = '';
    
    for (const [area, categoriasArray] of Object.entries(categorias)) {
        const usuariosAsignados = asignaciones[area] || [];
        
        html += `
            <div class="bg-white border border-gray-200 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-lg font-semibold text-gray-900">${area}</h4>
                    <span class="text-sm text-gray-500">${categoriasArray.length} categorías</span>
                </div>
                
                <div class="mb-3">
                    <p class="text-sm text-gray-600 mb-2">Categorías:</p>
                    <div class="flex flex-wrap gap-2">
                        ${categoriasArray.map(cat => `
                            <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                                ${cat}
                            </span>
                        `).join('')}
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Usuarios responsables:
                    </label>
                    <select multiple class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                            id="permisos-${area.replace(/\s+/g, '-')}" 
                            data-area="${area}">
                        ${usuariosActivos.map(usuario => `
                            <option value="${usuario.id}" ${usuariosAsignados.includes(usuario.id) ? 'selected' : ''}>
                                ${usuario.nombre} (${usuario.puesto_trabajo || 'Sin puesto'})
                            </option>
                        `).join('')}
                    </select>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

async function guardarPermisosTickets() {
    try {
        const asignaciones = {};
        
        // Recolectar todas las asignaciones
        const selects = document.querySelectorAll('#permisos-tickets-content select[data-area]');
        selects.forEach(select => {
            const area = select.dataset.area;
            const usuariosSeleccionados = Array.from(select.selectedOptions).map(option => parseInt(option.value));
            asignaciones[area] = usuariosSeleccionados;
        });
        
        const response = await fetch('/auth/api/permisos-tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ asignaciones })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje('Permisos de tickets guardados correctamente', 'success');
        } else {
            mostrarMensaje('Error al guardar permisos: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error al guardar permisos de tickets:', error);
        mostrarMensaje('Error de conexión al guardar permisos', 'error');
    }
}

// ====== GESTIÓN DE PERMISOS DE HOME ======
async function cargarPermisosHome() {
    try {
        const response = await fetch('/auth/api/permisos-home');
        const data = await response.json();
        
        if (data.success) {
            renderizarPermisosHome(data.permisos);
        } else {
            console.error('Error al cargar permisos de home:', data.error);
        }
    } catch (error) {
        console.error('Error de conexión al cargar permisos de home:', error);
    }
}

function renderizarPermisosHome(permisos) {
    const container = document.getElementById('permisos-home-content');
    if (!container) return;
    
    const tiposPermisos = {
        'crear_posts': 'Crear publicaciones',
        'crear_eventos': 'Crear eventos',
        'moderar_contenido': 'Moderar contenido'
    };
    
    let html = '';
    
    for (const [tipo, nombre] of Object.entries(tiposPermisos)) {
        const usuariosAsignados = permisos[tipo] || [];
        
        html += `
            <div class="bg-white border border-gray-200 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-lg font-semibold text-gray-900">${nombre}</h4>
                    <span class="text-sm text-gray-500">${usuariosAsignados.length} usuarios</span>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Usuarios con permiso:
                    </label>
                    <select multiple class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                            id="permisos-home-${tipo}" 
                            data-tipo="${tipo}">
                        ${usuariosActivos.map(usuario => `
                            <option value="${usuario.id}" ${usuariosAsignados.includes(usuario.id) ? 'selected' : ''}>
                                ${usuario.nombre} (${usuario.puesto_trabajo || 'Sin puesto'})
                            </option>
                        `).join('')}
                    </select>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

async function guardarPermisosHome() {
    try {
        const permisos = {};
        
        // Recolectar todas las asignaciones
        const selects = document.querySelectorAll('#permisos-home-content select[data-tipo]');
        selects.forEach(select => {
            const tipo = select.dataset.tipo;
            const usuariosSeleccionados = Array.from(select.selectedOptions).map(option => parseInt(option.value));
            permisos[tipo] = usuariosSeleccionados;
        });
        
        const response = await fetch('/auth/api/permisos-home', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ permisos })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensaje('Permisos de Home guardados correctamente', 'success');
        } else {
            mostrarMensaje('Error al guardar permisos: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error al guardar permisos de home:', error);
        mostrarMensaje('Error de conexión al guardar permisos', 'error');
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

// ====== GESTIÓN DE TABLAS DE REFERENCIA ======
function agregarCategoria() {
    const area = document.getElementById('nueva-categoria-area').value;
    const categoria = document.getElementById('nueva-categoria-nombre').value;
    
    if (!area || !categoria) {
        mostrarMensaje('Por favor completa todos los campos', 'error');
        return;
    }
    
    // Aquí se agregaría la lógica para guardar en la base de datos
    mostrarMensaje(`Categoría "${categoria}" agregada al área "${area}"`, 'success');
    
    // Limpiar campos
    document.getElementById('nueva-categoria-area').value = '';
    document.getElementById('nueva-categoria-nombre').value = '';
    
    // Recargar permisos para mostrar la nueva categoría
    cargarPermisosTickets();
}

function eliminarCategoria(area, categoria) {
    if (confirm(`¿Estás seguro de que quieres eliminar la categoría "${categoria}" del área "${area}"?`)) {
        // Aquí se agregaría la lógica para eliminar de la base de datos
        mostrarMensaje(`Categoría "${categoria}" eliminada`, 'success');
        cargarPermisosTickets();
    }
}

// ====== VALIDACIONES ======
function validarFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let valid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            valid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return valid;
}
