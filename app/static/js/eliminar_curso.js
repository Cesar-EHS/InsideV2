document.addEventListener('DOMContentLoaded', function() {
    // Usamos delegación de eventos en el contenedor principal de los cursos.
    // Esto asegura que el botón de eliminar siempre funcione,
    // incluso si las tarjetas se cargan dinámicamente.
    const cursosContainer = document.getElementById('tab-content-catalogo');
    
    if (cursosContainer) {
        cursosContainer.addEventListener('click', async function(e) {
            // Buscamos el botón de eliminar más cercano al elemento que se clicó.
            const deleteBtn = e.target.closest('.btn-eliminar-curso');
            
            // Si no se clicó en el botón de eliminar, no hacemos nada.
            if (!deleteBtn) {
                return;
            }
            
            const cursoId = deleteBtn.dataset.id;
            console.log("ID del curso a eliminar:", cursoId);
            if (!cursoId) {
                return;
            }
            
            // Usamos SweetAlert2 para una confirmación más profesional.
            const result = await Swal.fire({
                title: '¿Estás seguro?',
                text: "¡No podrás revertir esto! El curso se marcará como inactivo.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            });

            if (!result.isConfirmed) {
                return;
            }

            try {
                // Primero, obtenemos el token del campo oculto en el DOM.
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;

                const resp = await fetch(`/cursos/eliminar/${cursoId}`, {
                    method: 'DELETE',
                    headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrfToken }
                });

                // Imprime el encabezado de la respuesta
                console.log('Estatus de la respuesta:', resp.status);
                console.log('Encabezado Content-Type:', resp.headers.get('Content-Type'));

                // Verifica si la respuesta es de tipo JSON antes de intentar parsearla
                const contentType = resp.headers.get('Content-Type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await resp.json();
                    console.log('Datos recibidos (JSON):', data);

                    if (data.success) {
                    // ... Lógica de éxito con SweetAlert2 ...
                        await Swal.fire('Eliminado', 'El curso ha sido eliminado.', 'success');
                    } else {
                    // ... Lógica de error con SweetAlert2 ...
                        await Swal.fire('Error', data.message || 'Error al eliminar el curso.', 'error');
                    }
                } else {
                    // Si no es JSON, lee la respuesta como texto
                    const data = await resp.text();
                    console.error('El servidor no devolvió JSON. Contenido de la respuesta:', data);

                    Swal.fire('Error', 'El servidor devolvió una respuesta inesperada.', 'error');
                }

            } catch (err) {
                console.error('Error en la petición DELETE:', err);
                Swal.fire('Error', 'Error de conexión con el servidor.', 'error');
                }
        });
    }
});