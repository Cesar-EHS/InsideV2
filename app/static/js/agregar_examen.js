let contadorPreguntas = 1;
document.addEventListener('DOMContentLoaded', function () {
  // Botón para abrir el modal
  const addExamBtn = document.getElementById('add-examen-btn');
  // Modal
  const modalExamen = document.getElementById('modal-examen');
  // Tabs
  const datosTabBtn = document.getElementById('tab-datos-btn');
  const preguntasTabBtn = document.getElementById('tab-preguntas-btn');
  // Botón para cambiar a preguntas desde el formulario
  const preguntasBtn = document.getElementById('btn-preguntas-modal');

  //Tipos de opciones para las preguntas
  const preguntasContainer = document.getElementById('preguntas-container');
  const btnOpcionMultiple = document.getElementById('btn-opcion-multiple');
  const btnVerdaderoFalso = document.getElementById('btn-verdadero-falso');
  const btnAbierta = document.getElementById('btn-abierta');

  // Funcion para enumrar las preguntas si es que se borra alguna
  function renumerarPreguntas()
  {
    const numeros = preguntasContainer.querySelectorAll('.numero-pregunta');
    numeros.forEach((span, idx) => {
        span.textContent = (idx + 1) + '.';
    });
    // Actualizamos el numero de la pregunta para la siguiente
    //contadorPreguntas = preguntas.length + 1;
  }

  // DELEGACIÓN DE EVENTOS PARA AGREGAR OPCIONES
  preguntasContainer.addEventListener('click', function(e) {
    // Agregar una opción en una pregunta de opción múltiple
    if (e.target.classList.contains('btn-agregar-opcion')) {
      const pregunta = e.target.closest('.bg-gray-200');
      const opcionesContainer = pregunta.querySelector('.opciones-container');
      const nuevaOpcion = document.createElement('div');
      nuevaOpcion.className = 'flex items-center gap-2 opcion-item';
      nuevaOpcion.innerHTML = `
        <input type="checkbox" disabled>
        <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2" value="Nueva opción">
        <button type="button" class="text-red-500 btn-borrar-opcion" title="Eliminar opción">
          <span class="material-icons">delete</span>
        </button>
      `;
      opcionesContainer.appendChild(nuevaOpcion);
    }
    // Borrar una opción en una pregunta de opción múltiple
    if(e.target.classList.contains('btn-borrar-opcion') || e.target.closest('.btn-borrar-opcion')) {
      const btn = e.target.classList.contains('btn-borrar-opcion') ? e.target : e.target.closest('.btn-borrar-opcion');
      const opcion = btn.closest('.opcion-item');
      opcion.remove();
    }
    // Eliminar la pregunta completa
    if(e.target.classList.contains('btn-borrar-pregunta') || e.target.closest('.btn-borrar-pregunta')) {
      const btn = e.target.classList.contains('btn-borrar-pregunta') ? e.target : e.target.closest('.btn-borrar-pregunta');
      const pregunta = btn.closest('.bg-gray-200');
      if(pregunta) {pregunta.remove(); renumerarPreguntas();}
    }
  });

  // Abrir el modal
  if (addExamBtn && modalExamen) {
    addExamBtn.addEventListener('click', function (e) {
      e.preventDefault();
      modalExamen.classList.remove('hidden');
      window.showTabExamen('datos'); // Siempre inicia en datos
    });
  }

  // Cerrar el modal
  window.closeModalExamen = function () {
    if (modalExamen) {
      modalExamen.classList.add('hidden');
    }
  };

  // Función global para mostrar la pestaña seleccionada
  window.showTabExamen = function(tab) {
    const datosTab = document.getElementById('tab-datos-examen');
    const preguntasTab = document.getElementById('tab-preguntas-examen');

    if (tab === 'datos') {
      datosTab.classList.remove('hidden');
      preguntasTab.classList.add('hidden');
      datosTabBtn.classList.add('border-yellow-400');
      datosTabBtn.classList.remove('border-transparent');
      preguntasTabBtn.classList.remove('border-yellow-400');
      preguntasTabBtn.classList.add('border-transparent');
    } else if (tab === 'preguntas') {
      datosTab.classList.add('hidden');
      preguntasTab.classList.remove('hidden');
      datosTabBtn.classList.remove('border-yellow-400');
      datosTabBtn.classList.add('border-transparent');
      preguntasTabBtn.classList.add('border-yellow-400');
      preguntasTabBtn.classList.remove('border-transparent');
    }
  };

  // Listeners para tabs
  if (datosTabBtn) {
    datosTabBtn.addEventListener('click', function () {
      window.showTabExamen('datos');
    });
  }
  if (preguntasTabBtn) {
    preguntasTabBtn.addEventListener('click', function () {
      window.showTabExamen('preguntas');
    });
  }
  if (preguntasBtn) {
    preguntasBtn.addEventListener('click', function () {
      window.showTabExamen('preguntas');
    });
  }
  // Logica para agregar preguntas dinámicamente
  // Opción múltiple
  if (btnOpcionMultiple) {
    btnOpcionMultiple.addEventListener('click', function () {
      const preguntaHTML = `
        <div class="bg-gray-200 rounded-xl p-6 mb-6 shadow flex flex-col gap-4">
          <div class="flex justify-end gap-2">
              <button title="Eliminar" class="btn-borrar-pregunta" style="color: var(--inside-yellow);"><span class="material-icons">delete</span></button>
          </div>
          <div class="flex items-center justify-between mb-2 gap-3">
            <span class="numero-pregunta font-bold text-lg"></span>
            <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2 mb-2 font-bold" placeholder="Pregunta de opción múltiple">
          </div>
          <div class="grid grid-cols-2 gap-2 opciones-container">
            <div class="flex items-center gap-2 opcion-item">
              <input type="checkbox" disabled>
              <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2" value="Opción 1">
              <button type="button" class="text-red-500 btn-borrar-opcion" title="Eliminar opción">
                <span class="material-icons">delete</span>
              </button>
            </div>
            <div class="flex items-center gap-2 opcion-item">
              <input type="checkbox" disabled>
              <input type="text" class="text-sm w-full border border-gray-300 rounded px-3 py-2" value="Opción 2">
              <button type="button" class="text-red-500 btn-borrar-opcion" title="Eliminar opción">
                <span class="material-icons">delete</span>
              </button>
            </div>
          </div>
          <button type="button" class="text-blue-600 font-semibold mt-2 btn-agregar-opcion">+ Agregar opción</button>
          <div class="flex justify-end items-center gap-4 mt-4">
            <label class="inline-flex items-center cursor-pointer">
              <input type="checkbox" class="sr-only peer">
              <div class="w-10 h-6 bg-gray-400 rounded-full peer peer-checked:bg-[#fab522] transition"></div>
            </label>
            <span class="font-semibold text-base">Obligatoria</span>
          </div>
        </div>
      `;
      preguntasContainer.insertAdjacentHTML('beforeend', preguntaHTML);
      renumerarPreguntas();

      // Selecciona el último recuadro de pregunta agregada
      const preguntas = preguntasContainer.querySelectorAll('.bg-gray-200');
      const ultimaPregunta = preguntas[preguntas.length - 1];
      const btnAgregarOpcion = ultimaPregunta.querySelector('.btn-agregar-opcion');
      const opcionesContainer = ultimaPregunta.querySelector('.opciones-container');
    });
  }

  // Verdadero / Falso
  if (btnVerdaderoFalso) {
    btnVerdaderoFalso.addEventListener('click', function () {
      const preguntaHTML = `
        <div class="bg-gray-200 rounded-xl p-6 mb-6 shadow flex flex-col gap-4">
          <div class="flex justify-end gap-2">
            <button title="Eliminar" class="btn-borrar-pregunta" style="color: var(--inside-yellow);"><span class="material-icons">delete</span></button>
          </div>
          <div class="flex items-center justify-between mb-2 gap-3">
              <span class="numero-pregunta font-bold text-lg"></span>
              <input type="text" class="w-full border border-gray-300 rounded px-3 py-2 mb-2 font-bold" placeholder="Pregunta verdadero/falso">
          </div>
          <div class="flex flex-col gap-2">
            <div class="flex items-center gap-2">
              <input type="radio" disabled>
              <span>Verdadero</span>
            </div>
            <div class="flex items-center gap-2">
              <input type="radio" disabled>
              <span>Falso</span>
            </div>
          </div>
          <div class="flex justify-end items-center gap-4 mt-4">
            <label class="inline-flex items-center cursor-pointer">
              <input type="checkbox" class="sr-only peer">
              <div class="w-10 h-6 bg-gray-400 rounded-full peer peer-checked:bg-[#fab522] transition"></div>
            </label>
            <span class="font-semibold text-base">Obligatoria</span>
          </div>
        </div>
      `;
      preguntasContainer.insertAdjacentHTML('beforeend', preguntaHTML);
      renumerarPreguntas();
    });
  }

  // Abierta
  if (btnAbierta) {
    btnAbierta.addEventListener('click', function () {
      const preguntaHTML = `
        <div class="bg-gray-200 rounded-xl p-6 mb-6 shadow flex flex-col gap-4">
          <div class="flex justify-end gap-2">
            <button title="Eliminar" class="btn-borrar-pregunta" style="color: var(--inside-yellow);"><span class="material-icons">delete</span></button>
          </div>
          <div class="flex items-center justify-between mb-2 gap-3">
              <span class="numero-pregunta font-bold text-lg"></span>
              <input type="text" class="w-full border border-gray-300 rounded px-3 py-2 mb-2 font-bold" placeholder="Pregunta abierta">
          </div>
          <textarea class="w-full border border-gray-300 rounded px-3 py-2 bg-gray-100" placeholder="Respuesta del alumno"></textarea>
          <div class="flex justify-end items-center gap-3 mt-2">
            <label class="inline-flex items-center cursor-pointer">
              <input type="checkbox" class="sr-only peer">
              <div class="w-10 h-6 bg-gray-400 rounded-full peer peer-checked:bg-[#fab522] transition"></div>
            </label>
            <span class="font-semibold text-base">Obligatoria</span>
          </div>
        </div>
      `;
      preguntasContainer.insertAdjacentHTML('beforeend', preguntaHTML);
      renumerarPreguntas();
    });
  }
});

// Validación de fechas
document.addEventListener('DOMContentLoaded', function () {
  const fechaInicio = document.getElementById('fechaInicio');
  const fechaCierre = document.getElementById('fechaCierre');

  if (fechaInicio && fechaCierre) {
    fechaInicio.addEventListener('change', function () {
      fechaCierre.min = fechaInicio.value;
      if (fechaCierre.value < fechaInicio.value) {
        fechaCierre.value = fechaInicio.value;
      }
    });
  }
});