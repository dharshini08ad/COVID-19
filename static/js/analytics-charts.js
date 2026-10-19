/* Analytics page — monthly trend, daily trend, district doughnut */
(function () {
  'use strict';

  function initAnalyticsCharts() {
    if (typeof Chart === 'undefined') {
      setTimeout(initAnalyticsCharts, 100);
      return;
    }

    var dataEl = document.getElementById('analytics-data');
    if (!dataEl) return;
    var D = window.__ANALYTICS_DATA__;
    if (!D) {
      try {
        D = JSON.parse(dataEl.textContent);
        window.__ANALYTICS_DATA__ = D;
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
    var PINK_DEEP = '#D94478';
    var NAVY_3 = '#2A3054';
    var SLATE = '#626579';

    var tooltipBase = {
      backgroundColor: '#11152F',
      padding: 12,
      cornerRadius: 8,
      titleFont: { weight: '600' },
    };

    /* Monthly multi-line */
    var monthlyEl = document.getElementById('monthlyChart');
    if (monthlyEl && D.monthlyLabels && D.monthlyLabels.length > 0) {
      new Chart(monthlyEl, {
        type: 'line',
        data: {
          labels: D.monthlyLabels,
          datasets: [
            {
              label: 'New positive cases',
              data: D.monthlyCases,
              borderColor: NAVY,
              backgroundColor: 'rgba(17,21,47,.08)',
              fill: true,
              tension: 0.35,
              borderWidth: 2.5,
              pointRadius: 3,
              pointBackgroundColor: NAVY,
              pointHoverRadius: 6,
            },
            {
              label: 'Recoveries recorded',
              data: D.monthlyRecovered,
              borderColor: PINK,
              backgroundColor: 'rgba(244,91,145,.14)',
              fill: true,
              tension: 0.35,
              borderWidth: 2.5,
              pointRadius: 3,
              pointBackgroundColor: PINK,
              pointHoverRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true, grid: { color: 'rgba(17,21,47,.06)' }, border: { display: false } },
          },
          plugins: { tooltip: tooltipBase },
        },
      });
    }

    /* Daily trend bars */
    var dailyEl = document.getElementById('dailyChart');
    if (dailyEl && D.dailyLabels && D.dailyLabels.length > 0) {
      new Chart(dailyEl, {
        type: 'bar',
        data: {
          labels: D.dailyLabels,
          datasets: [
            {
              label: 'New positive intake',
              data: D.dailyNew,
              backgroundColor: NAVY,
              borderRadius: 4,
              borderSkipped: false,
            },
            {
              label: 'Recoveries',
              data: D.dailyRecovered,
              backgroundColor: 'rgba(244,91,145,.65)',
              borderRadius: 4,
              borderSkipped: false,
            },
            {
              type: 'line',
              label: 'Active inpatient estimate',
              data: D.dailyActive,
              borderColor: PINK_DEEP,
              backgroundColor: 'rgba(217,68,120,.08)',
              tension: 0.2,
              borderWidth: 2.5,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { stacked: false, grid: { display: false }, ticks: { maxTicksLimit: 10 } },
            y: { beginAtZero: true, grid: { color: 'rgba(17,21,47,.06)' }, border: { display: false } },
          },
          plugins: { tooltip: tooltipBase },
        },
      });
    }

    /* District doughnut */
    var districtEl = document.getElementById('districtChart');
    if (districtEl && D.districtNames && D.districtNames.length > 0) {
      new Chart(districtEl, {
        type: 'doughnut',
        data: {
          labels: D.districtNames,
          datasets: [{
            data: D.districtActive,
            backgroundColor: [
              NAVY, '#2A3054', '#3D4573', SLATE, '#767B9A',
              PINK_DEEP, PINK, '#F8A5C2', '#C44569', '#574B90', '#303952', '#FBE3EC'
            ],
            borderWidth: 2,
            borderColor: '#F7F0E6',
            hoverOffset: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '62%',
          plugins: {
            tooltip: {
              backgroundColor: '#11152F',
              padding: 12,
              cornerRadius: 8,
              callbacks: {
                label: function (c) {
                  return ' ' + c.label + ': ' + c.parsed + ' active inpatients';
                },
              },
            },
          },
        },
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnalyticsCharts);
  } else {
    initAnalyticsCharts();
  }
})();
