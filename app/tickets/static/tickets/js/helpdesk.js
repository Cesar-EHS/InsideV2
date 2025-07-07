// helpdesk.js - ÚNICO archivo JS para tickets
// Moderno, robusto, AJAX, feedback visual, soporte archivos

document.addEventListener('DOMContentLoaded', function () {
  // Toast minimalista
  window.mostrarToast = function (msg, tipo = 'success') {
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

  // MODAL NUEVO TICKET
  const modalNuevo = document.getElementById('modalNuevoTicket');
  document.getElementById('btnNuevoTicket')?.addEventListener('click', () => {
    modalNuevo.classList.remove('hidden');
    modalNuevo.classList.add('flex');
    setTimeout(() => modalNuevo.classList.add('backdrop-blur-md'), 10);
    document.body.style.overflow = 'hidden';
    const primerInput = modalNuevo.querySelector('input, textarea, select');
    if (primerInput) primerInput.focus();
  });
  document.querySelectorAll('.btn-cancelar-modal, #btnCancelarModal').forEach(btn => {
    btn?.addEventListener('click', () => {
      modalNuevo.classList.add('hidden');
      modalNuevo.classList.remove('flex');
      modalNuevo.classList.remove('backdrop-blur-md');
      document.body.style.overflow = '';
    });
  });
  window.addEventListener('click', (e) => {
    if (e.target === modalNuevo) {
      modalNuevo.classList.add('hidden');
      modalNuevo.classList.remove('flex');
      modalNuevo.classList.remove('backdrop-blur-md');
      document.body.style.overflow = '';
    }
  });
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      modalNuevo.classList.add('hidden');
      modalNuevo.classList.remove('flex');
      modalNuevo.classList.remove('backdrop-blur-md');
      document.body.style.overflow = '';
    }
  });

  // AJAX para crear ticket (Flask-WTF compatible)
  const formNuevo = document.getElementById('formNuevoTicket');
  formNuevo?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(formNuevo);
    const csrf = formNuevo.querySelector('input[name="csrf_token"]')?.value;
    const submitBtn = formNuevo.querySelector('button[type=submit], input[type=submit]');
    submitBtn.disabled = true;
    submitBtn.innerText = 'Enviando...';
    try {
      const resp = await fetch(formNuevo.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest', ...(csrf ? { 'X-CSRFToken': csrf } : {}) }
      });
      if (resp.redirected) {
        mostrarToast('Ticket creado correctamente');
        setTimeout(() => window.location.reload(), 1200);
        return;
      }
      let data;
      try { data = await resp.json(); } catch { data = {}; }
      if (resp.ok && (data.success || data.message === undefined)) {
        mostrarToast('Ticket creado correctamente');
        setTimeout(() => window.location.reload(), 1200);
      } else {
        mostrarToast(data.error || data.message || 'Error al crear ticket', 'error');
      }
    } catch {
      mostrarToast('Error de red', 'error');
    }
    submitBtn.disabled = false;
    submitBtn.innerText = 'Crear Ticket';
  });

  // MODAL DETALLE TICKET
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-ver-ticket')) {
      const id = e.target.dataset.id;
      console.log('Click en Ver ticket', id);
      (async () => {
        try {
          const res = await fetch(`/tickets/detalle/${id}`);
          const data = await res.json();
          console.log('Respuesta detalle:', data);
          showTicketDetailModal(data, id);
        } catch (err) {
          mostrarToast('Error al cargar ticket', 'error');
        }
      })();
    }
  });

  function showTicketDetailModal(data, ticketId) {
    let modal = document.getElementById('modalDetalleTicket');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'modalDetalleTicket';
      modal.className = 'fixed inset-0 bg-black/40 z-50 flex items-center justify-center';
      document.body.appendChild(modal);
    }
    // Detectar si el usuario es encargado (puede cambiar estatus SOLO si el ticket es de su categoría)
    const puedeGestionar = window.puestos_encargados && window.puestos_encargados.includes(window.mi_puesto_id) && data && data.categoria && (
      (window.puestos_encargados.find(id => id === window.mi_puesto_id) && data.categoria === getCategoriaByPuesto(window.mi_puesto_id))
    );
    // Obtener CSRF token global (de un input oculto en el DOM)
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    let selectEstatus = '';
    if (puedeGestionar) {
      selectEstatus = `
        <form id="formEstatusTicket" class="flex items-center gap-2 mb-4">
          <input type="hidden" name="csrf_token" value="${csrfToken || ''}">
          <label class="text-sm font-medium">Estatus:</label>
          <select name="estatus" class="border rounded px-2 py-1 bg-white/80">
            <option value="Abierto" ${data.estatus === 'Abierto' ? 'selected' : ''}>Abierto</option>
            <option value="En progreso" ${data.estatus === 'En progreso' ? 'selected' : ''}>En progreso</option>
            <option value="Resuelto" ${data.estatus === 'Resuelto' ? 'selected' : ''}>Resuelto</option>
          </select>
          <button type="submit" class="bg-[#fab522] text-white px-3 py-1 rounded hover:bg-[#e0a800]">Guardar</button>
        </form>
      `;
    }
    modal.innerHTML = `
      <div class="bg-white/90 backdrop-blur-xl rounded-2xl w-full max-w-2xl p-6 relative glassmorphism-modal animate-fadein shadow-xl border border-gray-100">
        <button class="absolute top-3 right-3 text-gray-500 hover:text-gray-800 text-2xl font-bold" onclick="document.getElementById('modalDetalleTicket').classList.add('hidden');document.getElementById('modalDetalleTicket').classList.remove('flex');">&times;</button>
        <h2 class="text-2xl font-semibold mb-2 font-sfpro text-[#3b3b3c]">${data.titulo}</h2>
        <div class="mb-2 text-[#3b3b3c] text-lg">${data.descripcion}</div>
        <div class="flex flex-wrap gap-3 mb-4">
          <span class="px-2 py-1 rounded text-xs text-white ${getPriorityColor(data.prioridad)}">${data.prioridad}</span>
          <span class="px-2 py-1 rounded text-xs bg-[#fab522]/80 text-[#3b3b3c]">${data.estatus}</span>
          <span class="px-2 py-1 rounded text-xs bg-gray-200 text-[#3b3b3c]">${data.fecha}</span>
          ${data.archivo ? `<a href="/tickets/archivo/${data.archivo}" target="_blank" class="underline text-[#fab522]">Archivo</a>` : ''}
        </div>
        ${selectEstatus}
        <div class="mb-4">
          <h3 class="font-semibold mb-1">Comentarios</h3>
          <div class="space-y-2 max-h-56 overflow-y-auto pr-2" id="comentariosTicket">
            ${data.comentarios.map(c => `
              <div class="rounded-xl p-3 bg-white/95 shadow flex flex-col gap-1 animate-fadein border border-gray-100">
                <div class="text-sm font-semibold text-[#3b3b3c] font-sfpro">${c.emisor}</div>
                <div class="text-[#3b3b3c]">${c.contenido}</div>
                ${c.imagen ? `<img src="/tickets/archivo/${c.imagen}" class="max-h-32 rounded mt-1" />` : ''}
                <div class="text-xs text-gray-500">${c.fecha}</div>
              </div>
            `).join('')}
          </div>
        </div>
        <form id="formComentarTicket" class="flex flex-col gap-2 mt-2" enctype="multipart/form-data">
          <input type="hidden" name="csrf_token" value="${csrfToken || ''}">
          <textarea name="contenido" class="border rounded-xl p-2 bg-white/70" placeholder="Agregar comentario..." required></textarea>
          <input type="file" name="imagen" accept="image/*,application/pdf" class="mb-2" />
          <button type="submit" class="bg-[#fab522] text-[#3b3b3c] px-4 py-2 rounded-xl hover:bg-[#ffe08a] self-end font-sfpro">Comentar</button>
        </form>
      </div>
    `;
    // Asegura que el modal se muestre
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.onclick = e => { if (e.target === modal) modal.remove(); };
    // AJAX comentar
    const form = document.getElementById('formComentarTicket');
    form.onsubmit = async function(e) {
      e.preventDefault();
      const formData = new FormData(form);
      // Añadir CSRF token si existe
      const csrf = form.querySelector('input[name="csrf_token"]')?.value;
      if (csrf) formData.set('csrf_token', csrf); // asegurar que el valor es el correcto
      const submitBtn = form.querySelector('button[type=submit], input[type=submit]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Enviando...';
      }
      let resp, d = {};
      try {
        resp = await fetch(`/tickets/comentar/${data.id}`, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        // Si la respuesta es un redirect (por ejemplo, sesión expirada)
        if (resp.redirected) {
          window.location.href = resp.url;
          return;
        }
        try { d = await resp.json(); } catch { d = {}; }
        if (resp.ok && d.success && d.comentario) {
          mostrarToast('Comentario agregado');
          // Agregar el comentario al DOM sin recargar
          const comentariosDiv = document.getElementById('comentariosTicket');
          if (comentariosDiv) {
            const nuevo = document.createElement('div');
            nuevo.className = 'rounded-xl p-3 bg-white/95 shadow flex flex-col gap-1 animate-fadein border border-gray-100';
            nuevo.innerHTML = `
              <div class="text-sm font-semibold text-[#3b3b3c] font-sfpro">${d.comentario.emisor}</div>
              <div class="text-[#3b3b3c]">${d.comentario.contenido}</div>
              ${d.comentario.imagen ? `<img src="/tickets/archivo/${d.comentario.imagen}" class="max-h-32 rounded mt-1" />` : ''}
              <div class="text-xs text-gray-500">${d.comentario.fecha}</div>
            `;
            comentariosDiv.appendChild(nuevo);
          }
          form.reset();
        } else {
          mostrarToast(d.error || d.message || 'Error al comentar', 'error');
        }
      } catch (err) {
        mostrarToast('Error de red', 'error');
      }
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Comentar';
      }
    };
    // AJAX cambiar estatus
    const formEstatus = document.getElementById('formEstatusTicket');
    if (formEstatus) {
      formEstatus.onsubmit = async function(e) {
        e.preventDefault();
        const estatus = formEstatus.estatus.value;
        const csrf = formEstatus.querySelector('input[name="csrf_token"]')?.value;
        let body = new FormData();
        body.append('estatus', estatus);
        if (csrf) body.append('csrf_token', csrf);
        const submitBtn = formEstatus.querySelector('button[type=submit], input[type=submit]');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerText = 'Guardando...';
        }
        let resp, d = {};
        try {
          resp = await fetch(`/tickets/estatus/${data.id}`, {
            method: 'POST',
            body: body,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
          });
          if (resp.redirected) {
            window.location.href = resp.url;
            return;
          }
          try { d = await resp.json(); } catch { d = {}; }
          if (resp.ok && d.success) {
            mostrarToast('Estatus actualizado');
            modal.remove();
            setTimeout(() => window.location.reload(), 1000);
          } else {
            mostrarToast(d.error || d.message || 'Error al cambiar estatus', 'error');
          }
        } catch (err) {
          mostrarToast('Error de red', 'error');
        }
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerText = 'Guardar';
        }
      };
    }
  }

  function getPriorityColor(prio) {
    if (prio === 'Alta') return 'bg-[#fab522] text-[#3b3b3c]';
    if (prio === 'Urgente') return 'bg-red-700';
    if (prio === 'Media') return 'bg-[#ffe08a] text-[#3b3b3c]';
    return 'bg-gray-300 text-[#3b3b3c]';
  }

  // Helper para obtener la categoría por puesto (debe coincidir con backend)
  function getCategoriaByPuesto(puestoId) {
    const map = {
      10: 'Soporte Sistemas',
      3: 'Requisición Compras',
      24: 'Desarrollo Organizacional',
      7: 'Capacitación Técnica',
      9: 'Diseño Institucional',
      2: 'Recursos Humanos',
      6: 'Soporte EHSmart'
    };
    return map[puestoId] || null;
  }

  // Manejo de tabs Gestión/Mis tickets
  const tabGestion = document.getElementById('tab-gestion');
  const tabMis = document.getElementById('tab-mis');
  const contentGestion = document.getElementById('tab-content-gestion');
  const contentMis = document.getElementById('tab-content-mis');
  if (tabGestion && contentGestion) {
    tabGestion.onclick = function() {
      tabGestion.classList.add('border-b-2', 'border-[#fab522]');
      tabMis.classList.remove('border-b-2', 'border-[#fab522]');
      contentGestion.classList.remove('hidden');
      contentMis.classList.add('hidden');
      tabGestion.blur();
    };
  }
  if (tabMis && contentMis) {
    tabMis.onclick = function() {
      tabMis.classList.add('border-b-2', 'border-[#fab522]');
      if (tabGestion) tabGestion.classList.remove('border-b-2', 'border-[#fab522]');
      contentMis.classList.remove('hidden');
      if (contentGestion) contentGestion.classList.add('hidden');
      tabMis.blur();
    };
  }

  // Animaciones y glassmorphism
  const style = document.createElement('style');
  style.innerHTML = `
  @keyframes fadein { from { opacity: 0; transform: translateY(16px) scale(.98); } to { opacity: 1; transform: none; } }
  .animate-fadein { animation: fadein .5s cubic-bezier(.4,0,.2,1); }
  .glassmorphism-modal { box-shadow: 0 8px 32px 0 rgba(31,38,135,0.2); border: 1px solid rgba(255,255,255,0.18); }
  .font-sfpro { font-family: 'SF Pro Display', 'Inter', Arial, sans-serif; }
  `;
  document.head.appendChild(style);
});
