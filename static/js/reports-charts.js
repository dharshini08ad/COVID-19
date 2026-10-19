/* Reports page — admissions and discharges from the selected range */
(function () {
  'use strict';

  function initReportChart() {
    if (typeof Chart === 'undefined') {
      setTimeout(initReportChart, 100);
      return;
    }

    var dataEl = document.getElementById('report-data');
    if (!dataEl) return;
    var D = window.__REPORT_DATA__;
    if (!D) {
      try {
        D = JSON.parse(dataEl.textContent);
        window.__REPORT_DATA__ = D;
      } catch (e) {
        return;
      }
    }

    var reportEl = document.getElementById('reportChart');
    if (!reportEl || !D.labels || D.labels.length === 0) return;

    Chart.defaults.font.family = "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#626579';
    Chart.defaults.plugins.legend.display = false;

    var NAVY = '#11152F';
    var PINK_SOFT = 'rgba(244,91,145,.65)';

    var tooltipBase = {
      backgroundColor: '#11152F',
      padding: 12,
      cornerRadius: 8,
      titleFont: { weight: '600' },
    };

    new Chart(reportEl, {
      type: 'bar',
      data: {
        labels: D.labels,
        datasets: [
          { label: 'Admissions', data: D.admissions, backgroundColor: NAVY, borderRadius: 5, borderSkipped: false, barThickness: 22 },
          { label: 'Discharges', data: D.discharges, backgroundColor: PINK_SOFT, borderRadius: 5, borderSkipped: false, barThickness: 22 },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, border: { display: false } },
          y: { beginAtZero: true, grid: { color: 'rgba(17,21,47,.05)' }, border: { display: false } },
        },
        plugins: { tooltip: tooltipBase },
      },
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReportChart);
  } else {
    initReportChart();
  }
})();
