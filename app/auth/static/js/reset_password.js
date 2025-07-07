document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('password');
  const confirmInput = document.getElementById('confirm_password');
  const eyeIcon1 = document.getElementById('eyeIcon1');
  const eyeIcon2 = document.getElementById('eyeIcon2');
  const form = document.getElementById('resetPasswordForm');

  // Toggle contraseña nueva
  eyeIcon1.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    eyeIcon1.classList.toggle('ph-eye');
    eyeIcon1.classList.toggle('ph-eye-slash');
  });

  // Toggle confirmación
  eyeIcon2.addEventListener('click', () => {
    const isPassword = confirmInput.type === 'password';
    confirmInput.type = isPassword ? 'text' : 'password';
    eyeIcon2.classList.toggle('ph-eye');
    eyeIcon2.classList.toggle('ph-eye-slash');
  });

  // Validación básica en submit
  form.addEventListener('submit', (e) => {
    if (!passwordInput.value || !confirmInput.value) {
      e.preventDefault();
      alert("Por favor, complete ambos campos de contraseña.");
      return;
    }
    if (passwordInput.value !== confirmInput.value) {
      e.preventDefault();
      alert("Las contraseñas no coinciden.");
    }
  });
});
