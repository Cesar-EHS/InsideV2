document.addEventListener('DOMContentLoaded', function () {
    // 1. Seleccionamos los elementos con los que vamos a trabajar.
    const toggleFiltro = document.getElementById('toggle-inactivos');
    const contenedorCursos = document.getElementById('grid-mis-cursos');

    // Si por alguna razón la página no tiene estos elementos, no hacemos nada.
    if (!toggleFiltro || !contenedorCursos) {
        console.warn('No se encontraron los elementos para el filtro de "Mis Cursos".');
        return;
    }

    // 2. Definimos la función que se encargará de mostrar u ocultar los cursos.
    const aplicarFiltro = () => {
        // Obtenemos el estado actual del toggle (true si está activado, false si no).
        const mostrarInactivos = toggleFiltro.checked;
        
        // Obtenemos todas las 'cards' de los cursos que están dentro del contenedor.
        const cursos = contenedorCursos.querySelectorAll('.card-curso-creado');

        let cursosVisibles = 0;

        cursos.forEach(curso => {
            // Leemos el estado del curso que guardamos en el atributo `data-estado`.
            const estado = curso.dataset.estado;

            if (mostrarInactivos) {
                // Si el toggle está activado, simplemente mostramos todos los cursos.
                curso.style.display = 'block';
                cursosVisibles++;
            } else {
                // Si el toggle está desactivado...
                if (estado === 'inactivo') {
                    // ...ocultamos los que están inactivos.
                    curso.style.display = 'none';
                } else {
                    // ...y mostramos los demás.
                    curso.style.display = 'block';
                    cursosVisibles++;
                }
            }
        });
    };

    // 3. Hacemos que la función se ejecute en dos momentos clave:

    // a) Inmediatamente cuando la página carga, para que el estado inicial sea el correcto.
    aplicarFiltro();

    // b) Cada vez que el usuario haga clic en el toggle para cambiar su estado.
    toggleFiltro.addEventListener('change', aplicarFiltro);
});