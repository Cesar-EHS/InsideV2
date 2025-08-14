// static/js/modal_add_curso.js

document.addEventListener('DOMContentLoaded', function() {
  console.log('modal_add_curso.js: Script de Cursos cargado y DOM listo.');

  // === 1. Obtener Referencias de Elementos ===
  const btnNuevoCurso = document.getElementById('btnNuevoCurso'); // Botón "+ Nuevo"
  const cursoModal = document.getElementById('cursoModal');       // Contenedor principal del modal
  const closeModalBtn = document.getElementById('closeModal');   // Botón "X" para cerrar
  const formNuevoCurso = document.getElementById('formNuevoCurso'); // El formulario dentro del modal

  // === 2. Funciones de Ayuda ===

  // Función para mostrar mensajes "toast" (copiada/adaptada de helpdesk.js si no la tienes globalmente)
  // Asegúrate de que esta función no exista ya globalmente para evitar duplicados.
  if (typeof window.mostrarToast === 'undefined') {
    window.mostrarToast = function (msg, tipo = 'success') {
      let toast = document.getElementById('toast-feedback');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-feedback';
        toast.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-2 rounded-xl shadow-lg z-50 font-sfpro text-base opacity-0 transition-opacity duration-300';
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      toast.classList.remove('opacity-0', 'bg-red-600', 'bg-green-600', 'bg-gray-900');
      toast.classList.add('opacity-100');
      if (tipo === 'success') toast.classList.add('bg-green-600');
      else if (tipo === 'error') toast.classList.add('bg-red-600');
      else toast.classList.add('bg-gray-900'); // Default o info

      setTimeout(() => {
          toast.classList.remove('opacity-100');
          toast.classList.add('opacity-0');
          setTimeout(() => { 
            // Eliminar el toast del DOM después de la transición de desvanecimiento
            if (toast.parentNode) toast.parentNode.removeChild(toast); 
          }, 300); 
      }, 2200); // Tiempo visible antes de empezar a desvanecerse
    };
  }

  // Función para cerrar el modal
const cerrarCursoModal = function() {
  console.log('modal_add_curso.js: Cerrando modal de curso.');
  if (cursoModal) {
    cursoModal.classList.add('hidden'); // <-- ¡Asegúrate de que esta línea esté aquí!
    cursoModal.classList.remove('flex');
    cursoModal.classList.remove('bg-black/40'); // Las que agregaste para el fondo
    cursoModal.classList.remove('backdrop-blur-md'); // Y el blur
    document.body.style.overflow = ''; // Restaurar el scroll del body
    // Opcional: limpiar el formulario al cerrar si no recargas la página
    if (formNuevoCurso) formNuevoCurso.reset();
  }
};

  // === 3. Event Listeners para Abrir/Cerrar Modal ===

  // Event Listener para el botón "+ Nuevo"
  if (btnNuevoCurso && cursoModal) {
    btnNuevoCurso.addEventListener('click', function(e) {
      e.preventDefault(); // ¡CRÍTICO! Esto evita que el navegador siga el href="#" y recargue la página.
      console.log('modal_add_curso.js: Botón "+ Nuevo" clickeado. Abriendo modal.');
      cursoModal.classList.remove('hidden');
      cursoModal.classList.add('flex'); // Cambia a 'flex' para mostrarlo (según tu CSS de modal)
      cursoModal.classList.add('bg-black/40'); // O bg-gray-600/50 si te gusta más ese color
      setTimeout(() => cursoModal.classList.add('backdrop-blur-md'), 10);
      document.body.style.overflow = 'hidden'; // Evita el scroll del body principal
      // Opcional: enfocar el primer campo del formulario para mejorar UX
      const primerInput = formNuevoCurso ? formNuevoCurso.querySelector('input, textarea, select') : null;
      if (primerInput) primerInput.focus();
    });
  } else {
    console.error("modal_add_curso.js: Elementos HTML 'btnNuevoCurso' o 'cursoModal' no encontrados.");
  }

  // Event Listener para el botón "X" de cerrar
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', cerrarCursoModal);
  } else {
    console.warn("modal_add_curso.js: Botón 'closeModal' no encontrado.");
  }
  
  // Event Listener para el botón "Cancelar" dentro del formulario (el que tiene id="btnCancelarFormCurso")
  const btnCancelarFormCurso = document.getElementById('btnCancelarFormCurso');
  if (btnCancelarFormCurso) {
      btnCancelarFormCurso.addEventListener('click', cerrarCursoModal);
  }


  // Event Listener para cerrar el modal al hacer clic fuera del contenido
  if (cursoModal) {
    cursoModal.addEventListener('click', function(e) {
      // Si el clic es directamente en el overlay (fondo oscuro) y no en el contenido del modal
      if (e.target === cursoModal) { 
        cerrarCursoModal();
      }
    });
  }

  // Event Listener para cerrar el modal con la tecla 'Escape'
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && cursoModal && !cursoModal.classList.contains('hidden')) {
      cerrarCursoModal();
    }
  });

  // === 4. Event Listener para el Envío del Formulario (AJAX) ===

  if (formNuevoCurso) {
    formNuevoCurso.addEventListener('submit', async function(e) {
      e.preventDefault(); // Detiene el envío normal del formulario

      console.log('modal_add_curso.js: Formulario de curso enviado vía AJAX.');
      const formData = new FormData(formNuevoCurso);
      
      // Obtener el token CSRF (Flask-WTF lo pone en un input hidden)
      const csrfTokenElement = formNuevoCurso.querySelector('input[name="csrf_token"]');
      const csrfToken = csrfTokenElement ? csrfTokenElement.value : null;

      const submitBtn = formNuevoCurso.querySelector('button[type=submit], input[type=submit]');
      if (submitBtn) {
        submitBtn.disabled = true; // Deshabilita el botón para evitar doble envío
        submitBtn.innerText = 'Enviando...'; // Cambia el texto del botón
      }

      try {
        const resp = await fetch(formNuevoCurso.action, { // La URL de acción del formulario (ej. /cursos/agregar)
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest', // Indica a Flask que esta es una petición AJAX
            ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}) // Incluye el token CSRF en el header
          }
        });

        // Manejo de redirecciones (ej. si la sesión expira o hay un redirect en Flask)
        if (resp.redirected) {
          console.log('modal_add_curso.js: Redirección de Flask detectada. Recargando página.');
          window.location.href = resp.url; // Redirige a la URL que Flask indica
          return;
        }

        let data;
        // Intenta parsear la respuesta como JSON solo si el tipo de contenido es JSON
        const contentType = resp.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            data = await resp.json();
        } else {
            // Si no es JSON, asume que es una respuesta exitosa sin JSON o un error no-JSON.
            // Esto es un fallback si Flask no siempre devuelve JSON en errores, pero lo ideal es que sí.
            data = { success: resp.ok, message: await resp.text() }; // Lee como texto si no es JSON
            if (!resp.ok) { // Si hubo un error HTTP, considéralo un error.
                console.error('modal_add_curso.js: Respuesta no JSON para un error:', data.message);
                throw new Error(data.message); // Lanza un error para ser capturado por el catch
            }
        }

        if (resp.ok && data.success) {
          console.log('modal_add_curso.js: Curso agregado exitosamente. Mensaje:', data.message);
          window.mostrarToast(data.message || 'Curso agregado correctamente.', 'success');
          cerrarCursoModal(); // Cierra el modal
          setTimeout(() => window.location.reload(), 800); // Recarga la página para ver el nuevo curso
        } else {
          console.error('modal_add_curso.js: Error al agregar curso. Detalles:', data);
          let errorMsg = data.message || data.error || 'Error desconocido al agregar curso.';
          if (data.errors) { // Si Flask-WTF devuelve errores de validación en el JSON
              // Convierte los errores de campo en un string legible
              const fieldErrors = Object.entries(data.errors)
                  .map(([field, messages]) => {
                      // Capitaliza el nombre del campo para una mejor presentación
                      const formattedField = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                      return `${formattedField}: ${messages.join(', ')}`;
                  })
                  .join('<br>');
              errorMsg = `Errores de validación:<br>${fieldErrors}`;
          }
          window.mostrarToast(errorMsg, 'error');
        }

      } catch (error) {
        console.error('modal_add_curso.js: Error de red o en la petición fetch:', error);
        window.mostrarToast('Error de conexión con el servidor. Por favor, inténtalo de nuevo.', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false; // Habilita el botón
          submitBtn.innerText = 'Crear Curso'; // Restaura el texto original
        }
      }
    });
  } else {
    console.error("modal_add_curso.js: Formulario con ID 'formNuevoCurso' no encontrado en el DOM.");
  }

  // Previsualización de archivos en los recuadros de recursos
  ['archivo1', 'archivo2', 'archivo3'].forEach(function(id) {
    const input = document.getElementById(id);
    const preview = document.getElementById('preview-' + id);
    const label = document.getElementById('label-' + id);
    const iconoRecurso = label ? label.querySelector('.icono-recurso') : null;

    if (input && preview && label && iconoRecurso) {
      input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
          // Oculta el "+ Recurso"
          iconoRecurso.style.display = 'none';

          let iconHtml = '';
          if (file.type.startsWith('image/')) {
            // Miniatura de imagen
            const reader = new FileReader();
            reader.onload = function(ev) {
              preview.innerHTML = `
                <div class="flex flex-col items-center justify-center w-full">
                  <img src="${ev.target.result}" class="h-16 w-16 object-cover rounded mb-2" alt="preview">
                  <span class="font-semibold text-center">${file.name}</span>
                  <button type="button" class="mt-2 text-red-500 font-bold text-lg remove-recurso" title="Eliminar">&times;</button>
                </div>
              `;
              preview.querySelector('.remove-recurso').onclick = function() {
                input.value = '';
                preview.innerHTML = '';
                iconoRecurso.style.display = '';
              };
            };
            reader.readAsDataURL(file);
          } else {
            // Ícono según tipo
            if (file.type === 'application/pdf') {
              iconHtml = '<i class="fas fa-file-pdf text-5xl text-red-500 mb-2"></i>';
            } else if (
              file.type === 'application/msword' ||
              file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ) {
              iconHtml = '<i class="fas fa-file-word text-5xl text-blue-500 mb-2"></i>';
            } else {
              iconHtml = '<i class="fas fa-file-alt text-5xl text-gray-500 mb-2"></i>';
            }
            preview.innerHTML = `
              <div class="flex flex-col items-center justify-center w-full">
                ${iconHtml}
                <span class="font-semibold text-center">${file.name}</span>
                <button type="button" class="mt-2 text-red-500 font-bold text-lg remove-recurso" title="Eliminar">&times;</button>
              </div>
            `;
            preview.querySelector('.remove-recurso').onclick = function() {
              input.value = '';
              preview.innerHTML = '';
              iconoRecurso.style.display = '';
            };
          }
        } else {
          preview.innerHTML = '';
          iconoRecurso.style.display = '';
        }
      });
    }
  });

  const imagenInput = document.getElementById('imagen');
  const previewImg = document.getElementById('preview-img');
  const labelImagen = document.getElementById('label-imagen');
  const iconoImagen = document.getElementById('icono-imagen');

  if (imagenInput && previewImg && labelImagen && iconoImagen) {
    imagenInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file && file.type.startsWith('image/')) {
        iconoImagen.style.display = 'none';
        const reader = new FileReader();
        reader.onload = function(ev) {
          previewImg.innerHTML = `
            <img src="${ev.target.result}" class="object-cover w-full h-full rounded-xl" alt="Previsualización">
            <button type="button" class="absolute top-2 right-2 text-red-500 font-bold text-lg remove-imagen bg-white/80 rounded-full px-2" title="Eliminar">&times;</button>
          `;
          const removeBtn = previewImg.querySelector('.remove-imagen');
          removeBtn.onclick = function() {
            imagenInput.value = '';
            previewImg.innerHTML = '';
            iconoImagen.style.display = '';
          };
        };
        reader.readAsDataURL(file);
      } else {
        previewImg.innerHTML = '';
        iconoImagen.style.display = '';
      }
    });
  }
});