document.addEventListener('DOMContentLoaded', function () {
  const addBtn = document.getElementById('add-resource-btn');
  const fileInput = document.getElementById('add-resource-input');
  const recursosContainer = document.getElementById('recursos-container');

  // Función para agregar botón eliminar a cada recurso
  function addDeleteButton(div) {
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'ml-2 p-1 rounded-full hover:bg-red-100';
    deleteBtn.title = 'Eliminar recurso';
    deleteBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    `;
    deleteBtn.addEventListener('click', function () {
      div.remove();
    });
    div.appendChild(deleteBtn);
  }

  // Añadir botón eliminar a los recursos existentes
  recursosContainer.querySelectorAll('.bg-white.rounded-xl.shadow.p-4').forEach(function(div) {
    addDeleteButton(div);
  });

  if (addBtn && fileInput && recursosContainer) {
    addBtn.addEventListener('click', function () {
      fileInput.click();
    });

    fileInput.addEventListener('change', function () {
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const ext = file.name.split('.').pop().toLowerCase();
        let iconSrc = '';
        if (ext === 'pdf') iconSrc = '/static/img/pdf.png';
        else if (['doc', 'docx'].includes(ext)) iconSrc = '/static/img/oficina.png';
        else if (ext === 'ppt') iconSrc = '/static/img/ppt.png';
        else if (ext === 'xlsx') iconSrc = '/static/img/xlsx.png';
        else if (ext === 'png') iconSrc = '/static/img/png.png';

        const div = document.createElement('div');
        div.className = 'bg-white rounded-xl shadow p-4 flex flex-col items-center';
        if (iconSrc) {
          const img = document.createElement('img');
          img.src = iconSrc;
          img.className = 'w-12 h-12 mb-2';
          div.appendChild(img);
        }
        const span = document.createElement('span');
        span.className = 'text-xs text-gray-700';
        span.textContent = file.name;
        div.appendChild(span);

        addDeleteButton(div);

        recursosContainer.insertBefore(div, addBtn);
      }
    });
  }
});