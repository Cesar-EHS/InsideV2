function abrirSeccionModal(titulo, contenido) {
  const overlay = document.getElementById('seccion-modal-overlay');
  const modal = document.getElementById('seccion-modal');
  document.getElementById('seccion-modal-titulo').textContent = titulo;
  document.getElementById('seccion-modal-contenido').textContent = contenido;

  overlay.classList.remove('hidden');
  setTimeout(() => {
    overlay.classList.add('opacity-100');
    modal.classList.remove('opacity-0', 'scale-95');
    modal.classList.add('opacity-100', 'scale-100');
  }, 10);
}

function cerrarSeccionModal() {
  const overlay = document.getElementById('seccion-modal-overlay');
  const modal = document.getElementById('seccion-modal');
  overlay.classList.remove('opacity-100');
  modal.classList.remove('opacity-100', 'scale-100');
  modal.classList.add('opacity-0', 'scale-95');
  setTimeout(() => {
    overlay.classList.add('hidden');
  }, 300);
}