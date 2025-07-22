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

  
  mostrarModalEliminacion(
    'Eliminar comentario',
    '¿Estás seguro de que deseas eliminar este comentario?<br>Esta acción no se puede deshacer.',
    () => eliminarConUrl(deleteUrl)
  );
}

// --- OTRAS FUNCIONES BÁSICAS ---

// Toggle comentarios
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

// Toggle reaction
function toggleReaction(button) {
  const postId = button.dataset.postId;
  const reactionType = button.dataset.reaction;
  
  fetch('/home/toggle_reaction', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || 
                    document.querySelector('input[name="csrf_token"]')?.value || ''
    },
    body: JSON.stringify({
      post_id: postId,
      reaction_type: reactionType
    })
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    }
    throw new Error('Error en la respuesta');
  })
  .then(data => {
    if (data.success) {
      // Actualizar el botón y contador dinámicamente
      const countElement = document.getElementById(`love-count-${postId}`);
      if (countElement) {
        countElement.textContent = data.new_count;
      }
      
      // Actualizar el estilo del botón
      if (data.user_reacted) {
        button.classList.add('text-red-500');
        button.classList.remove('hover:text-red-500');
        const svg = button.querySelector('svg');
        if (svg) {
          svg.setAttribute('fill', 'currentColor');
        }
      } else {
        button.classList.remove('text-red-500');
        button.classList.add('hover:text-red-500');
        const svg = button.querySelector('svg');
        if (svg) {
          svg.setAttribute('fill', 'none');
        }
      }
    }
  })
  .catch(error => {
    console.error('Error al toggle reaction:', error);
  });
}

// Cargar más comentarios
function cargarMasComentarios(postId, button) {
  const page = parseInt(button.dataset.page) + 1;
  
  fetch(`/home/load_more_comments/${postId}?page=${page}`, {
    method: 'GET',
    headers: {
      'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || 
                    document.querySelector('input[name="csrf_token"]')?.value || ''
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success && data.comments) {
      const comentariosLista = document.getElementById(`comentarios-lista-${postId}`);
      
      // Agregar los nuevos comentarios
      data.comments.forEach(comment => {
        const commentElement = document.createElement('li');
        commentElement.className = 'flex space-x-3 group relative';
        commentElement.setAttribute('data-comment-id', comment.id);
        
        let deleteButton = '';
        if (comment.puede_eliminar) {
          deleteButton = `
            <div class="absolute right-0 top-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
              <div class="relative dropdown">
                <button class="dropdown-toggle" onclick="toggleDropdown('comment-${comment.id}')" type="button" aria-label="Opciones de comentario">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                  </svg>
                </button>
                <div id="dropdown-comment-${comment.id}" class="dropdown-menu">
                  <button class="dropdown-item danger" data-delete-url="${comment.delete_url}" data-delete-type="comentario" type="button">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1-1H8a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          `;
        }
        
        commentElement.innerHTML = `
          ${deleteButton}
          <img title="${comment.user_name}" class="w-8 h-8 rounded-full flex-shrink-0" src="${comment.user_avatar}" alt="Avatar">
          <div class="flex-1 bg-gray-100 rounded-xl px-3 py-2">
            <p class="text-gray-800 text-sm">${comment.content}</p>
          </div>
        `;
        
        comentariosLista.appendChild(commentElement);
      });
      
      // Actualizar el botón
      button.dataset.page = page;
      if (data.has_more) {
        button.textContent = `Ver más comentarios (${data.remaining_count} restante${data.remaining_count !== 1 ? 's' : ''})`;
      } else {
        button.remove();
      }
    }
  })
  .catch(error => {
    console.error('Error al cargar más comentarios:', error);
  });
}

// --- FUNCIONES PARA MODALES ---

// Modal para crear publicación
function abrirModalPost() {
  document.getElementById('modal-post').classList.remove('hidden');
  document.getElementById('modal-post').classList.add('flex');
}

function cerrarModalPost() {
  document.getElementById('modal-post').classList.add('hidden');
  document.getElementById('modal-post').classList.remove('flex');
}

// Modal para crear evento
function abrirModalEvento() {
  document.getElementById('modal-evento').classList.remove('hidden');
  document.getElementById('modal-evento').classList.add('flex');
}

function cerrarModalEvento() {
  document.getElementById('modal-evento').classList.add('hidden');
  document.getElementById('modal-evento').classList.remove('flex');
}

// --- FUNCIÓN PARA SALUDO DINÁMICO ---
function actualizarSaludo() {
  const saludoElement = document.getElementById('saludo');
  if (saludoElement) {
    const nombre = saludoElement.getAttribute('data-nombre');
    const ahora = new Date();
    const hora = ahora.getHours();
    
    let saludo;
    if (hora >= 5 && hora < 12) {
      saludo = `Buenos días, ${nombre} 🌅`;
    } else if (hora >= 12 && hora < 18) {
      saludo = `Buenas tardes, ${nombre} ☀️`;
    } else {
      saludo = `Buenas noches, ${nombre} 🌙`;
    }
    
    saludoElement.textContent = saludo;
  }
}

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 HOME.JS DEFINITIVO CARGADO');
  console.log('✅ Funciones disponibles:');
  console.log('  - confirmarEliminarPublicacion(url)');
  console.log('  - confirmarEliminarEvento(url)');
  console.log('  - confirmarEliminarComentario(url)');
  console.log('  - toggleComments(postId)');
  console.log('  - toggleReaction(button)');
  
  // Hacer las funciones accesibles globalmente
  window.confirmarEliminarPublicacion = confirmarEliminarPublicacion;
  window.confirmarEliminarEvento = confirmarEliminarEvento;
  window.confirmarEliminarComentario = confirmarEliminarComentario;
  window.toggleComments = toggleComments;
  window.toggleReaction = toggleReaction;
  window.toggleDropdown = toggleDropdown;
  window.cargarMasComentarios = cargarMasComentarios;
  
  // Inicializar saludo dinámico
  actualizarSaludo();
  
  // Cerrar dropdowns al hacer clic fuera
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown')) {
      cerrarDropdowns();
    }
  });
  
  // Event listeners para botones de eliminar con data attributes
  document.addEventListener('click', function(e) {
    if (e.target.closest('.dropdown-item.danger')) {
      const button = e.target.closest('.dropdown-item.danger');
      const deleteUrl = button.getAttribute('data-delete-url');
      const deleteType = button.getAttribute('data-delete-type');
      
      if (deleteUrl && deleteType) {
        e.preventDefault();
        
        switch(deleteType) {
          case 'evento':
            confirmarEliminarEvento(deleteUrl);
            break;
          case 'publicacion':
            confirmarEliminarPublicacion(deleteUrl);
            break;
          case 'comentario':
            confirmarEliminarComentario(deleteUrl);
            break;
        }
      }
    }
    
    // Event listener para botón "Ver más comentarios"
    if (e.target.classList.contains('mostrar-mas-comentarios')) {
      const button = e.target;
      const postId = button.getAttribute('data-post-id');
      if (postId) {
        cargarMasComentarios(postId, button);
      }
    }
    
    // Event listener para toggle dropdown
    if (e.target.closest('.dropdown-toggle')) {
      const button = e.target.closest('.dropdown-toggle');
      const dropdownId = button.getAttribute('onclick');
      if (dropdownId) {
        // Extraer el ID del onclick
        const match = dropdownId.match(/toggleDropdown\('([^']+)'\)/);
        if (match) {
          e.preventDefault();
          toggleDropdown(match[1]);
        }
      }
    }
  });
  
  // Event listeners para modales
  const btnAbrirModalPost = document.getElementById('btn-abrir-modal-post');
  const btnCerrarModalPost = document.getElementById('btn-cerrar-modal-post');
  const btnNuevoEvento = document.getElementById('btn-nuevo-evento');
  const btnNuevoEventoMobile = document.getElementById('btn-nuevo-evento-mobile');
  const btnCerrarModalEvento = document.getElementById('btn-cerrar-modal-evento');
  
  if (btnAbrirModalPost) {
    btnAbrirModalPost.addEventListener('click', abrirModalPost);
  }
  
  if (btnCerrarModalPost) {
    btnCerrarModalPost.addEventListener('click', cerrarModalPost);
  }
  
  if (btnNuevoEvento) {
    btnNuevoEvento.addEventListener('click', abrirModalEvento);
  }
  
  if (btnNuevoEventoMobile) {
    btnNuevoEventoMobile.addEventListener('click', abrirModalEvento);
  }
  
  if (btnCerrarModalEvento) {
    btnCerrarModalEvento.addEventListener('click', cerrarModalEvento);
  }
  
  // Cerrar modales con ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      cerrarModalPost();
      cerrarModalEvento();
    }
  });
  
  // Cerrar modales haciendo clic fuera
  document.getElementById('modal-post')?.addEventListener('click', function(e) {
    if (e.target === this) {
      cerrarModalPost();
    }
  });
  
  document.getElementById('modal-evento')?.addEventListener('click', function(e) {
    if (e.target === this) {
      cerrarModalEvento();
    }
  });
  
  // Preview de imagen en modal de publicación
  const postImageInput = document.getElementById('post-image');
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('preview-image');
  const removeImageBtn = document.getElementById('remove-image');
  
  if (postImageInput) {
    postImageInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          previewImage.src = e.target.result;
          previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
      }
    });
  }
  
  if (removeImageBtn) {
    removeImageBtn.addEventListener('click', function() {
      postImageInput.value = '';
      previewContainer.classList.add('hidden');
      previewImage.src = '';
    });
  }
  
  // Configurar formulario de evento
  const formEvento = document.getElementById('form-evento');
  if (formEvento && !formEvento.action.includes('create_evento')) {
    formEvento.action = '/home/create_evento';
  }
  
  // Manejar envío de comentarios dinámicamente
  document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('comment-form')) {
      e.preventDefault();
      
      const form = e.target;
      const formData = new FormData(form);
      const postId = form.action.split('/').pop(); // Extraer post_id de la URL
      
      fetch(form.action, {
        method: 'POST',
        body: formData
      })
      .then(response => {
        // Primero verificar si la respuesta es OK
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Verificar si es JSON o HTML
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return response.json();
        } else {
          // Si no es JSON, es HTML - esto significa que se agregó exitosamente pero el servidor no envió JSON
          console.log('Comentario agregado exitosamente (respuesta HTML)');
          // Recargar la página para mostrar el nuevo comentario
          location.reload();
          return null;
        }
      })
      .then(data => {
        if (data && data.success) {
          // Limpiar el formulario
          form.querySelector('textarea').value = '';
          
          // Agregar el nuevo comentario a la lista
          const comentariosLista = document.getElementById(`comentarios-lista-${postId}`);
          const newComment = document.createElement('li');
          newComment.className = 'flex space-x-3 group relative';
          newComment.setAttribute('data-comment-id', data.comment_id);
          
          let deleteButton = '';
          if (data.puede_eliminar) {
            deleteButton = `
              <div class="absolute right-0 top-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                <div class="relative dropdown">
                  <button class="dropdown-toggle" onclick="toggleDropdown('comment-${data.comment_id}')" type="button" aria-label="Opciones de comentario">
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
            `;
          }
          
          newComment.innerHTML = `
            ${deleteButton}
            <img title="${data.comment_user}" class="w-8 h-8 rounded-full flex-shrink-0" src="${data.comment_user_avatar}" alt="Avatar">
            <div class="flex-1 bg-gray-100 rounded-xl px-3 py-2">
              <p class="text-gray-800 text-sm">${data.comment_content}</p>
            </div>
          `;
          
          // Insertar el nuevo comentario al principio de la lista
          comentariosLista.insertBefore(newComment, comentariosLista.firstChild);
          
          // Actualizar el contador de comentarios
          const commentButton = document.querySelector(`#btn-comments-toggle-${postId} span:last-child`);
          if (commentButton) {
            const currentCount = parseInt(commentButton.textContent) || 0;
            commentButton.textContent = currentCount + 1;
          }
        }
        // Si data es null (respuesta HTML), ya se recargó la página arriba
      })
      .catch(error => {
        console.error('Error al enviar comentario:', error);
        // Solo mostrar alert si realmente hay un error, no si es una respuesta HTML exitosa
        if (!error.message.includes('HTTP error! status: 2')) {
          alert('Error al agregar comentario');
        }
      });
    }
  });
});
