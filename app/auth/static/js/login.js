document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const emailInput = form.querySelector('input[type="email"]');
  const passwordInput = form.querySelector('input[type="password"]');

  // Crear o reutilizar un contenedor para mostrar errores
  function createErrorMessage(input) {
    let error = input.parentElement.querySelector('.error-message');
    if (!error) {
      error = document.createElement('div');
      error.className = 'error-message';
      input.parentElement.appendChild(error);
    }
    return error;
  }

  function validateEmail(email) {
    // Validación básica de email con regex simple
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  form.addEventListener('submit', (e) => {
    let valid = true;

    // Validar email
    const emailError = createErrorMessage(emailInput);
    if (emailInput.value.trim() === '') {
      emailError.textContent = 'El correo electrónico es obligatorio.';
      valid = false;
    } else if (!validateEmail(emailInput.value.trim())) {
      emailError.textContent = 'Por favor ingresa un correo electrónico válido.';
      valid = false;
    } else {
      emailError.textContent = '';
    }

    // Validar contraseña
    const passError = createErrorMessage(passwordInput);
    if (passwordInput.value.trim() === '') {
      passError.textContent = 'La contraseña es obligatoria.';
      valid = false;
    } else {
      passError.textContent = '';
    }

    if (!valid) {
      e.preventDefault();
    }
  });

  // Limpiar mensaje de error al escribir
  [emailInput, passwordInput].forEach(input => {
    input.addEventListener('input', () => {
      const error = input.parentElement.querySelector('.error-message');
      if (error) error.textContent = '';
    });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const passwordInput = document.getElementById('password');
  const eyeIcon = document.getElementById('eyeIcon');

  eyeIcon.addEventListener('click', () => {
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      eyeIcon.classList.remove('ph-eye');
      eyeIcon.classList.add('ph-eye-slash');
    } else {
      passwordInput.type = 'password';
      eyeIcon.classList.remove('ph-eye-slash');
      eyeIcon.classList.add('ph-eye');
    }
  });
});
