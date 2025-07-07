// search.js - Buscador global solo al presionar Enter

document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('form[role="search"] input[name="q"]');
  const searchForm = document.querySelector('form[role="search"]');
  const resultsContainer = document.getElementById('search-results');
  let lastTerm = '';

  if (!searchForm || !searchInput || !resultsContainer) return;

  // Captura el submit del header
  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const term = searchInput.value.trim();
    if (term === lastTerm || !term) return;
    lastTerm = term;
    doSearch(term);
  });

  // Si hay ?q= en la URL, cargar resultados al entrar/recargar
  const params = new URLSearchParams(window.location.search);
  const initialTerm = params.get('q') || '';
  if (initialTerm) {
    searchInput.value = initialTerm;
    doSearch(initialTerm);
    lastTerm = initialTerm;
  }

  function updateURL(term) {
    const url = new URL(window.location);
    if (term) {
      url.searchParams.set('q', term);
    } else {
      url.searchParams.delete('q');
    }
    window.history.replaceState({}, '', url);
  }

  function doSearch(term) {
    if (!term) {
      resultsContainer.innerHTML = '<p class="text-gray-500 text-lg text-center">Escribe tu búsqueda y presiona Enter.</p>';
      updateURL('');
      return;
    }
    fetch(`/buscar/api?q=${encodeURIComponent(term)}`)
      .then(res => res.json())
      .then(data => {
        resultsContainer.innerHTML = renderResults(data, term);
      })
      .catch(() => {
        resultsContainer.innerHTML = '<p class="text-red-500">Error al buscar. Intenta de nuevo.</p>';
      });
    updateURL(term);
  }
});

function renderResults(data, term) {
  if (!data) return '';
  let html = `<h1 class="text-3xl font-bold mb-8 text-right">Resultados de búsqueda para: <span class="text-[#fab522]">"${term}"</span></h1>`;
  if (!data.publicaciones.length && !data.eventos.length && !data.documentos.length && !data.tickets.length) {
    html += '<p class="text-gray-500 text-lg">No se encontraron resultados para su búsqueda.</p>';
  }
  // Publicaciones
  if (data.publicaciones && data.publicaciones.length) {
    html += '<section class="mb-10"><h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">📢 Publicaciones</h2><ul class="space-y-3">';
    data.publicaciones.forEach(pub => {
      html += `<li class="bg-white rounded-xl shadow p-4 flex gap-3 items-start animate-fade-in">
        <img src="${pub.user_avatar}" alt="Foto de ${pub.user_nombre}" class="w-8 h-8 rounded-full object-cover border border-yellow-100 bg-gray-100 flex-shrink-0" loading="lazy" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="font-semibold text-gray-800 text-sm truncate">${pub.user_nombre}</span>
            <span class="text-xs text-gray-400">${pub.timestamp}</span>
          </div>
          <p class="text-gray-700 text-sm mb-1 truncate">${pub.content}</p>
          ${pub.image_filename ? `<img src="${pub.image_url}" alt="Imagen publicación" class="rounded-lg max-h-32 mt-1 border border-gray-100 shadow-sm" loading="lazy" />` : ''}
        </div>
      </li>`;
    });
    html += '</ul></section>';
  }
  // Eventos
  if (data.eventos && data.eventos.length) {
    html += '<section class="mb-10"><h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">📅 Eventos</h2><ul class="space-y-3">';
    data.eventos.forEach(ev => {
      html += `<li class="bg-white rounded-xl shadow p-4 animate-fade-in">
        <h3 class="text-lg font-semibold text-[#3b3b3c] mb-1 truncate">${ev.titulo}</h3>
        <p class="text-gray-700 text-sm mb-1 truncate">${ev.descripcion}</p>
        <div class="text-xs text-gray-500 flex flex-wrap gap-4">
          <span>Fecha: <strong>${ev.fecha}</strong></span>
          <span>Hora: <strong>${ev.hora}</strong></span>
          ${ev.link_teams ? `<a href="${ev.link_teams}" target="_blank" rel="noopener" class="text-[#fab522] hover:text-[#cfa018] font-semibold">Enlace Teams</a>` : ''}
          <span>Creado: <strong>${ev.created_at}</strong></span>
        </div>
      </li>`;
    });
    html += '</ul></section>';
  }
  // Documentos
  if (data.documentos && data.documentos.length) {
    html += '<section class="mb-10"><h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">🗂️ Documentos</h2><ul class="space-y-3">';
    data.documentos.forEach(doc => {
      html += `<li class="bg-white rounded-xl shadow p-4 flex justify-between items-center animate-fade-in">
        <div class="min-w-0">
          <h3 class="text-base font-semibold text-[#3b3b3c] truncate">${doc.nombre}</h3>
          <p class="text-xs text-gray-600 truncate">Tipo: <strong>${doc.tipo}</strong> | Categoría: <strong>${doc.categoria}</strong> | Fecha de carga: <strong>${doc.fecha_carga}</strong></p>
        </div>
        ${doc.archivo_url ? `<a href="${doc.archivo_url}" target="_blank" class="text-[#fab522] hover:text-[#cfa018] font-semibold transition-colors duration-200 text-xs">Descargar</a>` : ''}
      </li>`;
    });
    html += '</ul></section>';
  }
  // Tickets
  if (data.tickets && data.tickets.length) {
    html += '<section><h2 class="text-2xl font-semibold mb-4 flex items-center gap-2">🧰 Centro de Ayuda</h2><ul class="space-y-3">';
    data.tickets.forEach(ticket => {
      html += `<li class="bg-white rounded-xl shadow p-4 flex gap-3 items-start animate-fade-in">
        <img src="${ticket.user_avatar}" alt="Foto de ${ticket.user_nombre}" class="w-7 h-7 rounded-full object-cover border border-yellow-100 bg-gray-100 flex-shrink-0" loading="lazy" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="font-semibold text-gray-800 text-sm truncate">${ticket.user_nombre}</span>
            <span class="text-xs text-gray-400">${ticket.fecha_creacion}</span>
          </div>
          <h3 class="text-base font-semibold text-[#3b3b3c] mb-0.5 truncate">${ticket.titulo}</h3>
          <p class="text-gray-700 text-sm mb-1 truncate">${ticket.descripcion}</p>
          <div class="flex flex-wrap gap-3 text-xs text-gray-500 mb-1">
            <span>Prioridad: <strong>${ticket.prioridad}</strong></span>
            <span>Estado: <strong>${ticket.estatus}</strong></span>
            <span>Categoría: <strong>${ticket.categoria}</strong></span>
          </div>
          ${ticket.archivo_url ? `<a href="${ticket.archivo_url}" class="inline-block text-[#fab522] hover:text-[#cfa018] font-semibold transition-colors duration-200 text-xs" target="_blank" rel="noopener noreferrer">Descargar archivo adjunto</a>` : ''}
        </div>
      </li>`;
    });
    html += '</ul></section>';
  }
  return html;
}

// Animación fade-in y estilos compactos
const style = document.createElement('style');
style.innerHTML = `.animate-fade-in { animation: fadeIn 0.5s; } @keyframes fadeIn { from { opacity: 0; transform: translateY(10px);} to { opacity: 1; transform: none;} }
  #search-results img { max-width: 56px !important; max-height: 56px !important; border-radius: 9999px; object-fit: cover; border: 2px solid #fab52222; background: #f3f3f3; }
  #search-results .bg-white { margin-bottom: 0.5rem; padding: 1.2rem 1.5rem; border-radius: 1.2rem; box-shadow: 0 2px 12px #0001; display: flex; align-items: flex-start; gap: 1rem; }
  #search-results h2 { margin-top: 2rem; margin-bottom: 1rem; font-size: 1.3rem; font-weight: 600; color: #fab522; }
`;
document.head.appendChild(style);
