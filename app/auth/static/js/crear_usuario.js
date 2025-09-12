document.addEventListener('DOMContentLoaded', () => {
  const agregarUsuarioBtn = document.getElementById('agregarUsuarioBtn');

  agregarUsuarioBtn.addEventListener('click', () => {
    window.location.href = agregarUsuarioBtn.dataset.url;
  });
});
