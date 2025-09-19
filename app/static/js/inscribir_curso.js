document.addEventListener('DOMContentLoaded', function() {
    const inscripcionForm = document.getElementById('inscripcionForm');

    if (inscripcionForm) {
        inscripcionForm.addEventListener('submit', function(event) {
            // 1. Prevenimos el envío tradicional del formulario
            event.preventDefault();

            const form = event.target;
            const url = form.action;
            const formData = new FormData(form);

            // 2. Enviamos la solicitud de inscripción en segundo plano
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // --- INICIO DE LA LÓGICA CORREGIDA ---

                // Caso 1: Inscripción nueva y exitosa
                if (data.status === 'success') {
                    Swal.fire({
                        title: '¡Éxito!',
                        text: data.message, // Usamos el mensaje del servidor
                        icon: 'success',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = data.redirect_url;
                    });
                } 
                
                // Caso 2: El usuario ya estaba inscrito
                else if (data.status === 'info') {
                    Swal.fire({
                        title: 'Información', // Título correcto
                        text: data.message, // Usamos el mensaje del servidor
                        icon: 'info', // Ícono correcto
                        confirmButtonText: 'Ir al curso'
                    }).then((result) => {
                        // Si el usuario hace clic en el botón, redirigimos
                        if (result.isConfirmed) {
                            window.location.href = data.redirect_url;
                        }
                    });
                } 
                
                // Caso 3: Ocurrió un error en el servidor
                else {
                    Swal.fire({
                        title: 'Error',
                        text: data.message || 'Hubo un problema al procesar tu solicitud.',
                        icon: 'error'
                    });
                }
                
                // --- FIN DE LA LÓGICA CORREGIDA ---
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    title: 'Error de Conexión',
                    text: 'No se pudo conectar con el servidor. Inténtalo de nuevo.',
                    icon: 'error'
                });
            });
        });
    }
});