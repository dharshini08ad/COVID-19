/* Appointments page — status filter + schedule modal */
(function () {
  'use strict';

  var filter = document.getElementById('apptStatusFilter');
  var table = document.getElementById('apptTable');

  if (filter && table) {
    var rows = Array.prototype.slice.call(table.querySelectorAll('tbody tr'));
    filter.addEventListener('change', function () {
      var val = filter.value;
      rows.forEach(function (row) {
        row.hidden = !!val && row.getAttribute('data-status') !== val;
      });
    });
  }

  /* Schedule modal */
  var modal = document.getElementById('apptModal');
  var openBtn = document.getElementById('newApptBtn');
  var closeBtn = document.getElementById('closeApptModal');
  var cancelBtn = document.getElementById('cancelApptModal');

  function openModal() { if (modal) modal.hidden = false; }
  function closeModal() { if (modal) modal.hidden = true; }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
  if (modal && !modal.hidden) openModal();
})();
