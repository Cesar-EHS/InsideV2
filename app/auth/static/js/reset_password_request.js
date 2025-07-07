document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const submitBtn = document.getElementById('resetBtn');

  form.addEventListener('submit', () => {
    // Desactiva el botón para evitar múltiples envíos
    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando...';
  });
});
