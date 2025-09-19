// La función showActivityView debe estar en el ámbito global para que los onclick la puedan encontrar
function showActivityView(view) {
  const selectView = document.getElementById('select-activity-view');
  const archivoView = document.getElementById('archivo-view');
  const videoView = document.getElementById('video-view');
  const examenView = document.getElementById('examen-view'); // <-- AÑADIDO

  // Ocultar todas las vistas primero
  selectView.classList.add('hidden');
  archivoView.classList.add('hidden');
  videoView.classList.add('hidden');
  if (examenView) examenView.classList.add('hidden'); // <-- AÑADIDO

  // Mostrar la vista seleccionada
  if (view === 'select') {
    selectView.classList.remove('hidden');
  } else if (view === 'archivo') {
    archivoView.classList.remove('hidden');
  } else if (view === 'video') {
    videoView.classList.remove('hidden');
  } else if (view === 'examen') { // <-- AÑADIDO: Caso para el examen
    if (examenView) examenView.classList.remove('hidden');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const btnArchivo = document.getElementById('btn-archivo');
  const btnVideo = document.getElementById('btn-video');
  const btnExamen = document.getElementById('btn-examen');

  // === Event Listeners para los botones de tipo de actividad ===
  if (btnArchivo) {
    btnArchivo.addEventListener('click', function() {
      showActivityView('archivo');
    });
  }

  if (btnVideo) {
    btnVideo.addEventListener('click', function() {
      showActivityView('video');
    });
  }

  if (btnExamen) {
    btnExamen.addEventListener('click', function() {
      showActivityView('examen');
    });
  }
  
  // NOTA: Los listeners para los botones de regreso se eliminaron
  // porque ya usas onclick="" en el HTML, lo cual es más simple y funciona bien.
  // La lógica para 'visualizar' también se eliminó porque se maneja con las pestañas del modal.

  // === Configuración Inicial ===
  showActivityView('select');
});