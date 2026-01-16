/**
 * Chart.js integration for A2Z DSA Learning System
 * Handles all chart rendering with defensive checks
 */

class ChartsManager {
    constructor() {
        this.charts = {};
        this.initialized = false;
    }

    /**
     * Wait for window.app to be available with stats data
     */
    async waitForAppData(maxWait = 5000) {
        const startTime = Date.now();
        while (Date.now() - startTime < maxWait) {
            if (window.app && window.app.data && window.app.data.stats) {
                return window.app.data.stats;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        return null;
    }

    /**
     * Initialize charts manager
     */
    async init() {
        if (this.initialized) {
            return;
        }

        // Wait for Chart.js to be available
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded yet');
            return false;
        }

        this.initialized = true;
        return true;
    }

    /**
     * Render all charts
     */
    async renderCharts() {
        await this.init();

        const stats = await this.waitForAppData();
        if (!stats) {
            console.warn('No stats data available for charts');
            return;
        }

        this.renderCoverageChart(stats);
        this.renderImplementationChart(stats);
    }

    /**
     * Render coverage doughnut chart
     */
    renderCoverageChart(stats) {
        const canvas = document.getElementById('coverageChart');
        if (!canvas) {
            console.warn('coverageChart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.warn('Could not get 2d context for coverageChart');
            return;
        }

        // Destroy existing chart
        if (this.charts.coverage) {
            this.charts.coverage.destroy();
        }

        const coverageData = {
            labels: ['Python Solutions', 'C++ Solutions', 'Missing'],
            datasets: [{
                data: [
                    stats.python_solutions || 0,
                    stats.cpp_solutions || 0,
                    (stats.total_problems * 2) - (stats.python_solutions || 0) - (stats.cpp_solutions || 0)
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

    /**
     * Render implementation bar chart
     */
    renderImplementationChart(stats) {
        const canvas = document.getElementById('implementationChart');
        if (!canvas) {
            console.warn('implementationChart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.warn('Could not get 2d context for implementationChart');
            return;
        }

        // Destroy existing chart
        if (this.charts.implementation) {
            this.charts.implementation.destroy();
        }

        const implementationData = {
            labels: ['Exact Matches', 'Approximate Matches', 'Missing Mappings'],
            datasets: [{
                label: 'Problem Mappings',
                data: [
                    stats.exact_matches || 0,
                    stats.approx_matches || 0,
                    (stats.total_problems || 0) - (stats.exact_matches || 0) - (stats.approx_matches || 0)
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
                                const total = stats.total_problems || 1;
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

    /**
     * Render section progress chart
     */
    renderSectionProgressChart(coverageData) {
        const canvas = document.getElementById('sectionProgressChart');
        if (!canvas) {
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            return;
        }

        // Destroy existing chart
        if (this.charts.sectionProgress) {
            this.charts.sectionProgress.destroy();
        }

        const sections = Object.entries(coverageData.coverage_by_section || {})
            .sort((a, b) => a[1].step_number - b[1].step_number);

        const sectionNames = sections.map(([name]) => {
            return name.length > 20 ? name.substring(0, 20) + '...' : name;
        });

        const problemCounts = sections.map(([, data]) => data.problem_count || 0);
        const fileCounts = sections.map(([, data]) => data.file_count || 0);

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

    /**
     * Destroy all charts
     */
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Create singleton instance
let chartsManager = null;

// Initialize on DOM ready
function initializeCharts() {
    if (chartsManager) {
        return chartsManager;
    }

    chartsManager = new ChartsManager();
    return chartsManager;
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initializeCharts();
    });
} else {
    initializeCharts();
}

// Global function to render charts (called by app.js)
window.renderCharts = async function() {
    const manager = initializeCharts();
    await manager.renderCharts();
};

// Export for module usage
export { ChartsManager, initializeCharts };
export default chartsManager;
