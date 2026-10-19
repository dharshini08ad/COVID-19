/* Meridian Care HMS — shared UI behaviours (mock interactions only) */
(function () {
  'use strict';

  /* ---------- Mobile sidebar ---------- */
  var sidebar = document.getElementById('appSidebar');
  var toggle = document.getElementById('sidebarToggle');
  var backdrop = document.getElementById('sidebarBackdrop');

  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('show');
  }

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      if (backdrop) backdrop.classList.toggle('show', sidebar.classList.contains('open'));
    });
  }
  if (backdrop) backdrop.addEventListener('click', closeSidebar);

  /* ---------- Mock toast ---------- */
  var toast = document.getElementById('toastMock');
  var toastTimer;

  window.showToast = function (message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('show'); }, 2600);
  };

  document.querySelectorAll('[data-mock-action]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      window.showToast(el.getAttribute('data-mock-action'));
    });
  });
})();
