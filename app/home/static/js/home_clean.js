// ===== HOME.JS - VERSIÓN DEFINITIVA CORREGIDA =====

// Variables globales
let currentDeleteUrl = '';
let confirmarEliminacionCallback = null;

// --- INICIALIZACIÓN PRINCIPAL ---
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 HOME.JS INICIADO CORRECTAMENTE');
    
    // Configurar saludo dinámico
    configurarSaludo();
    
    // Configurar modales
    configurarModales();
    
    // Configurar event listeners universales
    configurarEventListeners();
    
    // Cerrar dropdowns al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            cerrarDropdowns();
        }
    });
    
    console.log('✅ Todas las funcionalidades cargadas');
});

// --- CONFIGURACIÓN DE EVENT LISTENERS UNIVERSALES ---
function configurarEventListeners() {
    // Event delegation para todos los clicks
    document.addEventListener('click', function(e) {
        // Dropdowns toggles (3 puntos)
        if (e.target.closest('.dropdown-toggle')) {
            e.preventDefault();
            e.stopPropagation();
            const button = e.target.closest('.dropdown-toggle');
            const dropdownId = button.getAttribute('data-dropdown-id') || 
                             button.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
            if (dropdownId) {
                toggleDropdown(dropdownId);
            }
        }
        
        // Botones de eliminar en dropdowns
        else if (e.target.closest('[data-delete-url]')) {
            e.preventDefault();
            const button = e.target.closest('[data-delete-url]');
            const deleteUrl = button.getAttribute('data-delete-url');
            const deleteType = button.getAttribute('data-delete-type');
            
            switch(deleteType) {
                case 'publicacion':
                    confirmarEliminarPublicacion(deleteUrl);
                    break;
                case 'evento':
                    confirmarEliminarEvento(deleteUrl);
                    break;
                case 'comentario':
                    confirmarEliminarComentario(deleteUrl);
                    break;
            }
        }
        
        // Botón "Ver más comentarios"
        else if (e.target.closest('.mostrar-mas-comentarios')) {
            e.preventDefault();
            const button = e.target.closest('.mostrar-mas-comentarios');
            const postId = button.getAttribute('data-post-id');
            const currentPage = parseInt(button.getAttribute('data-page')) || 1;
            cargarMasComentarios(postId, currentPage);
        }
        
        // Botones de reacción (Me gusta)
        else if (e.target.closest('[data-reaction]')) {
            e.preventDefault();
            const button = e.target.closest('[data-reaction]');
            toggleReaction(button);
        }
        
        // Botón toggle comentarios
        else if (e.target.closest('[id^="btn-comments-toggle-"]')) {
            e.preventDefault();
            const button = e.target.closest('[id^="btn-comments-toggle-"]');
            const postId = button.getAttribute('data-post-id') || button.id.split('-')[3];
            toggleComments(postId);
        }
    });
    
    // Envío de formularios de comentarios
    document.addEventListener('submit', function(e) {
        if (e.target.classList.contains('comment-form')) {
            e.preventDefault();
            enviarComentario(e.target);
        }
    });
}

// --- FUNCIONES PARA DROPDOWNS ---
function toggleDropdown(dropdownId) {
    // Cerrar todos los otros dropdowns primero
    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        if (menu.id !== `dropdown-${dropdownId}`) {
            menu.classList.remove('show');
        }
    });
    
    // Toggle el dropdown actual
    const dropdown = document.getElementById(`dropdown-${dropdownId}`);
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

function cerrarDropdowns() {
    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
    });
}

// --- FUNCIONES PARA MODALES DE ELIMINACIÓN ---
function mostrarModalEliminacion(titulo, mensaje, confirmarCallback) {
    // Remover modal existente si lo hay
    const existingModal = document.getElementById('modal-eliminacion');
    if (existingModal) {
        existingModal.remove();
    }

    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" id="modal-eliminacion">
            <div class="bg-white rounded-2xl p-8 max-w-sm w-full mx-4 text-center shadow-2xl">
                <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H8a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-3">${titulo}</h3>
                <p class="text-gray-600 mb-8 leading-relaxed">${mensaje}</p>
                <div class="flex gap-3">
                    <button onclick="cerrarModalEliminacion()" class="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors">
                        Cancelar
                    </button>
                    <button onclick="ejecutarEliminacion()" class="flex-1 px-6 py-3 bg-red-600 text-white rounded-xl font-medium hover:bg-red-700 transition-colors">
                        Eliminar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    confirmarEliminacionCallback = confirmarCallback;
    
    // Cerrar con ESC
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            cerrarModalEliminacion();
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);
    
    // Cerrar haciendo clic fuera
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            cerrarModalEliminacion();
        }
    });
}

function cerrarModalEliminacion() {
    const modal = document.getElementById('modal-eliminacion');
    if (modal) {
        modal.remove();
    }
    confirmarEliminacionCallback = null;
    currentDeleteUrl = '';
}

function ejecutarEliminacion() {
    if (confirmarEliminacionCallback) {
        confirmarEliminacionCallback();
    }
    cerrarModalEliminacion();
}

// --- FUNCIONES ESPECÍFICAS DE ELIMINACIÓN ---
function confirmarEliminarPublicacion(deleteUrl) {
    console.log('🗑️ Confirmar eliminar publicación:', deleteUrl);
    cerrarDropdowns();
    
    mostrarModalEliminacion(
        'Eliminar publicación',
        '¿Estás seguro de que deseas eliminar esta publicación?<br>Esta acción no se puede deshacer.',
        () => eliminarConUrl(deleteUrl)
    );
}

function confirmarEliminarEvento(deleteUrl) {
    console.log('🗑️ Confirmar eliminar evento:', deleteUrl);
    cerrarDropdowns();
    
    mostrarModalEliminacion(
        'Eliminar evento',
        '¿Estás seguro de que deseas eliminar este evento?<br>Esta acción no se puede deshacer.',
        () => eliminarConUrl(deleteUrl)
    );
}

function confirmarEliminarComentario(deleteUrl) {
    console.log('🗑️ Confirmar eliminar comentario:', deleteUrl);
    cerrarDropdowns();
    
    mostrarModalEliminacion(
        'Eliminar comentario',
        '¿Estás seguro de que deseas eliminar este comentario?<br>Esta acción no se puede deshacer.',
        () => eliminarConUrl(deleteUrl)
    );
}

function eliminarConUrl(deleteUrl) {
    fetch(deleteUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': obtenerCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + (data.message || 'No se pudo eliminar'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión al eliminar');
    });
}

// --- FUNCIÓN PARA TOGGLE COMENTARIOS ---
function toggleComments(postId) {
    const commentsSection = document.getElementById(`comments-section-${postId}`);
    const btnToggle = document.getElementById(`btn-comments-toggle-${postId}`);
    
    if (commentsSection) {
        const isHidden = commentsSection.classList.toggle('hidden');
        if (btnToggle) {
            btnToggle.setAttribute('aria-expanded', (!isHidden).toString());
        }
    }
}

// --- FUNCIÓN PARA TOGGLE REACCIONES ---
function toggleReaction(button) {
    const postId = button.dataset.postId;
    const reactionType = button.dataset.reaction;
    
    console.log('❤️ Toggle reaction:', postId, reactionType);
    
    fetch('/home/toggle_reaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': obtenerCSRFToken()
        },
        body: JSON.stringify({
            post_id: parseInt(postId),
            reaction_type: reactionType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar contador
            const countElement = document.getElementById(`love-count-${postId}`);
            if (countElement) {
                countElement.textContent = data.love_count;
            }
            
            // Actualizar estilo del botón
            const svgIcon = button.querySelector('svg');
            if (data.user_reacted) {
                button.classList.add('text-red-500');
                button.classList.remove('hover:text-red-500');
                if (svgIcon) svgIcon.setAttribute('fill', 'currentColor');
            } else {
                button.classList.remove('text-red-500');
                button.classList.add('hover:text-red-500');
                if (svgIcon) svgIcon.setAttribute('fill', 'none');
            }
        } else {
            console.error('Error en reacción:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// --- FUNCIÓN PARA CARGAR MÁS COMENTARIOS ---
function cargarMasComentarios(postId, page) {
    console.log('💬 Cargando más comentarios para post:', postId, 'página:', page);
    
    const button = document.querySelector(`[data-post-id="${postId}"].mostrar-mas-comentarios`);
    if (button) {
        button.disabled = true;
        button.textContent = 'Cargando...';
    }
    
    fetch(`/home/cargar_mas_comentarios/${postId}?page=${page}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': obtenerCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Agregar comentarios al DOM
            const commentsList = document.getElementById(`comentarios-lista-${postId}`);
            if (commentsList && data.comments_html) {
                data.comments_html.forEach(commentHtml => {
                    commentsList.insertAdjacentHTML('beforeend', commentHtml);
                });
            }
            
            // Actualizar o ocultar botón
            if (button) {
                if (data.has_more) {
                    button.disabled = false;
                    button.setAttribute('data-page', data.next_page);
                    button.textContent = `Ver más comentarios`;
                } else {
                    button.remove();
                }
            }
        } else {
            console.error('Error al cargar comentarios:', data.message);
            if (button) {
                button.disabled = false;
                button.textContent = 'Error al cargar';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (button) {
            button.disabled = false;
            button.textContent = 'Error al cargar';
        }
    });
}

// --- FUNCIÓN PARA ENVIAR COMENTARIOS ---
function enviarComentario(form) {
    const formData = new FormData(form);
    // Extraer el ID del post de la URL: /home/post/9/comment -> 9
    const urlParts = form.action.split('/');
    const postId = urlParts[urlParts.length - 2]; // Obtener el penúltimo elemento
    
    console.log('💬 Enviando comentario para post:', postId);
    console.log('💬 URL de acción:', form.action);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': obtenerCSRFToken()
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('✅ Comentario enviado exitosamente');
            console.log('📄 Datos del comentario:', data);
            
            // Limpiar formulario
            form.reset();
            
            // Agregar comentario al DOM dinámicamente
            const commentsList = document.getElementById(`comentarios-lista-${postId}`);
            console.log('📋 Lista de comentarios encontrada:', commentsList);
            
            if (commentsList) {
                const newCommentHtml = `
                    <li class="flex space-x-3 group relative" data-comment-id="${data.comment_id}">
                        ${data.puede_eliminar ? `
                        <div class="absolute right-0 top-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                            <div class="relative dropdown">
                                <button class="dropdown-toggle" data-dropdown-id="comment-${data.comment_id}" type="button" aria-label="Opciones de comentario">
                                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                                    </svg>
                                </button>
                                <div id="dropdown-comment-${data.comment_id}" class="dropdown-menu">
                                    <button class="dropdown-item danger" data-delete-url="${data.delete_url}" data-delete-type="comentario" type="button">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H8a1 1 0 00-1 1v3M4 7h16"/>
                                        </svg>
                                        Eliminar
                                    </button>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        <img title="${data.comment_user}" class="w-8 h-8 rounded-full flex-shrink-0" src="${data.comment_user_avatar}" alt="Avatar">
                        <div class="flex-1 bg-gray-100 rounded-xl px-3 py-2">
                            <p class="text-gray-800 text-sm">${data.comment_content}</p>
                        </div>
                    </li>
                `;
                
                // Insertar el comentario al inicio de la lista
                commentsList.insertAdjacentHTML('afterbegin', newCommentHtml);
                
                // Actualizar contador de comentarios
                const commentButton = document.querySelector(`#btn-comments-toggle-${postId} span:last-child`);
                if (commentButton) {
                    const currentCount = parseInt(commentButton.textContent) || 0;
                    commentButton.textContent = currentCount + 1;
                    console.log('🔢 Contador actualizado a:', currentCount + 1);
                }
                
                // Mostrar la sección de comentarios si estaba oculta
                const commentsSection = document.getElementById(`comments-section-${postId}`);
                if (commentsSection && commentsSection.classList.contains('hidden')) {
                    commentsSection.classList.remove('hidden');
                    const btnToggle = document.getElementById(`btn-comments-toggle-${postId}`);
                    if (btnToggle) {
                        btnToggle.setAttribute('aria-expanded', 'true');
                    }
                    console.log('👀 Sección de comentarios mostrada');
                }
                
                console.log('✅ Comentario agregado al DOM correctamente');
            } else {
                console.error('❌ No se encontró la lista de comentarios para el post:', postId);
            }
        } else {
            console.error('❌ Error al enviar comentario:', data.message);
            alert('Error al enviar comentario: ' + data.message);
        }
    })
    .catch(error => {
        console.error('❌ Error de conexión:', error);
        alert('Error de conexión al enviar comentario');
    });
}

// --- FUNCIONES DE CONFIGURACIÓN ---
function configurarSaludo() {
    const saludoElement = document.getElementById('saludo');
    if (saludoElement) {
        const nombre = saludoElement.getAttribute('data-nombre') || 'Usuario';
        const hora = new Date().getHours();
        let saludo;
        
        if (hora < 12) saludo = 'Buenos días';
        else if (hora < 18) saludo = 'Buenas tardes';
        else saludo = 'Buenas noches';
        
        saludoElement.textContent = `${saludo}, ${nombre.split(' ')[0]}`;
    }
}

function configurarModales() {
    // Modal para eventos
    const btnNuevoEvento = document.getElementById('btn-nuevo-evento');
    const btnNuevoEventoMobile = document.getElementById('btn-nuevo-evento-mobile');
    const modalEvento = document.getElementById('modal-evento');
    const btnCerrarEvento = document.getElementById('btn-cerrar-modal-evento');
    const formEvento = document.getElementById('form-evento');
    
    // Modal para posts
    const btnAbrirModalPost = document.getElementById('btn-abrir-modal-post');
    const modalPost = document.getElementById('modal-post');
    const btnCerrarPost = document.getElementById('btn-cerrar-modal-post');
    const postFormModal = document.getElementById('post-form-modal');
    
    // Función para abrir modal
    function abrirModal(modal) {
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            modal.setAttribute('aria-hidden', 'false');
            document.body.classList.add('overflow-hidden');
        }
    }
    
    // Función para cerrar modal
    function cerrarModal(modal) {
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            modal.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('overflow-hidden');
            
            // Limpiar formularios
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
            }
        }
    }
    
    // Event listeners para abrir modales de eventos
    [btnNuevoEvento, btnNuevoEventoMobile].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', () => {
                abrirModal(modalEvento);
            });
        }
    });
    
    // Event listener para cerrar modal de evento
    if (btnCerrarEvento) {
        btnCerrarEvento.addEventListener('click', () => {
            cerrarModal(modalEvento);
        });
    }
    
    // Event listener para abrir modal de posts
    if (btnAbrirModalPost) {
        btnAbrirModalPost.addEventListener('click', () => {
            abrirModal(modalPost);
        });
    }
    
    // Event listener para cerrar modal de posts
    if (btnCerrarPost) {
        btnCerrarPost.addEventListener('click', () => {
            cerrarModal(modalPost);
        });
    }
    
    // Cerrar modales al hacer clic fuera del contenido
    if (modalEvento) {
        modalEvento.addEventListener('click', (e) => {
            if (e.target === modalEvento) {
                cerrarModal(modalEvento);
            }
        });
    }
    
    if (modalPost) {
        modalPost.addEventListener('click', (e) => {
            if (e.target === modalPost) {
                cerrarModal(modalPost);
            }
        });
    }
    
    // Cerrar modales con tecla Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (modalEvento && !modalEvento.classList.contains('hidden')) {
                cerrarModal(modalEvento);
            }
            if (modalPost && !modalPost.classList.contains('hidden')) {
                cerrarModal(modalPost);
            }
        }
    });
    
    // Envío de formulario de evento
    if (formEvento) {
        formEvento.addEventListener('submit', function(e) {
            e.preventDefault();
            enviarFormularioEvento(this);
        });
    }
    
    // Envío de formulario de post
    if (postFormModal) {
        postFormModal.addEventListener('submit', function(e) {
            e.preventDefault();
            enviarFormularioPost(this);
        });
    }
}

// --- FUNCIONES PARA ENVÍO DE FORMULARIOS ---
function enviarFormularioEvento(form) {
    const formData = new FormData(form);
    
    fetch('/home/create_evento', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': obtenerCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal antes de recargar
            const modalEvento = document.getElementById('modal-evento');
            if (modalEvento) {
                modalEvento.classList.add('hidden');
                modalEvento.classList.remove('flex');
                modalEvento.setAttribute('aria-hidden', 'true');
                document.body.classList.remove('overflow-hidden');
            }
            
            // Mostrar mensaje de éxito
            alert('Evento creado correctamente');
            
            // Recargar página
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al crear evento');
    });
}

function enviarFormularioPost(form) {
    const formData = new FormData(form);
    
    fetch('/home/post/create', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': obtenerCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal antes de recargar
            const modalPost = document.getElementById('modal-post');
            if (modalPost) {
                modalPost.classList.add('hidden');
                modalPost.classList.remove('flex');
                modalPost.setAttribute('aria-hidden', 'true');
                document.body.classList.remove('overflow-hidden');
            }
            
            // Mostrar mensaje de éxito
            alert('Publicación creada correctamente');
            
            // Recargar página
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al crear publicación');
    });
}

// --- FUNCIÓN AUXILIAR PARA CSRF TOKEN ---
function obtenerCSRFToken() {
    return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || 
           document.querySelector('input[name="csrf_token"]')?.value || '';
}
