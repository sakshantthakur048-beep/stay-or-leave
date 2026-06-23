/* ============================================================
   Stay or Leave — Auth forms behavior
   One file handles login, signup, forgot-password, and reset-password
   since each page only ever has one of these forms present.
   ============================================================ */

(function () {
  'use strict';

  function setFieldError(fieldId, hasError) {
    const field = document.getElementById(fieldId);
    if (field) field.classList.toggle('has-error', hasError);
  }

  function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
  }

  function isValidPassword(value) {
    return value.length >= 8 && /[A-Za-z]/.test(value) && /\d/.test(value);
  }

  function setLoading(btn, isLoading, loadingText) {
    if (!btn) return;
    if (isLoading) {
      btn.dataset.originalText = btn.textContent;
      btn.textContent = loadingText || 'Please wait...';
      btn.disabled = true;
    } else {
      btn.textContent = btn.dataset.originalText || btn.textContent;
      btn.disabled = false;
    }
  }

  /* ---------- Password strength meter ---------- */
  function initPasswordStrength() {
    const input = document.getElementById('password');
    const meter = document.getElementById('password-strength');
    if (!input || !meter) return;

    input.addEventListener('input', () => {
      const val = input.value;
      let score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score++;
      if (/\d/.test(val) && /[^A-Za-z0-9]/.test(val)) score++;
      else if (/\d/.test(val)) score += 0.5;

      meter.classList.remove('weak', 'medium', 'strong');
      if (val.length === 0) return;
      if (score < 1) meter.classList.add('weak');
      else if (score < 2) meter.classList.add('medium');
      else meter.classList.add('strong');
    });
  }

  /* ---------- Login ---------- */
  function initLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;

      const emailOk = isValidEmail(email);
      const passwordOk = password.length > 0;
      setFieldError('email-field', !emailOk);
      setFieldError('password-field', !passwordOk);
      if (!emailOk || !passwordOk) return;

      const btn = document.getElementById('login-submit-btn');
      setLoading(btn, true, 'Logging in...');
      try {
        const data = await window.SOL.api.post('/auth/login', { email, password });
        window.SOL.auth.setTokens(data);
        window.SOL.auth.setCachedUser(data.user);
        window.SOL.ui.showToast(`Welcome back, ${data.user.name.split(' ')[0]}`, 'success');
        setTimeout(() => (window.location.href = 'index.html'), 600);
      } catch (err) {
        window.SOL.ui.showToast(err.message || 'Could not log in', 'error');
      } finally {
        setLoading(btn, false);
      }
    });
  }

  /* ---------- Signup ---------- */
  function initSignupForm() {
    const form = document.getElementById('signup-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;

      const nameOk = name.length >= 2;
      const emailOk = isValidEmail(email);
      const passwordOk = isValidPassword(password);
      setFieldError('name-field', !nameOk);
      setFieldError('email-field', !emailOk);
      setFieldError('password-field', !passwordOk);
      if (!nameOk || !emailOk || !passwordOk) return;

      const btn = document.getElementById('signup-submit-btn');
      setLoading(btn, true, 'Creating account...');
      try {
        await window.SOL.api.post('/auth/register', { name, email, password });
        window.SOL.ui.showToast('Account created — check your email to verify it', 'success');
        setTimeout(() => (window.location.href = 'login.html'), 1200);
      } catch (err) {
        window.SOL.ui.showToast(err.message || 'Could not create your account', 'error');
      } finally {
        setLoading(btn, false);
      }
    });
  }

  /* ---------- Forgot password ---------- */
  function initForgotForm() {
    const form = document.getElementById('forgot-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const emailOk = isValidEmail(email);
      setFieldError('email-field', !emailOk);
      if (!emailOk) return;

      const btn = document.getElementById('forgot-submit-btn');
      setLoading(btn, true, 'Sending...');
      try {
        await window.SOL.api.post('/auth/forgot-password', { email });
        window.SOL.ui.showToast("If that email exists, a reset link is on its way", 'success');
        form.reset();
      } catch (err) {
        window.SOL.ui.showToast(err.message || 'Something went wrong', 'error');
      } finally {
        setLoading(btn, false);
      }
    });
  }

  /* ---------- Reset password ---------- */
  function initResetForm() {
    const form = document.getElementById('reset-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const password = document.getElementById('password').value;
      const passwordOk = isValidPassword(password);
      setFieldError('password-field', !passwordOk);
      if (!passwordOk) return;

      const token = new URLSearchParams(window.location.search).get('token');
      if (!token) {
        window.SOL.ui.showToast('This reset link is missing its token — request a new one', 'error');
        return;
      }

      const btn = document.getElementById('reset-submit-btn');
      setLoading(btn, true, 'Updating...');
      try {
        await window.SOL.api.post('/auth/reset-password', { token, new_password: password });
        window.SOL.ui.showToast('Password updated — log in with your new password', 'success');
        setTimeout(() => (window.location.href = 'login.html'), 1200);
      } catch (err) {
        window.SOL.ui.showToast(err.message || 'Could not reset your password', 'error');
      } finally {
        setLoading(btn, false);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initPasswordStrength();
    initLoginForm();
    initSignupForm();
    initForgotForm();
    initResetForm();
  });
})();
