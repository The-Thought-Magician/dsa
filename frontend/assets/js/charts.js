class ChartsManager {
    constructor() {
        this.charts = {};
    }

    renderCharts() {
        this.renderCoverageChart();
        this.renderImplementationChart();
    }

    renderCoverageChart() {
        const ctx = document.getElementById('coverageChart').getContext('2d');
        const stats = window.app.data.stats;

        if (this.charts.coverage) {
            this.charts.coverage.destroy();
        }

        const coverageData = {
            labels: ['Python Solutions', 'C++ Solutions', 'Missing'],
            datasets: [{
                data: [
                    stats.python_solutions,
                    stats.cpp_solutions,
                    (stats.total_problems * 2) - stats.python_solutions - stats.cpp_solutions
                ],
                backgroundColor: [
                    '#28a745',
                    '#17a2b8',
                    '#dc3545'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        };

        this.charts.coverage = new Chart(ctx, {
            type: 'doughnut',
            data: coverageData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderImplementationChart() {
        const ctx = document.getElementById('implementationChart').getContext('2d');
        const stats = window.app.data.stats;

        if (this.charts.implementation) {
            this.charts.implementation.destroy();
        }

        const implementationData = {
            labels: ['Exact Matches', 'Approximate Matches', 'Missing Mappings'],
            datasets: [{
                label: 'Problem Mappings',
                data: [
                    stats.exact_matches,
                    stats.approx_matches,
                    stats.total_problems - stats.exact_matches - stats.approx_matches
                ],
                backgroundColor: [
                    '#28a745',
                    '#ffc107',
                    '#dc3545'
                ],
                borderWidth: 1
            }]
        };

        this.charts.implementation = new Chart(ctx, {
            type: 'bar',
            data: implementationData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = stats.total_problems;
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45
                        }
                    }
                }
            }
        });
    }

    renderSectionProgressChart(coverageData) {
        const ctx = document.getElementById('sectionProgressChart');
        if (!ctx) return;

        if (this.charts.sectionProgress) {
            this.charts.sectionProgress.destroy();
        }

        const sections = Object.entries(coverageData.coverage_by_section)
            .sort((a, b) => a[1].step_number - b[1].step_number);

        const sectionNames = sections.map(([name, _]) => {
            return name.length > 20 ? name.substring(0, 20) + '...' : name;
        });

        const problemCounts = sections.map(([_, data]) => data.problem_count);
        const fileCounts = sections.map(([_, data]) => data.file_count);

        const sectionData = {
            labels: sectionNames,
            datasets: [{
                label: 'Problems',
                data: problemCounts,
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }, {
                label: 'Files',
                data: fileCounts,
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        };

        this.charts.sectionProgress = new Chart(ctx, {
            type: 'bar',
            data: sectionData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45
                        }
                    }
                }
            }
        });
    }

    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

let chartsManager;

document.addEventListener('DOMContentLoaded', () => {
    chartsManager = new ChartsManager();
});

window.renderCharts = () => {
    if (chartsManager) {
        chartsManager.renderCharts();
    }
};

App.prototype.renderCharts = function() {
    if (chartsManager) {
        chartsManager.renderCharts();
    }
};