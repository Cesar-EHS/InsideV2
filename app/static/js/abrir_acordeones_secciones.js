document.addEventListener('DOMContentLoaded', function () {
    const accordions = document.querySelectorAll('.seccion-acordeon');

    accordions.forEach(accordion => {
        const button = accordion.querySelector('button');
        const content = accordion.querySelector('.contenido-seccion');
        const icon = button.querySelector('.material-icons');

        button.addEventListener('click', () => {
            const isOpening = !content.style.maxHeight;
            // Cierra todos los demás
            accordions.forEach(otherAccordion => {
                if (otherAccordion !== accordion) {
                    otherAccordion.querySelector('.contenido-seccion').style.maxHeight = null;
                    otherAccordion.querySelector('button .material-icons')?.classList.remove('rotate-180');
                }
            });
            // Abre o cierra el actual
            if (isOpening) {
                content.style.maxHeight = content.scrollHeight + "px";
                icon?.classList.add('rotate-180');
            } else {
                content.style.maxHeight = null;
                icon?.classList.remove('rotate-180');
            }
        });
    });
});