function recolectarPreguntas() {
  const preguntas = [];
  const preguntaBlocks = document.querySelectorAll('.bg-gray-200');
  preguntaBlocks.forEach(block => {
    // Detecta el tipo de pregunta
    let tipo = '';
    if (block.querySelector('.opciones-container')) {
      tipo = 'opcion_multiple';
    } else if (block.querySelector('input[type="radio"]')) {
      tipo = 'verdadero_falso';
    } else if (block.querySelector('textarea')) {
      tipo = 'abierta';
    }

    // Texto de la pregunta
    const texto = block.querySelector('input[type="text"]').value;

    // Obligatoria
    const obligatoria = block.querySelector('input[type="checkbox"].peer')?.checked || false;

    // Opciones (solo para opción múltiple)
    let opciones = [];
    if (tipo === 'opcion_multiple') {
      const opcionItems = block.querySelectorAll('.opciones-container .opcion-item');
      opcionItems.forEach(item => {
        opciones.push({
          texto: item.querySelector('input[type="text"]').value,
          es_correcta: false // Puedes agregar lógica para marcar la correcta si lo necesitas
        });
      });
    }

    preguntas.push({
      texto,
      tipo,
      obligatoria,
      opciones
    });
  });
  return preguntas;
}

function enviarExamen() {
  // Recolecta datos del examen (ajusta los IDs según tu HTML)
  const titulo = document.getElementById('tituloExamen')?.value || '';
  const descripcion = document.getElementById('descripcionExamen')?.value || '';
  const fecha_inicio = document.getElementById('fechaInicio')?.value || '';
  const fecha_cierre = document.getElementById('fechaCierre')?.value || '';

  const preguntas = recolectarPreguntas();

  const examenData = {
    titulo,
    descripcion,
    fecha_inicio,
    fecha_cierre,
    preguntas
  };

  fetch('/curso/123/examen/agregar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(examenData)
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert('Examen guardado correctamente');
      // Redirige o limpia el formulario si quieres
    } else {
      alert('Error al guardar el examen');
    }
  });
}

// Ejemplo: llama a enviarExamen() cuando el usuario presione "Guardar examen"
// document.getElementById('btn-guardar-examen').addEventListener('click', enviarExamen);