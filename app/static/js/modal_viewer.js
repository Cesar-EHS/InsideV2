document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('pdf-modal');
  const viewer = document.getElementById('pdf-viewer');
  const closeBtn = document.getElementById('close-pdf-modal');

  // Crea el contenedor de imagen si no existe
  let imgViewer = document.getElementById('img-viewer');
  if (!imgViewer) {
    imgViewer = document.createElement('img');
    imgViewer.id = 'img-viewer';
    imgViewer.className = 'flex-1 w-full rounded-lg border hidden';
    viewer.parentNode.insertBefore(imgViewer, viewer.nextSibling);
  }

  document.querySelectorAll('.recurso-link').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const ext = el.getAttribute('data-extension');
      const url = el.getAttribute('data-url');
      if (ext === 'pdf') {
        e.preventDefault();
        viewer.src = url;
        viewer.classList.remove('hidden');
        imgViewer.classList.add('hidden');
        modal.classList.remove('hidden');
      } else if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'].includes(ext)) {
        e.preventDefault();
        imgViewer.src = url;
        imgViewer.classList.remove('hidden');
        viewer.classList.add('hidden');
        modal.classList.remove('hidden');
      } else {
        // Descargar otros archivos
        e.preventDefault();
        const link = document.createElement('a');
        link.href = url;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    });
  });

  closeBtn.addEventListener('click', function () {
    modal.classList.add('hidden');
    viewer.src = '';
    imgViewer.src = '';
  });

  modal.addEventListener('click', function (e) {
    if (e.target === modal) {
      modal.classList.add('hidden');
      viewer.src = '';
      imgViewer.src = '';
    }
  });
});