// alert('Theme JS loaded!');
if (window.history.replaceState) {
  window.history.replaceState({}, document.title, '/auth/login');
}

document.addEventListener('DOMContentLoaded', function () {
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  const nextBtn = document.getElementById('nextStepBtn');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const usernameError = document.getElementById('username-error');
  const passwordError = document.getElementById('password-error');
  const form = document.getElementById('kc-form-login');

  function showStep2() {
    step1.classList.remove('active');
    step2.classList.add('active');
    passwordInput.focus();
  }

  function validateUsername() {
    const username = usernameInput.value.trim();
    if (!username) {
      usernameError.textContent = "Enter your email or username.";
      usernameInput.setAttribute('aria-invalid', 'true');
      return false;
    }
    usernameError.textContent = "";
    usernameInput.removeAttribute('aria-invalid');
    return true;
  }

  function validatePassword() {
    const password = passwordInput.value.trim();
    if (!password) {
      passwordError.textContent = "Enter your password.";
      passwordInput.setAttribute('aria-invalid', 'true');
      return false;
    }
    passwordError.textContent = "";
    passwordInput.removeAttribute('aria-invalid');
    return true;
  }

  nextBtn.addEventListener('click', function () {
    if (validateUsername()) {
      showStep2();
    }
  });

  form.addEventListener('submit', function (e) {
    if (!validatePassword()) {
      e.preventDefault();
    }
  });

  document.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
      if (step1.classList.contains('active')) {
        e.preventDefault();
        if (validateUsername()) {
          showStep2();
        }
      }
    }
  });
});