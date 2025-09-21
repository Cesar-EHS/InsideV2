document.addEventListener('DOMContentLoaded', function () {

    // --- MANEJAR CLICS EN LAS ACTIVIDADES ---
    const courseContainer = document.getElementById('course-view-container');
    if (courseContainer) {
        courseContainer.addEventListener('click', function(event) {
            const activityItem = event.target.closest('li[data-tipo-actividad]');
            if (!activityItem) return;

            const tipo = activityItem.dataset.tipoActividad;
            const contenido = activityItem.dataset.contenido;
            const titulo = activityItem.querySelector('.flex-1').textContent.trim();

            if (tipo === 'documento') {
                openPdfModal(titulo, contenido);
            }
            // ... (lógica para video, examen) ...
        });
    }

    // --- LÓGICA DEL MODAL DE PDF (VERSIÓN CLÁSICA) ---
    const previewModal = document.getElementById('preview-modal');
    const closePreviewBtn = document.getElementById('close-preview-modal');
    const previewTitle = document.getElementById('preview-title');
    const viewerContainer = document.getElementById('viewerContainer');
    let pdfjsWebApp;

    function openPdfModal(titulo, rutaArchivo) {
        if (!previewModal) return;
        
        // Esta línea es CRUCIAL para que el PDF se cargue
        pdfjsLib.GlobalWorkerOptions.workerSrc = `/static/lib/pdfjs/build/pdf.worker.mjs`;
        
        const simpleFilename = rutaArchivo.replace('cursos/recursos_actividades/', '');
        const pdfUrl = `/cursos/recursos/view/${simpleFilename}`;

        previewTitle.textContent = titulo;
        previewModal.classList.remove('hidden');

        if (!pdfjsWebApp) {
            pdfjsWebApp = new pdfjsViewer.PDFViewerApplication({
                appConfig: viewerContainer,
                mainContainer: viewerContainer,
                viewerContainer: document.getElementById('viewer'),
            });
        }
        
        pdfjsWebApp.open(pdfUrl);
    }
    
    function closePreviewModal() {
        if (previewModal) {
            previewModal.classList.add('hidden');
            if (pdfjsWebApp) pdfjsWebApp.close();
        }
    }
    
    if (closePreviewBtn) {
        closePreviewBtn.addEventListener('click', closePreviewModal);
    }
});