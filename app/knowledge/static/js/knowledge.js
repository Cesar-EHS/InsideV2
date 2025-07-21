// Knowledge Module JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades
    initializeModal();
    initializeCategoryCards();
    initializeFilters();
    initializeSmoothTransitions();
});

// Inicializar transiciones suaves
function initializeSmoothTransitions() {
    // Interceptar navegación entre categorías
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (this.getAttribute('onclick')) {
                e.preventDefault();
                const categoryName = this.getAttribute('onclick').match(/'([^']+)'/)[1];
                navigateToCategory(categoryName);
            }
        });
    });

    // Interceptar envío de formularios
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this);
        });
    }

    // Interceptar filtros
    const filterElements = document.querySelectorAll('select, input[type="search"]');
    filterElements.forEach(element => {
        element.addEventListener('change', handleFilterChange);
        if (element.type === 'search') {
            element.addEventListener('input', debounce(handleFilterChange, 300));
        }
    });
}

// Navegación suave a categorías
function navigateToCategory(categoryName) {
    showLoadingOverlay();
    
    const url = `/knowledge/categoria/${encodeURIComponent(categoryName)}`;
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            // Fade out actual
            document.body.style.opacity = '0.7';
            document.body.style.transition = 'opacity 0.3s ease';
            
            setTimeout(() => {
                window.location.href = url;
            }, 300);
        })
        .catch(error => {
            console.error('Error:', error);
            hideLoadingOverlay();
            window.location.href = url; // Fallback
        });
}

// Manejo suave de envío de formularios
function handleFormSubmission(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Mostrar estado de carga
    showFormLoading(submitBtn);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (response.ok) {
            // Mostrar éxito y recargar suavemente
            showSuccessMessage('Archivo subido correctamente');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error('Error en la subida');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Error al subir el archivo');
        hideFormLoading(submitBtn);
    });
}

// Manejo suave de filtros
function handleFilterChange(e) {
    const container = document.getElementById('documents-container');
    if (!container) return;

    showLoadingOverlay();
    
    // Crear URL con parámetros de filtro actuales
    const form = e.target.closest('form') || document.querySelector('form');
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    const currentUrl = new URL(window.location);
    params.forEach((value, key) => {
        if (value) currentUrl.searchParams.set(key, value);
        else currentUrl.searchParams.delete(key);
    });
    
    fetch(currentUrl.toString())
        .then(response => response.text())
        .then(html => {
            // Extraer solo el contenido de documentos
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newContainer = doc.getElementById('documents-container');
            
            if (newContainer) {
                // Transición suave
                container.style.opacity = '0.5';
                container.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {
                    container.innerHTML = newContainer.innerHTML;
                    container.style.opacity = '1';
                    hideLoadingOverlay();
                    
                    // Actualizar URL sin recargar
                    window.history.pushState({}, '', currentUrl.toString());
                }, 300);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            hideLoadingOverlay();
        });
}

// Overlay de carga
function showLoadingOverlay() {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50';
        overlay.innerHTML = `
            <div class="bg-white rounded-lg p-6 shadow-lg flex items-center gap-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span class="text-gray-700">Cargando...</span>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Estados de formulario
function showFormLoading(button) {
    if (!button) return;
    
    button.disabled = true;
    button.innerHTML = `
        <div class="flex items-center gap-2">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Subiendo...</span>
        </div>
    `;
}

function hideFormLoading(button) {
    if (!button) return;
    
    button.disabled = false;
    button.innerHTML = 'Subir Documento';
}

// Mensajes de estado
function showSuccessMessage(message) {
    showToast(message, 'success');
}

function showErrorMessage(message) {
    showToast(message, 'error');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium transform translate-x-full transition-transform duration-300 ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Animar salida
    setTimeout(() => {
        toast.style.transform = 'translateX(full)';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Utility: Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Funciones para el modal
function initializeModal() {
    const modal = document.getElementById('modal');
    const openBtn = document.getElementById('btn-open-modal');
    const closeBtn = document.getElementById('modal-close');
    const cancelBtn = document.getElementById('modal-cancel');
    const form = document.getElementById('upload-form');

    if (!modal || !openBtn) return;

    function openModal() {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
        if (form) form.reset();
    }

    openBtn.addEventListener('click', openModal);
    closeBtn?.addEventListener('click', closeModal);
    cancelBtn?.addEventListener('click', closeModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

// Funciones para las tarjetas de categoría
function initializeCategoryCards() {
    const categoryCards = document.querySelectorAll('.category-card');
    
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Funciones para filtros y búsqueda
function initializeFilters() {
    const searchInput = document.querySelector('input[name="search"]');
    let searchTimeout;

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.form.submit();
            }, 500);
        });
    }
}

// Función global para abrir categoría con filtros
function openCategory(categoria) {
    const orderSelect = document.getElementById('order-select');
    const tipoFilter = document.getElementById('tipo-filter');
    const searchInput = document.getElementById('search-input');
    
    if (!orderSelect || !tipoFilter || !searchInput) {
        console.error('No se encontraron los elementos de filtro');
        return;
    }
    
    const orderBy = orderSelect.value;
    const tipoFilter_value = tipoFilter.value;
    const searchQuery = searchInput.value;
    
    // Construir URL base
    let baseUrl = '/knowledge/categoria/' + encodeURIComponent(categoria);
    
    const params = new URLSearchParams();
    if (orderBy !== 'fecha') params.append('order', orderBy);
    if (tipoFilter_value) params.append('tipo', tipoFilter_value);
    if (searchQuery) params.append('search', searchQuery);
    
    if (params.toString()) {
        baseUrl += '?' + params.toString();
    }
    
    window.location.href = baseUrl;
}

// Función global para eliminar documento
function deleteDocument(docId) {
    if (window.mostrarDialogoConfirmacion) {
        window.mostrarDialogoConfirmacion(
            '¿Estás seguro de que deseas eliminar este documento?',
            'Esta acción no se puede deshacer.',
            () => {
                executeDelete(docId);
            }
        );
    } else {
        if (confirm('¿Estás seguro de que deseas eliminar este documento?')) {
            executeDelete(docId);
        }
    }
}

function executeDelete(docId) {
    const deleteUrl = '/knowledge/delete/' + docId;
    
    fetch(deleteUrl, {
        method: 'POST',
        headers: { 
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Error al eliminar el documento.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al eliminar el documento.');
    });
}

// Función para obtener CSRF token
function getCSRFToken() {
    const token = document.querySelector('meta[name=csrf-token]');
    return token ? token.getAttribute('content') : '';
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Función para validar formularios
function validateDocumentForm(form) {
    const nombre = form.querySelector('input[name="nombre"]');
    const archivo = form.querySelector('input[name="archivo"]');
    
    if (!nombre.value.trim()) {
        showNotification('El nombre del documento es obligatorio', 'error');
        return false;
    }
    
    if (!archivo.files.length) {
        showNotification('Debes seleccionar un archivo', 'error');
        return false;
    }
    
    return true;
}

// Exponer funciones globalmente
window.openCategory = openCategory;
window.deleteDocument = deleteDocument;
window.showNotification = showNotification;
window.validateDocumentForm = validateDocumentForm;
