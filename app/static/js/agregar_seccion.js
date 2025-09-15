document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('btn-agregar-seccion');
  const contenedor = document.getElementById('contenedor-secciones');
  const btnSiguiente = document.getElementById('btn-siguiente-secciones');

  function actualizarSecciones() {
    const cards = contenedor.querySelectorAll('.seccion-card');
    cards.forEach((card, idx) => {
      const parentContainer = card.closest('.card-container');
      const numDiv = card.querySelector('.seccion-numero');
      if (numDiv) numDiv.textContent = idx + 1;

      // Actualizamos los atributos name de los campos, titulo y descripción
      const inputNombre = parentContainer.querySelector('.edit-nombre');
      const inputDescripcion = parentContainer.querySelector('.edit-descripcion');

      if(inputNombre) inputNombre.name = `secciones[${idx}][nombre]`;
      if(inputDescripcion) inputDescripcion.name = `secciones[${idx}][descripcion]`;
    });
  }

  if(btnSiguiente) {
    btnSiguiente.addEventListener('click', function(event) {
      // Evita que el formulario se envíe
      event.preventDefault();
      
      // Llama a la función showTab() para cambiar a la pestaña de secciones
      window.showTab('secciones');
    });
  }

  btn.addEventListener('click', function () {
    const nuevaSeccion = document.createElement('div');
    nuevaSeccion.className = 'card-container mb-4';
    const index = contenedor.children.length;

    nuevaSeccion.innerHTML = `
      <div class="seccion-card flex w-full max-w-xs h-28 mx-auto overflow-hidden rounded-xl shadow-lg bg-white relative transition-transform duration-200 hover:-translate-y-2 hover:shadow-2xl hover:scale-105 cursor-pointer">
        <button type="button" class="absolute top-2 right-2 text-gray-400 hover:text-red-500 text-xl font-bold focus:outline-none eliminar-seccion" title="Eliminar sección">&times;</button>
        <div class="flex items-center justify-center w-1/3 bg-[color:var(--inside-yellow)] text-white text-2xl font-bold seccion-numero rounded-l-xl h-full"></div>
        <div class="flex flex-col justify-center w-2/3 p-3">
          <div class="font-bold text-base text-gray-800 mb-1 nombre-card">Nueva sección</div>
          <div class="text-gray-500 text-xs descripcion-card">Presione aquí para editar la sección.</div>
        </div>
      </div>

      <div class="edit-box h-0 overflow-hidden bg-white rounded-xl shadow-lg -mt-4 transition-all duration-300 ease-in-out">
        <div class="p-2">
          <div class="mb-2">
            <label for="secciones-${index}-nombre" class="block text-sm font-semibold mb-1">Nombre</label>
            <input type="text" id="secciones-${index}-nombre" name="secciones[${index}][nombre]" class="text-sm edit-nombre w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400">
          </div>
          <div>
            <label for="secciones-${index}-descripcion" class="block text-sm font-semibold mb-1">Descripción</label>
            <textarea id="secciones-${index}-descripcion" name="secciones[${index}][descripcion]" rows="2" class="text-sm edit-descripcion w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"></textarea>
          </div>
        </div>
      </div>
    `;
    contenedor.appendChild(nuevaSeccion);

    // Referencias a elementos
    const nombreCard = nuevaSeccion.querySelector('.nombre-card');
    const descripcionCard = nuevaSeccion.querySelector('.descripcion-card');
    const inputNombre = nuevaSeccion.querySelector('.edit-nombre');
    const inputDescripcion = nuevaSeccion.querySelector('.edit-descripcion');

    // Evento para eliminar la tarjeta
    nuevaSeccion.querySelector('.eliminar-seccion').addEventListener('click', function (e) {
      e.stopPropagation();
      nuevaSeccion.remove();
      actualizarSecciones();
    });

    // Evento para abrir/cerrar edit-box
    nuevaSeccion.querySelector('.seccion-card').addEventListener('click', function (e) {
      if (!e.target.classList.contains('eliminar-seccion')) {
        const editBox = nuevaSeccion.querySelector('.edit-box');
        editBox.classList.toggle('active');
        editBox.style.height = editBox.classList.contains('active') ? editBox.scrollHeight + "px" : "0";
      }
    });

    // 🔥 Vincular inputs a la card
    inputNombre.addEventListener('input', function () {
      nombreCard.textContent = inputNombre.value.trim() || "Nueva sección";
    });

    inputDescripcion.addEventListener('input', function () {
      descripcionCard.textContent = inputDescripcion.value.trim() || "Presione aquí para editar la sección.";
    });
    actualizarSecciones();
  });
});
