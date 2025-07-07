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

  // --- Modal para crear publicación ---
  setupModal('btn-abrir-modal-post', 'modal-post', 'btn-cerrar-modal-post', true);

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

  // --- Toggle comentarios ---
  window.toggleComments = function (postId) {
    const commentsSection = document.getElementById(`comments-section-${postId}`);
    const btnToggle = document.getElementById(`btn-comments-toggle-${postId}`);
    if (!commentsSection || !btnToggle) return;

    const isHidden = commentsSection.classList.toggle('hidden');
    btnToggle.setAttribute('aria-expanded', (!isHidden).toString());
  };

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

// --- Envío asíncrono de comentarios ---
document.querySelectorAll('form.comment-form').forEach(form => {
  form.addEventListener('submit', async e => {
    e.preventDefault();
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
        const commentList = document.getElementById(`comment-list-${postId}`);
        // Crear comentario visual
        const newComment = document.createElement('div');
        newComment.id = `comment-${data.comment_id}`;
        newComment.className = 'flex items-start gap-3 bg-white/90 rounded-xl shadow border border-gray-100 px-4 py-2 transition animate-fadein';
        newComment.innerHTML = `
          <img src="${data.comment_user_avatar}" alt="Foto de ${data.comment_user}" class="w-9 h-9 rounded-full object-cover border border-yellow-200">
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold text-gray-900 font-sfpro">${data.comment_user}</span>
              <span class="text-xs text-gray-400">${data.comment_timestamp}</span>
            </div>
            <p class="text-gray-800 whitespace-pre-wrap text-sm leading-normal mt-1">${data.comment_content}</p>
          </div>
          ${data.puede_eliminar ? `<button class='ml-2 text-red-500 hover:text-red-700 focus:outline-none text-xs font-bold bg-transparent' data-delete-url='${data.delete_url}' onclick='confirmarEliminarComentario(this.dataset.deleteUrl, "${data.comment_id}")' title='Eliminar comentario' aria-label='Eliminar comentario' type='button'>✕</button>` : ''}
        `;
        commentList.insertBefore(newComment, commentList.firstChild);
        form.reset();
      } else {
        mostrarToast(data.message || 'No se pudo agregar el comentario.');
      }
    } catch {
      mostrarToast('Error al conectar con el servidor.');
    }
  });
});

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
          headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value }
        });
        const data = await response.json();
        if (data.success) {
          postForm.reset();
          const previewContainer = document.getElementById('preview-container');
          const previewImage = document.getElementById('preview-image');
          if (previewContainer && previewImage) {
            previewContainer.classList.add('hidden');
            previewImage.src = '';
          }
          const modal = document.getElementById('modal-post');
          if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            document.body.style.overflow = '';
          }
          // Recargar solo la lista de publicaciones
          actualizarPublicaciones();
        }
      } catch {}
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

  // --- Manejo de reacción con corazón ---
  window.toggleReaction = async function (button) {
    const postId = button.getAttribute('data-post-id');
    const reactionType = button.getAttribute('data-reaction');

    try {
      const response = await fetch(`/home/add_reaction/${postId}?reaction_type=${reactionType}`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        }
      });

      if (!response.ok) throw new Error('Error en la respuesta del servidor');

      const data = await response.json();

      if (data.success) {
        const countSpan = document.getElementById('love-count-' + postId);
        if (countSpan) countSpan.textContent = data.love_count;

        button.classList.toggle('text-red-600');
        button.classList.toggle('text-gray-600');
      } else {
        alert(data.message || 'Error al enviar reacción.');
      }
    } catch {
      alert('Error al conectar con el servidor.');
    }
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
        <svg class="w-12 h-12 text-yellow-400 mb-2" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M12 20a8 8 0 100-16 8 8 0 000 16z"/></svg>
        <p class="text-center text-gray-800 text-lg font-medium">${mensaje}</p>
        <div class="flex gap-3 mt-2">
          <button id="btn-confirmar-inside" class="bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold px-4 py-1 rounded transition">Sí, eliminar</button>
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

  // --- Mostrar más comentarios de 5 en 5 ---
  window.mostrarMasComentarios = function(postId) {
    const lista = document.getElementById(`comment-list-${postId}`);
    if (!lista) return;

    const ocultos = lista.querySelectorAll('.group[data-visible="false"]');
    const aMostrar = Array.from(ocultos).slice(0, 5);

    aMostrar.forEach(comment => {
      comment.style.display = 'block';
      comment.setAttribute('data-visible', 'true');
    });

    if (lista.querySelectorAll('.group[data-visible="false"]').length === 0) {
      const btn = document.querySelector(`#comments-section-${postId} button[onclick*="mostrarMasComentarios"]`);
      if (btn) btn.remove();
    }
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
