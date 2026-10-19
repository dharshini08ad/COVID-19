/* Staff page — add modal functionality */
(function () {
  'use strict';

  /* Add staff modal */
  var modal = document.getElementById('staffModal');
  var openBtn = document.getElementById('addStaffBtn');
  var closeBtn = document.getElementById('closeStaffModal');
  var cancelBtn = document.getElementById('cancelStaffModal');
  var form = document.getElementById('staffForm');

  function openModal() { if (modal) modal.hidden = false; }
  function closeModal() { if (modal) modal.hidden = true; }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
  if (modal && !modal.hidden) openModal();
})();
