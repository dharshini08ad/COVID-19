/* Beds page — stacked occupancy chart */
(function () {
  'use strict';

  function initBedChart() {
    if (typeof Chart === 'undefined') {
      setTimeout(initBedChart, 100);
      return;
    }

    var dataEl = document.getElementById('bed-data');
    if (!dataEl) return;
    var D = window.__BED_DATA__;
    if (!D) {
      try {
        D = JSON.parse(dataEl.textContent);
        window.__BED_DATA__ = D;
      } catch (e) {
        return;
      }
    }

    var el = document.getElementById('bedChart');
    if (!el || !D.wards || D.wards.length === 0) return;

    Chart.defaults.font.family = "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#626579';
    Chart.defaults.plugins.legend.display = false;

    new Chart(el, {
      type: 'bar',
      data: {
        labels: D.wards,
        datasets: [
          {
            label: 'Occupied',
            data: D.occupied,
            backgroundColor: '#11152F',
            borderRadius: { topLeft: 0, topRight: 0, bottomLeft: 6, bottomRight: 6 },
            borderSkipped: false,
            barThickness: 26,
          },
          {
            label: 'Free',
            data: D.free,
            backgroundColor: '#F8DCE6',
            borderRadius: { topLeft: 6, topRight: 6 },
            borderSkipped: false,
            barThickness: 26,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, grid: { display: false }, border: { display: false }, ticks: { maxRotation: 40, minRotation: 0 } },
          y: { stacked: true, beginAtZero: true, grid: { color: 'rgba(16, 35, 63, .05)' }, border: { display: false } },
        },
        plugins: {
          tooltip: {
            backgroundColor: '#11152F',
            padding: 12,
            cornerRadius: 8,
          },
        },
      },
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBedChart);
  } else {
    initBedChart();
  }
})();
