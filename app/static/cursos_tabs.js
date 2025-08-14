// static/js/cursos_tabs.js

document.addEventListener('DOMContentLoaded', function () {
    // Lógica para las pestañas de Catálogo, Inscrito y Terminados
    const tabCatalogoBtn = document.getElementById('tab-catalogo');
    const tabInscritoBtn = document.getElementById('tab-inscrito');
    const tabTerminadosBtn = document.getElementById('tab-terminados');
    const tabContentCatalogo = document.getElementById('tab-content-catalogo');
    const tabContentInscrito = document.getElementById('tab-content-inscrito');
    const tabContentTerminados = document.getElementById('tab-content-terminados');
    const btnEliminarCurso = document.getElementById('btn-eliminar-curso');

    function activateTab(activeBtn, activeContent) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.classList.remove('text-[#3b3b3c]');
            btn.classList.add('text-[#3b3b3c]/80');
        });
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        if (activeBtn) {
            activeBtn.classList.add('active');
            activeBtn.classList.remove('text-[#3b3b3c]/80');
            activeBtn.classList.add('text-[#3b3b3c]');
        }
        if (activeContent) {
            activeContent.classList.add('active');
        }
    }

    // Activar pestaña de Incristo si tiene el parámetro de "inscrito" en la URL
    const parametros = new URLSearchParams(window.location.search);
    const tabParametro = parametros.get('tab');
    if (tabParametro === 'inscrito' && tabInscritoBtn && tabContentInscrito) {
        activateTab(tabInscritoBtn, tabContentInscrito);
    }

    // Determinar tab inicial para catálogo o inscrito según el rol
    const esEncargado = window.esEncargado;
    if (esEncargado && tabCatalogoBtn && tabContentCatalogo) {
        activateTab(tabCatalogoBtn, tabContentCatalogo);
    } else if (tabInscritoBtn && tabContentInscrito) {
        activateTab(tabInscritoBtn, tabContentInscrito);
    }

    // Eventos de click para las nuevas pestañas
    if (tabCatalogoBtn) {
        tabCatalogoBtn.addEventListener('click', function () {
            activateTab(tabCatalogoBtn, tabContentCatalogo);
        });
    }
    if (tabInscritoBtn) {
        tabInscritoBtn.addEventListener('click', function () {
            activateTab(tabInscritoBtn, tabContentInscrito);
        });
    }
    if (tabTerminadosBtn) {
        tabTerminadosBtn.addEventListener('click', function () {
            activateTab(tabTerminadosBtn, tabContentTerminados);
        });
    }

    document.body.addEventListener('click', function (e) {
        if (e.target.closest('.btn-eliminar-curso')) {
            const btn = e.target.closest('.btn-eliminar-curso');
            const cursoId = btn.getAttribute('data-id');
            if (cursoId) {
                confirmDeleteCourse(cursoId);
            }
        }
    });

    // Lógica para botones de eliminar (SweetAlert2)
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
                fetch('/cursos/eliminar/${cursoId}', {
                    method: 'DELETE',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json',
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
                            const contentType = response.headers.get('content-type');
                            if (contentType && contentType.includes('application/json')) {
                                response.json().then(data => {
                                    Swal.fire(
                                        'Error',
                                        data.message || 'No se pudo eliminar el curso.',
                                        'error'
                                    );
                                });
                            } else {
                                Swal.fire(
                                    'Error',
                                    'No se pudo eliminar el curso (respuesta inesperada del servidor).',
                                    'error'
                                );
                            }
                        }
                    })
            }
        });
    }
    window.confirmDeleteCourse = confirmDeleteCourse;
});