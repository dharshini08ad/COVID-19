/* Dashboard charts — COVID case trend + resource utilisation */
(function () {
  'use strict';

  function initDashCharts() {
    if (typeof Chart === 'undefined') {
      setTimeout(initDashCharts, 100);
      return;
    }

    var dataEl = document.getElementById('dashboard-data');
    if (!dataEl) return;
    var D = window.__DASH_DATA__;
    if (!D) {
      try {
        D = JSON.parse(dataEl.textContent);
        window.__DASH_DATA__ = D;
      } catch (e) {
        return;
      }
    }

    Chart.defaults.font.family = "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#626579';
    Chart.defaults.plugins.legend.display = false;

    var NAVY = '#11152F';
    var PINK = '#F45B91';

    /* Case trend — smooth line chart */
    var trendEl = document.getElementById('caseTrendChart');
    if (trendEl && D.trendLabels && D.trendLabels.length > 0) {
      new Chart(trendEl, {
        type: 'line',
        data: {
          labels: D.trendLabels,
          datasets: [
            {
              label: 'New cases',
              data: D.newCases,
              borderColor: NAVY,
              backgroundColor: 'rgba(17, 21, 47, .06)',
              fill: true,
              tension: 0.4,
              pointRadius: 2,
              pointHoverRadius: 5,
              borderWidth: 2,
            },
            {
              label: 'Recovered',
              data: D.recovered,
              borderColor: PINK,
              backgroundColor: 'rgba(244, 91, 145, .10)',
              fill: true,
              tension: 0.4,
              pointRadius: 2,
              pointHoverRadius: 5,
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          scales: {
            x: { grid: { display: false }, ticks: { maxTicksLimit: 10 } },
            y: { beginAtZero: true, grid: { color: 'rgba(16, 35, 63, .05)' }, border: { display: false } },
          },
          plugins: {
            tooltip: {
              backgroundColor: '#10233f',
              padding: 12,
              cornerRadius: 8,
              titleFont: { weight: '600' },
            },
          },
        },
      });
    }

    /* Resource utilisation — horizontal bars */
    var resEl = document.getElementById('resourceChart');
    if (resEl && D.resourceLabels && D.resourceLabels.length > 0) {
      new Chart(resEl, {
        type: 'bar',
        data: {
          labels: D.resourceLabels,
          datasets: [{
            data: D.resourceUtil,
            backgroundColor: ['#11152F', '#1B2040', '#D94478', '#F45B91', '#2A3054', '#767B9A'],
            borderRadius: 7,
            borderSkipped: false,
            barThickness: 16,
          }],
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { max: 100, grid: { color: 'rgba(16, 35, 63, .05)' }, border: { display: false }, ticks: { callback: function (v) { return v + '%'; } } },
            y: { grid: { display: false }, border: { display: false } },
          },
          plugins: {
            tooltip: {
              backgroundColor: '#10233f',
              padding: 12,
              cornerRadius: 8,
              callbacks: { label: function (c) { return ' ' + c.parsed.x + '% occupied'; } },
            },
          },
        },
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashCharts);
  } else {
    initDashCharts();
  }
})();
