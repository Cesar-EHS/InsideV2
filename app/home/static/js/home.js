// --- FUNCIONES GLOBALES (definidas antes del DOMContentLoaded) ---

// --- Función para mostrar notificaciones toast ---
window.mostrarToast = function(mensaje, tipo = 'info') {
  // Crear elemento toast
  const toast = document.createElement('div');
  toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 transition-opacity duration-300 ${
    tipo === 'success' ? 'bg-green-500' : 
    tipo === 'error' ? 'bg-red-500' : 
    'bg-blue-500'
  }`;
  toast.textContent = mensaje;
  
  // Agregar al DOM
  document.body.appendChild(toast);
  
  // Remover después de 3 segundos
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => {
      if (document.body.contains(toast)) {
        document.body.removeChild(toast);
      }
    }, 300);
  }, 3000);
};

// --- Toggle comentarios (función global) ---
window.toggleComments = function (postId) {
  console.log('toggleComments llamado para post:', postId);
  const commentsSection = document.getElementById(`comments-section-${postId}`);
  const btnToggle = document.getElementById(`btn-comments-toggle-${postId}`);
  
  if (!commentsSection) {
    console.error('No se encontró comments-section para post:', postId);
    return;
  }
  if (!btnToggle) {
    console.error('No se encontró btn-comments-toggle para post:', postId);
    return;
  }

  const isHidden = commentsSection.classList.toggle('hidden');
  btnToggle.setAttribute('aria-expanded', (!isHidden).toString());
  console.log('Comentarios', isHidden ? 'ocultados' : 'mostrados', 'para post:', postId);
};

// --- Manejo de reacción con corazón (función global) ---
window.toggleReaction = async function (button) {
  console.log('toggleReaction llamado');
  const postId = button.getAttribute('data-post-id');
  const reactionType = button.getAttribute('data-reaction');
  
  console.log('Post ID:', postId, 'Reaction Type:', reactionType);

  try {
    const csrfToken = document.querySelector('input[name="csrf_token"]');
    if (!csrfToken) {
      console.error('No se encontró CSRF token');
      return;
    }

    const response = await fetch(`/home/add_reaction/${postId}?reaction_type=${reactionType}`, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrfToken.value
      }
    });

    if (!response.ok) throw new Error('Error en la respuesta del servidor');

    const data = await response.json();

    if (data.success) {
      const countSpan = document.getElementById('love-count-' + postId);
      if (countSpan) {
        countSpan.textContent = data.love_count;
      }

      button.classList.toggle('text-red-500');
      button.classList.toggle('text-gray-600');
      console.log('Reacción actualizada correctamente');
    } else {
      console.error('Error del servidor:', data.message);
      alert(data.message || 'Error al enviar reacción.');
    }
  } catch (error) {
    console.error('Error en toggleReaction:', error);
    alert('Error al conectar con el servidor.');
  }
};

// --- Mostrar más comentarios con paginación AJAX (función global) ---
window.mostrarMasComentarios = async function(postId) {
  console.log('mostrarMasComentarios llamado para post:', postId);
  
  const commentsContainer = document.querySelector(`#comentarios-lista-${postId}`);
  if (!commentsContainer) {
    console.error('No se encontró el contenedor de comentarios para post:', postId);
    return;
  }
  
  const loadMoreBtn = document.querySelector(`#load-more-${postId}`);
  if (!loadMoreBtn) {
    console.error('No se encontró el botón de cargar más para post:', postId);
    return;
  }
  
  const currentPage = parseInt(loadMoreBtn.dataset.page) || 1;
  const nextPage = currentPage + 1;
  
  console.log('Cargando página:', nextPage);
  
  try {
    console.log('Enviando petición a:', `/home/post/${postId}/comments?page=${nextPage}`);
    const response = await fetch(`/home/post/${postId}/comments?page=${nextPage}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    
    console.log('Status de respuesta:', response.status);
    console.log('Response OK:', response.ok);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error del servidor:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, response: ${errorText}`);
    }
    
    const data = await response.json();
    console.log('Respuesta del servidor:', data);
    
    if (data.success && data.comments) {
      // Agregar nuevos comentarios al contenedor
      data.comments.forEach(comment => {
        const commentElement = document.createElement('li');
        commentElement.className = 'flex space-x-3 group relative';
        commentElement.setAttribute('data-comment-id', comment.id);
        commentElement.innerHTML = `
          ${comment.puede_eliminar ? `
            <button class="eliminar-comentario absolute left-0 top-1 opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-700 text-sm w-5 h-5 flex items-center justify-center bg-white rounded-full shadow-sm z-10" 
                    data-comment-id="${comment.id}" 
                    data-post-id="${postId}"
                    title="Eliminar comentario">
              ✕
            </button>
          ` : ''}
          <img title="${comment.user_name}" class="w-8 h-8 rounded-full flex-shrink-0" src="${comment.user_avatar}" alt="Avatar">
          <div class="flex-1 bg-gray-100 rounded-xl px-3 py-2">
            <p class="text-gray-800 text-sm">${comment.content}</p>
          </div>
        `;
        commentsContainer.appendChild(commentElement);
      });
      
      // Actualizar estado del botón
      loadMoreBtn.dataset.page = nextPage;
      
      // Actualizar el texto del botón con el número correcto de comentarios restantes
      if (data.has_next) {
        const totalCommentsInPage = commentsContainer.children.length;
        const totalComments = data.total;
        const remainingComments = totalComments - totalCommentsInPage;
        
        if (remainingComments > 0) {
          const pluralText = remainingComments === 1 ? 'restante' : 'restantes';
          loadMoreBtn.textContent = `Ver más comentarios (${remainingComments} ${pluralText})`;
        } else {
          loadMoreBtn.style.display = 'none';
        }
      } else {
        loadMoreBtn.style.display = 'none';
        console.log('No hay más comentarios, ocultando botón');
      }
    } else {
      console.error('Error en la respuesta:', data.message);
      mostrarToast(data.message || 'Error al cargar más comentarios');
    }
  } catch (error) {
    console.error('Error al cargar más comentarios:', error);
    mostrarToast('Error al conectar con el servidor');
  }
};

// --- Función para eliminar comentarios ---
window.eliminarComentario = async function(commentId, postId) {
  mostrarDialogoConfirmacion({
    mensaje: "¿Estás seguro de que quieres eliminar este comentario?",
    onConfirm: async () => {
      try {
        const response = await fetch(`/delete_comment/${commentId}`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
          }
        });
        
        const data = await response.json();
        if (data.success) {
          // Buscar y eliminar el elemento del comentario
          const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
          if (commentElement) {
            commentElement.remove();
          }
          mostrarToast('Comentario eliminado exitosamente');
          
          // Actualizar contador de comentarios
          const commentsList = document.querySelector(`#comentarios-lista-${postId}`);
          if (commentsList) {
            const remainingComments = commentsList.children.length;
            const commentsButton = document.querySelector(`#btn-comments-toggle-${postId}`);
            if (commentsButton) {
              const countSpan = commentsButton.querySelector('svg').nextSibling;
              if (countSpan) {
                countSpan.textContent = ` ${remainingComments}`;
              }
            }
          }
        } else {
          mostrarToast(data.message || 'Error al eliminar el comentario');
        }
      } catch (error) {
        console.error('Error al eliminar comentario:', error);
        mostrarToast('Error al conectar con el servidor');
      }
    }
  });
};

// --- Función para actualizar la paginación de comentarios (función global) ---
window.updateCommentsPagination = function(postId) {
  console.log('updateCommentsPagination llamado para post:', postId);
  const lista = document.getElementById(`comment-list-${postId}`);
  if (!lista) {
    console.error('No se encontró lista de comentarios para post:', postId);
    return;
  }

  const todosLosComentarios = lista.querySelectorAll('[id^="comment-"]');
  console.log('Total comentarios encontrados:', todosLosComentarios.length);
  
  // Ocultar todos los comentarios excepto los primeros 4
  todosLosComentarios.forEach((comment, index) => {
    if (index >= 4) {
      comment.style.display = 'none';
      comment.setAttribute('data-visible', 'false');
    } else {
      comment.style.display = 'block';
      comment.setAttribute('data-visible', 'true');
    }
  });

  // Actualizar o crear el botón "Ver más"
  updateLoadMoreButton(postId);
};

// --- Función para manejar el botón "Ver más comentarios" (función global) ---
window.updateLoadMoreButton = function(postId) {
  const lista = document.getElementById(`comment-list-${postId}`);
  const commentsSection = document.getElementById(`comments-section-${postId}`);
  if (!lista || !commentsSection) return;

  const ocultos = lista.querySelectorAll('[data-visible="false"]');
  let btn = commentsSection.querySelector('.load-more-btn');

  if (ocultos.length > 0) {
    if (!btn) {
      btn = document.createElement('button');
      btn.className = 'load-more-btn text-blue-600 hover:text-blue-700 text-sm font-medium mt-2 transition-colors';
      btn.type = 'button';
      btn.onclick = () => mostrarMasComentarios(postId);
      
      // Insertar antes del formulario de comentarios
      const form = commentsSection.querySelector('form');
      commentsSection.insertBefore(btn, form);
    }
    
    const remaining = ocultos.length;
    const toShow = Math.min(remaining, 5);
    btn.textContent = `Ver ${toShow} comentario${toShow > 1 ? 's' : ''} más${remaining > toShow ? ` (${remaining} restantes)` : ''}`;
  } else if (btn) {
    btn.remove();
  }
};

// --- INICIO DEL CÓDIGO PRINCIPAL ---
document.addEventListener('DOMContentLoaded', () => {
  // --- Saludo dinámico según hora ---
  const saludoElem = document.getElementById('saludo');
  if (saludoElem) {
    const nombreUsuario = saludoElem.dataset.nombre || 'Usuario';
    saludoElem.textContent = obtenerSaludo(nombreUsuario);
  }

  function obtenerSaludo(nombre) {
    const hora = new Date().getHours();
    if (hora >= 5 && hora < 12) return `🌅 Buenos días, ${nombre}`;
    if (hora >= 12 && hora < 19) return `☀️ Buenas tardes, ${nombre}`;
    return `🌙 Buenas noches, ${nombre}`;
  }

  // --- Actualizar hora local cada minuto ---
  const horaLocalElem = document.getElementById('hora-local');
  if (horaLocalElem) {
    actualizarHora();
    setInterval(actualizarHora, 60000);
  }
  function actualizarHora() {
    const now = new Date();
    horaLocalElem.textContent = now.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }

  // --- Modal para agregar evento ---
  setupModal('btn-nuevo-evento', 'modal-evento', 'btn-cerrar-modal-evento');
  setupModal('btn-nuevo-evento-mobile', 'modal-evento', 'btn-cerrar-modal-evento');

  // --- Modal para crear publicación ---
  setupModal('btn-abrir-modal-post', 'modal-post', 'btn-cerrar-modal-post', true);

  // --- Inicializar paginación de comentarios al cargar la página ---
  const listasComentarios = document.querySelectorAll('[id^="comment-list-"]');
  console.log('Listas de comentarios encontradas:', listasComentarios.length);
  
  listasComentarios.forEach(lista => {
    const postId = lista.id.replace('comment-list-', '');
    console.log('Inicializando paginación para post:', postId);
    updateCommentsPagination(postId);
  });

  // --- Verificar que las funciones globales estén disponibles ---
  console.log('Home.js cargado correctamente');
  console.log('toggleComments disponible:', typeof window.toggleComments);
  console.log('toggleReaction disponible:', typeof window.toggleReaction);

  // --- Event listeners para botones de comentarios ---
  document.addEventListener('click', function(e) {
    // Botón eliminar comentario
    if (e.target.classList.contains('eliminar-comentario')) {
      const commentId = e.target.dataset.commentId;
      const postId = e.target.dataset.postId;
      eliminarComentario(commentId, postId);
    }
    
    // Botón mostrar más comentarios
    if (e.target.classList.contains('mostrar-mas-comentarios')) {
      const postId = e.target.dataset.postId;
      mostrarMasComentarios(postId);
    }
  });

  function setupModal(btnOpenId, modalId, btnCloseId, tienePreview = false) {
    const btnOpen = document.getElementById(btnOpenId);
    const modal = document.getElementById(modalId);
    const btnClose = document.getElementById(btnCloseId);

    if (!btnOpen || !modal || !btnClose) return;

    btnOpen.setAttribute('aria-controls', modalId);
    btnOpen.setAttribute('aria-expanded', 'false');

    btnOpen.addEventListener('click', () => {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      modal.setAttribute('aria-hidden', 'false');
      btnOpen.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';

      const primerInput = modal.querySelector('input, textarea, button');
      if (primerInput) primerInput.focus();
    });

    btnClose.addEventListener('click', () => {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
      modal.setAttribute('aria-hidden', 'true');
      btnOpen.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      btnOpen.focus();

      if (tienePreview) clearPreview();
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        btnClose.click();
      }
    });

    modal.addEventListener('click', e => {
      if (e.target === modal) btnClose.click();
    });

    if (tienePreview) setupImagePreview(modal);
  }

  function setupImagePreview(modal) {
    const inputFile = modal.querySelector('#post-image');
    const previewContainer = modal.querySelector('#preview-container');
    const previewImage = modal.querySelector('#preview-image');
    const removeImageBtn = modal.querySelector('#remove-image');

    if (!inputFile || !previewContainer || !previewImage || !removeImageBtn) return;

    inputFile.addEventListener('change', e => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          previewImage.src = reader.result;
          previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
      } else clearPreview();
    });

    removeImageBtn.addEventListener('click', () => {
      inputFile.value = '';
      clearPreview();
    });

    function clearPreview() {
      previewImage.src = '';
      previewContainer.classList.add('hidden');
    }
  }

  // --- Función para crear el HTML completo del nuevo comentario ---
  function crearComentarioHTML(comment) {
    return `
    <div class="group relative bg-gray-100 rounded-lg p-3 shadow-sm hover:bg-gray-50 transition" data-visible="true">
      <div class="flex items-start gap-3">
        <img src="${comment.user_foto}" alt="Foto de ${comment.user_nombre}" class="w-8 h-8 rounded-full object-cover" loading="lazy">
        <div class="flex-1">
          <h4 class="text-sm font-semibold text-gray-800">${comment.user_nombre} ${comment.user_apellido}</h4>
          <p class="text-sm text-gray-700 mt-1">${comment.content}</p>
          <span class="text-xs text-gray-500 block mt-1">${comment.timestamp}</span>
        </div>
      </div>
      ${comment.puede_eliminar ? `
      <button
        class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition text-red-600 hover:text-red-800 focus:outline-none text-xs font-bold"
        data-delete-url="${comment.delete_url}"
        onclick="confirmarEliminarComentario(this.dataset.deleteUrl)"
        title="Eliminar comentario"
        aria-label="Eliminar comentario de ${comment.user_nombre} ${comment.user_apellido}"
        type="button">
        Eliminar
      </button>` : ''}
    </div>`;
  }

  // --- Envío asíncrono de comentarios (usando delegación de eventos) ---
  document.addEventListener('submit', async function(e) {
    // Solo procesar formularios de comentarios
    if (!e.target.classList.contains('comment-form')) return;
    
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const action = form.action;
    const csrfToken = form.querySelector('input[name="csrf_token"]').value;
    
    try {
      const response = await fetch(action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken
        }
      });
      const data = await response.json();
      if (data.success) {
        // Extraer postId
        const match = action.match(/\/post\/(\d+)\/comment/);
        const postId = match ? match[1] : null;
        if (!postId) return;
        
        const commentsList = document.getElementById(`comentarios-lista-${postId}`);
        const commentsButton = document.getElementById(`btn-comments-toggle-${postId}`);
        
        // Actualizar contador de comentarios dinámicamente
        if (commentsButton) {
          const countElement = commentsButton.querySelector('svg').nextSibling;
          if (countElement && countElement.nodeType === Node.TEXT_NODE) {
            const currentCount = parseInt(countElement.textContent.trim()) || 0;
            countElement.textContent = ` ${currentCount + 1}`;
          }
        }
        
        // Crear nuevo comentario con la nueva estructura
        const newComment = document.createElement('li');
        newComment.className = 'flex space-x-3 group relative';
        newComment.setAttribute('data-comment-id', data.comment_id);
        newComment.innerHTML = `
          ${data.puede_eliminar ? `
            <button class="eliminar-comentario absolute left-0 top-1 opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-700 text-sm w-5 h-5 flex items-center justify-center bg-white rounded-full shadow-sm z-10" 
                    data-comment-id="${data.comment_id}" 
                    data-post-id="${postId}"
                    title="Eliminar comentario">
              ✕
            </button>
          ` : ''}
          <img title="${data.comment_user}" class="w-8 h-8 rounded-full flex-shrink-0" src="${data.comment_user_avatar}" alt="Avatar">
          <div class="flex-1 bg-gray-100 rounded-xl px-3 py-2">
            <p class="text-gray-800 text-sm">${data.comment_content}</p>
          </div>
        `;
        
        // Agregar al principio de la lista
        if (commentsList) {
          commentsList.insertBefore(newComment, commentsList.firstChild);
        }
        
        // Limpiar formulario
        form.reset();
        
        // Mostrar sección de comentarios si estaba oculta
        const commentsSection = document.getElementById(`comments-section-${postId}`);
        if (commentsSection && commentsSection.classList.contains('hidden')) {
          commentsSection.classList.remove('hidden');
        }
        
      } else {
        mostrarToast(data.message || 'No se pudo agregar el comentario.');
      }
    } catch (error) {
      console.error('Error:', error);
      mostrarToast('Error al conectar con el servidor.');
    }
  });

  // --- Envío asíncrono del formulario de publicación ---
  const postForm = document.getElementById('post-form-modal');
  if (postForm) {
    postForm.addEventListener('submit', async e => {
      e.preventDefault();
      const formData = new FormData(postForm);
      
      try {
        const response = await fetch(postForm.action, {
          method: 'POST',
          body: formData,
          headers: { 
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || '' 
          }
        });
        const data = await response.json();
        if (data.success) {
          postForm.reset();
          const modal = document.getElementById('modal-post');
          if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            document.body.style.overflow = '';
          }
          mostrarToast('Publicación creada exitosamente');
          // Recargar la página para mostrar la nueva publicación
          setTimeout(() => window.location.reload(), 1000);
        } else {
          mostrarToast(data.message || 'Error al crear la publicación');
        }
      } catch (error) {
        console.error('Error:', error);
        mostrarToast('Error al conectar con el servidor');
      }
    });
  }

  // --- Envío asíncrono del formulario de evento ---
  const eventoForm = document.getElementById('form-evento');
  if (eventoForm) {
    eventoForm.addEventListener('submit', async e => {
      e.preventDefault();
      const formData = new FormData(eventoForm);
      try {
        const response = await fetch('/home/evento/create', {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || '' }
        });
        const data = await response.json();
        if (data.success) {
          eventoForm.reset();
          const modal = document.getElementById('modal-evento');
          if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            document.body.style.overflow = '';
          }
          mostrarToast('Evento creado correctamente.');
          setTimeout(() => actualizarEventos(), 500);
        } else {
          mostrarToast(data.message || 'No se pudo crear el evento.');
        }
      } catch {
        mostrarToast('Error al conectar con el servidor.');
      }
    });
  }

  // --- Recarga dinámica de publicaciones ---
  window.actualizarPublicaciones = async function() {
    const publicacionesContainer = document.querySelector('main ul.space-y-8');
    if (!publicacionesContainer) return;
    try {
      const resp = await fetch(window.location.pathname + window.location.search, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      const html = await resp.text();
      const temp = document.createElement('div');
      temp.innerHTML = html;
      const nuevasPubs = temp.querySelector('main ul.space-y-8');
      if (nuevasPubs) publicacionesContainer.innerHTML = nuevasPubs.innerHTML;
    } catch {}
  };

  // --- Recarga dinámica de eventos ---
  window.actualizarEventos = async function() {
    const eventosContainer = document.querySelector('aside ul[aria-live="polite"]');
    if (!eventosContainer) return;
    try {
      const resp = await fetch(window.location.pathname + window.location.search, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      const html = await resp.text();
      const temp = document.createElement('div');
      temp.innerHTML = html;
      const nuevosEventos = temp.querySelector('aside ul[aria-live="polite"]');
      if (nuevosEventos) eventosContainer.innerHTML = nuevosEventos.innerHTML;
    } catch {}
  };

  // --- Confirmar eliminación de comentario con diálogo visual ---
  window.confirmarEliminarComentario = async function (deleteUrl, commentId) {
    mostrarDialogoConfirmacion({
      mensaje: '¿Seguro que deseas eliminar este comentario?',
      onConfirm: async () => {
        try {
          const response = await fetch(deleteUrl, {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            }
          });
          const data = await response.json();
          if (data.success) {
            const commentElem = document.getElementById('comment-' + commentId);
            if (commentElem) {
              // Obtener postId del commentElem
              const commentList = commentElem.closest('[id^="comment-list-"]');
              const postId = commentList ? commentList.id.replace('comment-list-', '') : null;
              
              // Actualizar contador de comentarios dinámicamente
              if (postId) {
                const commentsButton = document.getElementById(`btn-comments-toggle-${postId}`);
                if (commentsButton) {
                  const countElement = commentsButton.querySelector('svg').nextSibling;
                  if (countElement && countElement.nodeType === Node.TEXT_NODE) {
                    const currentCount = parseInt(countElement.textContent.trim()) || 0;
                    countElement.textContent = ` ${Math.max(0, currentCount - 1)}`;
                  }
                }
                
                // Actualizar paginación después de eliminar
                setTimeout(() => updateCommentsPagination(postId), 500);
              }
              
              commentElem.classList.add('opacity-0');
              setTimeout(() => commentElem.remove(), 400);
            }
            mostrarToast('Comentario eliminado.');
          } else {
            mostrarToast(data.message || 'No se pudo eliminar el comentario.');
          }
        } catch {
          mostrarToast('Error al conectar con el servidor.');
        }
      }
    });
  };

  // --- Confirmar eliminación de evento con diálogo visual ---
  window.confirmarEliminarEvento = async function (deleteUrl) {
    mostrarDialogoConfirmacion({
      mensaje: '¿Seguro que deseas eliminar este evento?',
      onConfirm: async () => {
        try {
          const response = await fetch(deleteUrl, {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            }
          });
          const data = await response.json();
          if (data.success) {
            // Fade out visual
            const match = deleteUrl.match(/evento\/delete\/(\d+)/);
            const eventoId = match ? match[1] : null;
            if (eventoId) {
              const eventoElem = document.getElementById('evento-' + eventoId);
              if (eventoElem) {
                eventoElem.classList.add('opacity-0');
                setTimeout(() => eventoElem.remove(), 400);
              }
            }
            mostrarToast('Evento eliminado.');
            setTimeout(() => actualizarEventos(), 500);
          } else {
            mostrarToast(data.message || 'No se pudo eliminar el evento.');
          }
        } catch {
          mostrarToast('Error al conectar con el servidor.');
        }
      }
    });
  };

  // --- Diálogo de confirmación bonito ---
  window.mostrarDialogoConfirmacion = function({mensaje, onConfirm}) {
    // Elimina cualquier diálogo previo
    const existente = document.getElementById('dialogo-confirmacion-inside');
    if (existente) existente.remove();
    const dialogo = document.createElement('div');
    dialogo.id = 'dialogo-confirmacion-inside';
    dialogo.className = 'fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-sm';
    dialogo.innerHTML = `
      <div class="bg-white rounded-2xl shadow-2xl max-w-xs w-full p-6 flex flex-col items-center gap-4 animate-fadein">
        <svg class="w-12 h-12 text-blue-500 mb-2" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M12 20a8 8 0 100-16 8 8 0 000 16z"/></svg>
        <p class="text-center text-gray-800 text-lg font-medium">${mensaje}</p>
        <div class="flex gap-3 mt-2">
          <button id="btn-confirmar-inside" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-1 rounded transition">Sí, eliminar</button>
          <button id="btn-cancelar-inside" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold px-4 py-1 rounded transition">Cancelar</button>
        </div>
      </div>
    `;
    document.body.appendChild(dialogo);
    document.getElementById('btn-confirmar-inside').onclick = () => {
      dialogo.remove();
      onConfirm();
    };
    document.getElementById('btn-cancelar-inside').onclick = () => dialogo.remove();
  };

  // --- Toast minimalista para feedback visual ---
  window.mostrarToast = function (msg) {
    let toast = document.getElementById('toast-feedback');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast-feedback';
      toast.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-2 rounded-xl shadow-lg z-50 font-sfpro text-base opacity-0 transition-opacity';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.remove('opacity-0');
    toast.classList.add('opacity-100');
    setTimeout(() => toast.classList.add('opacity-0'), 2200);
  };
});
// --- Confirmar eliminación de publicación con diálogo visual ---
window.confirmarEliminarPublicacion = async function(deleteUrl, postId) {
  mostrarDialogoConfirmacion({
    mensaje: '¿Seguro que deseas eliminar esta publicación?',
    onConfirm: async () => {
      try {
        const response = await fetch(deleteUrl, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
          }
        });
        const data = await response.json();
        if (data.success) {
          const publicacionElem = document.getElementById('post-' + postId);
          if (publicacionElem) {
            publicacionElem.classList.add('opacity-0');
            setTimeout(() => publicacionElem.remove(), 400);
          }
          mostrarToast('Publicación eliminada.');
          setTimeout(() => actualizarPublicaciones(), 500);
        } else {
          mostrarToast(data.message || 'No se pudo eliminar la publicación.');
        }
      } catch {
        mostrarToast('Error al conectar con el servidor.');
      }
    }
  });
};

// --- FUNCIONES DE ELIMINACIÓN CON MODALES PERSONALIZADOS ---

// Variables globales para almacenar las URLs de eliminación
let currentDeleteUrl = null;
let currentCommentId = null;
let currentPostId = null;

// Función para confirmar eliminación de publicación
window.confirmarEliminarPublicacion = function(deleteUrl) {
  currentDeleteUrl = deleteUrl;
  const modal = document.getElementById('delete-publication-modal');
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
};

// Función para confirmar eliminación de evento
window.confirmarEliminarEvento = function(deleteUrl) {
  currentDeleteUrl = deleteUrl;
  const modal = document.getElementById('delete-event-modal');
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
};

// Función para confirmar eliminación de comentario
window.confirmarEliminarComentario = function(commentId, postId) {
  currentCommentId = commentId;
  currentPostId = postId;
  const modal = document.getElementById('delete-comment-modal');
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
};

// Función para cerrar modales de eliminación
function closeDeleteModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.classList.add('hidden');
  document.body.style.overflow = 'auto';
  currentDeleteUrl = null;
  currentCommentId = null;
  currentPostId = null;
}

// Función para realizar la eliminación
async function executeDelete(url) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    if (response.ok) {
      location.reload();
    } else {
      mostrarToast('Error al eliminar el elemento', 'error');
    }
  } catch (error) {
    mostrarToast('Error de conexión', 'error');
  }
}

// Función para eliminar comentario
async function eliminarComentario(commentId, postId) {
  try {
    const response = await fetch(`/home/delete_comment/${commentId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    if (response.ok) {
      // Remover el comentario del DOM
      const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
      if (commentElement) {
        commentElement.remove();
      }
      mostrarToast('Comentario eliminado', 'success');
    } else {
      mostrarToast('Error al eliminar el comentario', 'error');
    }
  } catch (error) {
    mostrarToast('Error de conexión', 'error');
  }
}

// Event listeners para los modales de eliminación
document.addEventListener('DOMContentLoaded', function() {
  // Modal de publicación
  const deletePublicationModal = document.getElementById('delete-publication-modal');
  const deletePublicationCancel = document.getElementById('delete-publication-cancel');
  const deletePublicationConfirm = document.getElementById('delete-publication-confirm');

  if (deletePublicationCancel) {
    deletePublicationCancel.addEventListener('click', () => closeDeleteModal('delete-publication-modal'));
  }

  if (deletePublicationConfirm) {
    deletePublicationConfirm.addEventListener('click', () => {
      if (currentDeleteUrl) {
        closeDeleteModal('delete-publication-modal');
        executeDelete(currentDeleteUrl);
      }
    });
  }

  if (deletePublicationModal) {
    deletePublicationModal.addEventListener('click', (e) => {
      if (e.target === deletePublicationModal) {
        closeDeleteModal('delete-publication-modal');
      }
    });
  }

  // Modal de evento
  const deleteEventModal = document.getElementById('delete-event-modal');
  const deleteEventCancel = document.getElementById('delete-event-cancel');
  const deleteEventConfirm = document.getElementById('delete-event-confirm');

  if (deleteEventCancel) {
    deleteEventCancel.addEventListener('click', () => closeDeleteModal('delete-event-modal'));
  }

  if (deleteEventConfirm) {
    deleteEventConfirm.addEventListener('click', () => {
      if (currentDeleteUrl) {
        closeDeleteModal('delete-event-modal');
        executeDelete(currentDeleteUrl);
      }
    });
  }

  if (deleteEventModal) {
    deleteEventModal.addEventListener('click', (e) => {
      if (e.target === deleteEventModal) {
        closeDeleteModal('delete-event-modal');
      }
    });
  }

  // Modal de comentario
  const deleteCommentModal = document.getElementById('delete-comment-modal');
  const deleteCommentCancel = document.getElementById('delete-comment-cancel');
  const deleteCommentConfirm = document.getElementById('delete-comment-confirm');

  if (deleteCommentCancel) {
    deleteCommentCancel.addEventListener('click', () => closeDeleteModal('delete-comment-modal'));
  }

  if (deleteCommentConfirm) {
    deleteCommentConfirm.addEventListener('click', () => {
      if (currentCommentId && currentPostId) {
        closeDeleteModal('delete-comment-modal');
        eliminarComentario(currentCommentId, currentPostId);
      }
    });
  }

  if (deleteCommentModal) {
    deleteCommentModal.addEventListener('click', (e) => {
      if (e.target === deleteCommentModal) {
        closeDeleteModal('delete-comment-modal');
      }
    });
  }

  // Event listeners para botones de eliminar comentario
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('eliminar-comentario')) {
      e.preventDefault();
      const commentId = e.target.getAttribute('data-comment-id');
      const postId = e.target.getAttribute('data-post-id');
      confirmarEliminarComentario(commentId, postId);
    }
  });

  // Cerrar modales con ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      if (!deletePublicationModal.classList.contains('hidden')) {
        closeDeleteModal('delete-publication-modal');
      } else if (!deleteEventModal.classList.contains('hidden')) {
        closeDeleteModal('delete-event-modal');
      } else if (!deleteCommentModal.classList.contains('hidden')) {
        closeDeleteModal('delete-comment-modal');
      }
    }
  });
});
