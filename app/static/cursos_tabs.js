// static/js/cursos_tabs.js

document.addEventListener('DOMContentLoaded', function () {
    // Lógica para las pestañas de Catálogo, Inscrito y Terminados
    const tabCatalogoBtn = document.getElementById('tab-catalogo');
    const tabInscritoBtn = document.getElementById('tab-inscrito');
    const tabTerminadosBtn = document.getElementById('tab-terminados');
    const tabMisCursosBtn = document.getElementById('tab-mis-cursos');
    const tabContentCatalogo = document.getElementById('tab-content-catalogo');
    const tabContentInscrito = document.getElementById('tab-content-inscrito');
    const tabContentTerminados = document.getElementById('tab-content-terminados');
    const tabContentMisCursos = document.getElementById('tab-content-mis-cursos');

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
    if (tabMisCursosBtn) {
        tabMisCursosBtn.addEventListener('click', function () {
            activateTab(tabMisCursosBtn, tabContentMisCursos);
        });
    
    }
});