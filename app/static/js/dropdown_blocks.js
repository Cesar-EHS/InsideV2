document.addEventListener('DOMContentLoaded', function () {
  function setupDropdown(toggleId, contentId, arrowId) {
    const toggle = document.getElementById(toggleId);
    const content = document.getElementById(contentId);
    const arrow = document.getElementById(arrowId);

    toggle.addEventListener('click', function () {
      const isOpen = !content.classList.contains('hidden');
      content.classList.toggle('hidden');
      arrow.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
    });
  }

  setupDropdown('recursos-toggle', 'recursos-content', 'recursos-arrow');
  setupDropdown('actividades-toggle', 'actividades-content', 'actividades-arrow');
});