// ═══════════════════════════════════════════════════════════
//  SHAP EXPLAINABILITY MODULE
//  Loads and displays real SHAP feature importance from
//  the trained model. Shows users WHY the price was predicted.
// ═══════════════════════════════════════════════════════════

async function loadSHAPExplanation() {
    try {
        const response = await fetch('/api/v1/explain', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({})
        });

        if (!response.ok) return;

        const data = await response.json();
        if (!data.success) return;

        renderSHAPChart(data.feature_importance);

    } catch (err) {
        console.log('SHAP explanation not available:', err);
    }
}

function renderSHAPChart(featureImportance) {
    const canvas = document.getElementById('shapChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    const labels = featureImportance.map(f =>
        f.feature.charAt(0).toUpperCase() + f.feature.slice(1).replace('_', ' ')
    );
    const values = featureImportance.map(f => Math.round(f.importance));

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#9d9a91' : '#5c5650';
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';

    if (window.shapChartInstance) window.shapChartInstance.destroy();

    window.shapChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'SHAP Importance ($)',
                data:   values,
                backgroundColor: [
                    '#c9a84c','#e8c97a','#5b9cf6','#4caf7d',
                    '#f5a623','#c9a84c','#5b9cf6','#4caf7d',
                    '#f27070','#9b8ae8'
                ].slice(0, labels.length),
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',  // Horizontal bar chart
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => ` $${ctx.raw.toLocaleString()} avg impact`
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: textColor,
                        callback: v => '$' + (v/1000).toFixed(0) + 'K',
                        font: { family: 'DM Mono', size: 10 }
                    },
                    grid: { color: gridColor }
                },
                y: {
                    ticks: {
                        color: textColor,
                        font: { family: 'DM Sans', size: 11 }
                    },
                    grid: { color: gridColor }
                }
            }
        }
    });
}

// Load SHAP data when page loads
document.addEventListener('DOMContentLoaded', loadSHAPExplanation);