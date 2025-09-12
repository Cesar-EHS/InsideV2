document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('password');
  const confirmInput = document.getElementById('confirm_password');
  const eyeIconPassword = document.getElementById('eyeIconPassword');
  const eyeIconConfirmPassword = document.getElementById('eyeIconConfirmPassword');
  const form = document.getElementById('resetPasswordForm');

  // Toggle contraseña nueva
  eyeIconPassword.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    eyeIconPassword.classList.toggle('ph-eye');
    eyeIconPassword.classList.toggle('ph-eye-slash');
  });

  // Toggle confirmación
  eyeIconConfirmPassword.addEventListener('click', () => {
    const isPassword = confirmInput.type === 'password';
    confirmInput.type = isPassword ? 'text' : 'password';
    eyeIconConfirmPassword.classList.toggle('ph-eye');
    eyeIconConfirmPassword.classList.toggle('ph-eye-slash');
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
