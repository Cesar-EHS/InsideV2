// Función de alertas para notificaciones
function showAlert(message, type = 'info') {
    // Crear elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all transform translate-x-full opacity-0`;
    
    const colors = {
        success: 'bg-green-100 text-green-800 border border-green-200',
        error: 'bg-red-100 text-red-800 border border-red-200',
        warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
        info: 'bg-blue-100 text-blue-800 border border-blue-200'
    };
    
    alertDiv.className += ` ${colors[type] || colors.info}`;
    alertDiv.innerHTML = `
        <div class="flex items-center">
            <span class="mr-2">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-gray-500 hover:text-gray-700">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Animación de entrada
    setTimeout(() => {
        alertDiv.classList.remove('translate-x-full', 'opacity-0');
        alertDiv.classList.add('translate-x-0', 'opacity-100');
    }, 100);
    
    // Auto-cierre después de 5 segundos
    setTimeout(() => {
        alertDiv.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// Función para subir imagen de login
function subirImagenLogin() {
    console.log('🚀 subirImagenLogin iniciada');
    const file = document.getElementById('loginImageInput').files[0];
    if (!file) {
        alert('Por favor selecciona un archivo');
        return;
    }
    
    // Validación de tamaño
    if (file.size > 2 * 1024 * 1024) {
        alert('Archivo muy grande. Máximo 2MB');
        return;
    }
    
    // Validación de tipo
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        alert('Tipo de archivo no permitido. Use PNG, JPG, JPEG o GIF.');
        return;
    }
    
    const formData = new FormData();
    formData.append('login_image', file);
    
    alert('Subiendo imagen de login...');
    
    fetch('/auth/actualizar_configuracion', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Imagen de login actualizada exitosamente');
            // Actualizar imagen mostrada
            const img = document.getElementById('currentLoginImage');
            if (img && data.new_image) {
                img.src = `/${data.new_image}?t=${Date.now()}`;
            }
            // Recargar página después de 2 segundos
            setTimeout(() => location.reload(), 2000);
        } else {
            alert('❌ Error: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Error de conexión');
    });
}

// Función para subir logo
function subirLogo() {
    console.log('🚀 subirLogo iniciada');
    const file = document.getElementById('logoImageInput').files[0];
    if (!file) {
        alert('Por favor selecciona un archivo');
        return;
    }
    
    // Validación de tamaño
    if (file.size > 2 * 1024 * 1024) {
        alert('Archivo muy grande. Máximo 2MB');
        return;
    }
    
    // Validación de tipo
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml'];
    if (!allowedTypes.includes(file.type)) {
        alert('Tipo de archivo no permitido. Use PNG, JPG, JPEG, GIF o SVG.');
        return;
    }
    
    const formData = new FormData();
    formData.append('logo_image', file);
    
    alert('Subiendo logo...');
    
    fetch('/auth/actualizar_configuracion', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Logo actualizado exitosamente');
            // Actualizar logo mostrado
            const img = document.getElementById('currentLogo');
            if (img && data.new_logo) {
                img.src = `/static/${data.new_logo}?t=${Date.now()}`;
            }
            // Recargar página después de 2 segundos
            setTimeout(() => location.reload(), 2000);
        } else {
            alert('❌ Error: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Error de conexión');
    });
}

// Función para subir imagen de fondo
function subirImagenFondo() {
    console.log('🚀 subirImagenFondo iniciada');
    const file = document.getElementById('backgroundImageInput').files[0];
    if (!file) {
        alert('Por favor selecciona un archivo');
        return;
    }
    
    // Validación de tamaño
    if (file.size > 2 * 1024 * 1024) {
        alert('Archivo muy grande. Máximo 2MB');
        return;
    }
    
    // Validación de tipo
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
        alert('Tipo de archivo no permitido. Use PNG, JPG o JPEG.');
        return;
    }
    
    const formData = new FormData();
    formData.append('background_image', file);
    
    alert('Subiendo imagen de fondo...');
    
    fetch('/auth/actualizar_configuracion', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Imagen de fondo actualizada exitosamente');
            // Recargar página después de 2 segundos para aplicar cambios
            setTimeout(() => location.reload(), 2000);
        } else {
            alert('❌ Error: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Error de conexión');
    });
}

// Mensaje de confirmación de carga del script
console.log('✅ Upload functions script loaded successfully');
console.log('✅ Funciones disponibles: subirImagenLogin, subirLogo, subirImagenFondo');
