// static/js/cursos_tabs.js

document.addEventListener('DOMContentLoaded', function() {
    const tabGestionBtn = document.getElementById('tab-gestion-cursos');
    const tabMisBtn = document.getElementById('tab-mis-cursos');
    const tabContentGestion = document.getElementById('tab-content-gestion-cursos');
    const tabContentMis = document.getElementById('tab-content-mis-cursos');

    function activateTab(activeBtn, activeContent) { // Simplificamos los parámetros
        // Eliminar 'active' de todos los botones y contenidos
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            // Restablecer colores de texto e icono a inactivo por defecto
            btn.classList.remove('text-[#3b3b3c]');
            btn.classList.add('text-[#3b3b3c]/80');
            const icon = btn.querySelector('i');
            if (icon) {
                icon.classList.remove('text-[#232323]');
                icon.classList.add('text-[#3b3b3c]/80');
            }
        });
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // Activar el botón y contenido seleccionados
        // Solo activar si el botón existe (tabGestionBtn podría ser null si no es encargado)
        if (activeBtn) {
            activeBtn.classList.add('active');
            activeBtn.classList.remove('text-[#3b3b3c]/80');
            activeBtn.classList.add('text-[#3b3b3c]');
            const activeIcon = activeBtn.querySelector('i');
            if (activeIcon) {
                activeIcon.classList.remove('text-[#3b3b3c]/80');
                activeIcon.classList.add('text-[#232323]');
            }
        }
        activeContent.classList.add('active');
    }

    // Determinar qué pestaña activar inicialmente al cargar la página
    // Ahora leemos el valor de la variable global que definimos en el HTML
    const esEncargado = window.esEncargado; 

    if (esEncargado) {
        // Si es encargado, activar la pestaña de Gestión de cursos por defecto
        activateTab(tabGestionBtn, tabContentGestion);
    } else {
        // Si NO es encargado, activar la pestaña de Mis cursos por defecto (y será la única visible)
        activateTab(tabMisBtn, tabContentMis);
    }

    // Asignar eventos de clic (solo si el botón existe)
    if (tabGestionBtn) {
        tabGestionBtn.addEventListener('click', function() {
            activateTab(tabGestionBtn, tabContentGestion);
        });
    }
    // Este botón siempre existirá
    tabMisBtn.addEventListener('click', function() {
        activateTab(tabMisBtn, tabContentMis);
    });

    // Lógica para botones de eliminar (Ejemplo con SweetAlert2)
    function confirmDeleteCourse(cursoId) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "¡No podrás revertir esto!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, ¡eliminar!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/cursos/eliminar/${cursoId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => {
                    if (response.ok) {
                        Swal.fire(
                            '¡Eliminado!',
                            'El curso ha sido eliminado.',
                            'success'
                        ).then(() => {
                            location.reload();
                        });
                    } else {
                        return response.json().then(data => {
                            Swal.fire(
                                'Error',
                                data.message || 'No se pudo eliminar el curso.',
                                'error'
                            );
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire(
                        'Error de red',
                        'Hubo un problema al conectar con el servidor.',
                        'error'
                    );
                });
            }
        });
    }
    window.confirmDeleteCourse = confirmDeleteCourse;

    /* // Lógica para el botón "Ver Ticket"
    document.querySelectorAll('.btn-ver-ticket').forEach(button => {
        button.addEventListener('click', function() {
            const ticketId = this.dataset.id;
            window.location.href = `/tickets/${ticketId}`;
        });
    }); */
});