document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('btn-agregar-seccion');
  const contenedor = document.getElementById('contenedor-secciones');
  const modal = document.getElementById('modal-actividad');
  const cerrarModal = document.getElementById('cerrar-modal-actividad');
  const modalExamen = document.getElementById('modal-examen');
  const btnExamen = document.querySelector('#modal-tab-actividades button:nth-child(3)');

  function actualizarNumeros() {
    const cards = contenedor.querySelectorAll('.seccion-card');
    cards.forEach((card, idx) => {
      const numDiv = card.querySelector('.seccion-numero');
      if (numDiv) numDiv.textContent = idx + 1;

      // Actualizamos los datos de cada sección para que tengan el indice correcto
      const parentContainer = card.closest('.card-container');
      parentContainer.querySelector('input[type="text"]').name = `secciones[${idx}][nombre]`;
      parentContainer.querySelector('textarea').name = `secciones[${idx}][descripcion]`;
    });
  }

  btn.addEventListener('click', function () {
    const nuevaSeccion = document.createElement('div');
    nuevaSeccion.className = 'card-container mb-4';

    nuevaSeccion.innerHTML = `
        <div class="seccion-card flex w-full max-w-xs h-28 mx-auto overflow-hidden rounded-xl shadow-lg bg-white relative transition-transform duration-200 hover:-translate-y-2 hover:shadow-2xl hover:scale-105 cursor-pointer">
            <button type="button" class="absolute top-2 right-2 text-gray-400 hover:text-red-500 text-xl font-bold focus:outline-none eliminar-seccion" title="Eliminar sección">&times;</button>
            <div class="flex items-center justify-center w-1/3 bg-[color:var(--inside-yellow)] text-white text-2xl font-bold seccion-numero rounded-l-xl h-full">
                </div>
            <div class="flex flex-col justify-center w-2/3 p-3">
            <div class="font-bold text-base text-gray-800 mb-1">Nueva sección</div>
                <div class="text-gray-500 text-xs">
                    Presione aquí para editar la sección.
                </div>
            </div>
        </div>

        <div class="edit-box h-0 overflow-hidden bg-white rounded-xl shadow-lg -mt-4 transition-all duration-300 ease-in-out">
            <div class="p-2">
                <div class="mb-2">
                    <label for="secciones-${index}-nombre" class="block text-sm font-semibold mb-1">Nombre</label>
                    <input type="text" id="secciones-${index}-nombre" name="secciones[${index}][nombre]" class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400">
                </div>
                <div>
                    <label for="secciones-${index}-descripcion" class="block text-sm font-semibold mb-1">Descripción</label>
                    <textarea id="secciones-${index}-descripcion" name="secciones[${index}][descripcion]" rows="2" class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"></textarea>
                </div>
            </div>
        </div>
        `;

    // Evento para eliminar la tarjeta
    nuevaSeccion.querySelector('.eliminar-seccion').addEventListener('click', function (e) {
      e.stopPropagation();
      nuevaSeccion.remove();
      actualizarNumeros();
    });

    // Evento para abrir el modal al hacer clic en la tarjeta (excepto en el botón eliminar)
    nuevaSeccion.querySelector('.seccion-card').addEventListener('click', function (e) {
        // Asegúrate de que el clic no sea en el botón de eliminar
        if (!e.target.classList.contains('eliminar-seccion')) {
            const editBox = nuevaSeccion.querySelector('.edit-box');
            
            // Alterna la clase 'active' para mostrar u ocultar
            editBox.classList.toggle('active');
        }
    });

    contenedor.appendChild(nuevaSeccion);
    actualizarNumeros();
  });

  // Cerrar el modal
  cerrarModal.addEventListener('click', function () {
    modal.classList.add('hidden');
  });

  // Opcional: cerrar modal al hacer clic fuera del contenido
 /*  modal.addEventListener('click', function (e) {
    if (e.target === modal) {
      modal.classList.add('hidden');
    }
  }); */


  if (btnExamen && modal && modalExamen) {
    btnExamen.addEventListener('click', function () {
        modal.classList.add('hidden');
        modalExamen.classList.remove('hidden');
        if (typeof showTabExamen === 'function') {
        showTabExamen('datos');
      }
    });
  }
  const cerrarModalExamen = document.getElementById('cerrar-modal-examen');
  if (cerrarModalExamen && modalExamen && modal) {
    cerrarModalExamen.addEventListener('click', function () {
        modalExamen.classList.add('hidden');
        modal.classList.remove('hidden');
        showModalTab('actividades'); // Opcional: muestra la pestaña de actividades
    });
}
});

// --- Tabs para el modal de actividad ---
function showModalTab(tab) {
  const datosBtn = document.getElementById('tab-datos-btn');
  const actividadesBtn = document.getElementById('tab-actividades-btn');
  const datosTab = document.getElementById('modal-tab-datos');
  const actividadesTab = document.getElementById('modal-tab-actividades');

  if (tab === 'datos') {
    datosBtn.classList.add('border-yellow-400');
    datosBtn.classList.remove('border-transparent');
    actividadesBtn.classList.remove('border-yellow-400');
    actividadesBtn.classList.add('border-transparent');
    datosTab.classList.remove('hidden');
    actividadesTab.classList.add('hidden');
  } else {
    actividadesBtn.classList.add('border-yellow-400');
    actividadesBtn.classList.remove('border-transparent');
    datosBtn.classList.remove('border-yellow-400');
    datosBtn.classList.add('border-transparent');
    actividadesTab.classList.remove('hidden');
    datosTab.classList.add('hidden');
  }
}