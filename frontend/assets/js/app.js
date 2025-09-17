const API_BASE_URL = '';

class App {
    constructor() {
        this.currentSection = 'dashboard';
        this.data = {
            topics: [],
            stats: null,
            coverage: null,
            studyPlan: null
        };
        this.init();
    }

    async init() {
        try {
            console.log('App initializing...');
            await this.loadInitialData();
            this.setupEventListeners();
            this.setupNavigation();

            // Show initial section based on hash or default to dashboard
            const hash = window.location.hash.slice(1) || 'dashboard';
            this.showSection(hash);
            console.log('App initialized successfully');
        } catch (error) {
            console.error('App initialization failed:', error);
            this.showError('Application failed to initialize: ' + error.message);
        }
    }

    async loadInitialData() {
        try {
            this.showLoading(true);

            const [stats, topics, coverage] = await Promise.all([
                this.fetchStats(),
                this.fetchTopics(),
                this.fetchCoverage()
            ]);

            this.data.stats = stats;
            this.data.topics = topics;
            this.data.coverage = coverage;

            this.renderDashboard();

        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load data. Please refresh the page.');
        } finally {
            this.showLoading(false);
        }
    }

    setupEventListeners() {
        const topicSearch = document.getElementById('topic-search');
        const statusFilter = document.getElementById('status-filter');
        const sectionFilter = document.getElementById('section-filter');

        if (topicSearch) {
            topicSearch.addEventListener('input',
                this.debounce(() => this.loadTopics(), 300)
            );
        }

        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.loadTopics());
        }

        if (sectionFilter) {
            sectionFilter.addEventListener('change', () => this.loadTopics());
        }
    }

    setupNavigation() {
        // Handle hash changes for navigation
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.slice(1) || 'dashboard';
            console.log('Hash changed to:', hash);
            this.showSection(hash);
        });

        // Handle navigation link clicks
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const hash = link.getAttribute('href').slice(1);
                if (hash) {
                    console.log('Navigation link clicked:', hash);
                    window.location.hash = hash;
                }
            });
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async fetchStats() {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        return await response.json();
    }

    async fetchTopics(section = null, status = null) {
        const params = new URLSearchParams();
        if (section) params.append('section', section);
        if (status) params.append('status', status);

        const response = await fetch(`${API_BASE_URL}/api/topics?${params}`);
        if (!response.ok) throw new Error('Failed to fetch topics');
        return await response.json();
    }

    async fetchCoverage() {
        const response = await fetch(`${API_BASE_URL}/api/coverage`);
        if (!response.ok) throw new Error('Failed to fetch coverage');
        return await response.json();
    }

    async fetchStudyPlan() {
        const response = await fetch(`${API_BASE_URL}/api/study-plan`);
        if (!response.ok) throw new Error('Failed to fetch study plan');
        return await response.json();
    }

    async fetchTodayPlan() {
        const response = await fetch(`${API_BASE_URL}/api/study-plan/today`);
        if (!response.ok) throw new Error('Failed to fetch today plan');
        return await response.json();
    }

    showSection(sectionName) {
        console.log('showSection called with:', sectionName);

        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
            console.log('Hiding section:', section.id);
        });

        // Show target section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            console.log('Showing section:', targetSection.id);
            this.currentSection = sectionName;

            // Load section-specific data
            switch(sectionName) {
                case 'topics':
                    console.log('Loading topics data');
                    this.loadTopics();
                    break;
                case 'coverage':
                    console.log('Loading coverage data');
                    this.loadCoverage();
                    break;
                case 'planning':
                    console.log('Loading planning data');
                    this.loadPlanning();
                    break;
                default:
                    console.log('Dashboard section - no additional data loading needed');
            }
        } else {
            console.error('Section not found:', `${sectionName}-section`);
        }
    }

    renderDashboard() {
        this.renderStatsCards();
        this.renderCharts();
    }

    renderStatsCards() {
        console.log('renderStatsCards called');
        const stats = this.data.stats;
        const coverage = this.data.coverage;
        console.log('Stats data:', stats);

        const container = document.getElementById('stats-cards');
        console.log('Container found:', container);

        if (!container) {
            console.error('stats-cards container not found');
            return;
        }

        if (!stats) {
            console.error('No stats data available');
            return;
        }

        const cardsHTML = `
            <div class="col-lg-3 col-md-6">
                <div class="stats-card text-center">
                    <div class="card-icon"><i class="fas fa-book"></i></div>
                    <div class="card-number">${stats.total_sections}</div>
                    <div>Total Sections</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="stats-card text-center">
                    <div class="card-icon"><i class="fas fa-tasks"></i></div>
                    <div class="card-number">${stats.total_problems}</div>
                    <div>Total Problems</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="stats-card text-center">
                    <div class="card-icon"><i class="fas fa-python"></i></div>
                    <div class="card-number">${stats.python_solutions}</div>
                    <div>Python Solutions</div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="stats-card text-center">
                    <div class="card-icon"><i class="fas fa-chart-pie"></i></div>
                    <div class="card-number">${stats.coverage_percentage.toFixed(1)}%</div>
                    <div>Coverage</div>
                </div>
            </div>
        `;

        console.log('Setting innerHTML for stats-cards');
        container.innerHTML = cardsHTML;
        console.log('Stats cards rendered successfully');
    }

    async loadTopics() {
        try {
            this.showLoading(true);

            const searchTerm = document.getElementById('topic-search').value;
            const statusFilter = document.getElementById('status-filter').value;
            const sectionFilter = document.getElementById('section-filter').value;

            const topics = await this.fetchTopics(
                sectionFilter || (searchTerm ? searchTerm : null),
                statusFilter || null
            );

            this.renderTopics(topics);

        } catch (error) {
            console.error('Error loading topics:', error);
            this.showError('Failed to load topics');
        } finally {
            this.showLoading(false);
        }
    }

    renderTopics(topics) {
        const container = document.getElementById('topics-container');

        if (topics.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No topics found matching your criteria.</div>';
            return;
        }

        const topicsHTML = topics.map(topic => `
            <div class="topic-card card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">
                            <span class="badge bg-primary me-2">${topic.step_number}</span>
                            ${topic.title}
                        </h5>
                        <span class="status-badge status-${topic.status}">${topic.status}</span>
                    </div>
                    <p class="card-text text-muted small">${topic.notes}</p>
                    <div class="row text-center">
                        <div class="col-4">
                            <i class="fas fa-tasks text-primary"></i>
                            <div class="small">Problems</div>
                            <strong>${topic.problem_count}</strong>
                        </div>
                        <div class="col-4">
                            <i class="fas fa-file-code text-success"></i>
                            <div class="small">Files</div>
                            <strong>${topic.file_count}</strong>
                        </div>
                        <div class="col-4">
                            <i class="fas fa-tags text-info"></i>
                            <div class="small">Topics</div>
                            <strong>${topic.tags.length}</strong>
                        </div>
                    </div>
                    ${topic.tags.length > 0 ? `
                        <div class="mt-3">
                            ${topic.tags.slice(0, 5).map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('')}
                            ${topic.tags.length > 5 ? `<span class="text-muted">+${topic.tags.length - 5} more</span>` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');

        container.innerHTML = topicsHTML;
    }

    async loadCoverage() {
        try {
            this.showLoading(true);

            if (!this.data.coverage) {
                this.data.coverage = await this.fetchCoverage();
            }

            this.renderCoverage();

        } catch (error) {
            console.error('Error loading coverage:', error);
            this.showError('Failed to load coverage data');
        } finally {
            this.showLoading(false);
        }
    }

    renderCoverage() {
        const coverage = this.data.coverage;

        const gapsHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-exclamation-circle text-warning"></i> Missing Python Implementations</h6>
                    ${coverage.gaps.missing_python.slice(0, 10).map(item => `
                        <div class="gap-item">${item}</div>
                    `).join('')}
                    ${coverage.gaps.missing_python.length > 10 ?
                        `<div class="text-muted">... and ${coverage.gaps.missing_python.length - 10} more</div>` : ''}
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-lightbulb text-info"></i> Recommendations</h6>
                    ${coverage.recommendations.map(rec => `
                        <div class="recommendation-item">${rec}</div>
                    `).join('')}
                </div>
            </div>
        `;

        document.getElementById('gaps-container').innerHTML = gapsHTML;

        const tableBody = document.querySelector('#coverage-table tbody');
        const sectionsHTML = Object.entries(coverage.coverage_by_section)
            .sort((a, b) => a[1].step_number - b[1].step_number)
            .map(([title, info]) => `
                <tr>
                    <td><span class="badge bg-primary">${info.step_number}</span></td>
                    <td>${title}</td>
                    <td><span class="status-badge status-${info.status}">${info.status}</span></td>
                    <td>${info.problem_count}</td>
                    <td>${info.file_count}</td>
                </tr>
            `).join('');

        tableBody.innerHTML = sectionsHTML;
    }

    async loadPlanning() {
        try {
            this.showLoading(true);

            const [todayPlan, studyPlan] = await Promise.all([
                this.fetchTodayPlan().catch(() => null),
                this.fetchStudyPlan()
            ]);

            this.renderPlanning(todayPlan, studyPlan);

        } catch (error) {
            console.error('Error loading planning data:', error);
            this.showError('Failed to load planning data');
        } finally {
            this.showLoading(false);
        }
    }

    renderPlanning(todayPlan, studyPlan) {
        const todayContainer = document.getElementById('today-plan');

        if (todayPlan && todayPlan.tasks.length > 0) {
            const todayHTML = `
                <h4><i class="fas fa-calendar-day"></i> Today's Plan - ${todayPlan.day_name}</h4>
                <p><i class="fas fa-clock"></i> Total time: ${Math.floor(todayPlan.total_time / 60)}h ${todayPlan.total_time % 60}m |
                   <i class="fas fa-tasks"></i> ${todayPlan.task_count} tasks</p>
                <div class="row">
                    ${todayPlan.tasks.map((task, index) => `
                        <div class="col-md-6 mb-3">
                            <div class="card task-card task-type-${task.type}">
                                <div class="card-body">
                                    <h6>${index + 1}. ${task.title}</h6>
                                    <p class="small text-muted">${task.estimated_time}min • ${task.difficulty} • ${task.problems.length} problems</p>
                                    <div class="small">${task.problems.slice(0, 2).join(', ')}${task.problems.length > 2 ? '...' : ''}</div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            todayContainer.innerHTML = todayHTML;
        } else {
            todayContainer.innerHTML = `
                <h4><i class="fas fa-info-circle"></i> No Plan for Today</h4>
                <p>No tasks scheduled for today. Generate a new study plan to get started!</p>
            `;
        }

        this.renderStudyPlan(studyPlan);
    }

    renderStudyPlan(studyPlan) {
        const container = document.getElementById('study-plan-container');

        const planHTML = `
            <div class="mb-4">
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${Math.floor(studyPlan.summary.total_study_time / 60)}h ${studyPlan.summary.total_study_time % 60}m</h4>
                            <small class="text-muted">Total Study Time</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${Math.floor(studyPlan.summary.average_daily_time / 60)}h ${studyPlan.summary.average_daily_time % 60}m</h4>
                            <small class="text-muted">Average Daily</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${studyPlan.summary.total_tasks}</h4>
                            <small class="text-muted">Total Tasks</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${studyPlan.summary.average_tasks_per_day.toFixed(1)}</h4>
                            <small class="text-muted">Tasks per Day</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="accordion" id="studyPlanAccordion">
                ${studyPlan.plans.map((plan, index) => `
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button ${index > 0 ? 'collapsed' : ''}"
                                    type="button" data-bs-toggle="collapse"
                                    data-bs-target="#plan-${index}">
                                <strong>${plan.date} (${plan.day_name})</strong>
                                <span class="ms-auto me-3">
                                    <small>${Math.floor(plan.total_time / 60)}h ${plan.total_time % 60}m • ${plan.task_count} tasks</small>
                                </span>
                            </button>
                        </h2>
                        <div id="plan-${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}"
                             data-bs-parent="#studyPlanAccordion">
                            <div class="accordion-body">
                                ${plan.tasks.length > 0 ? plan.tasks.map((task, taskIndex) => `
                                    <div class="task-card card mb-2 priority-${task.priority}">
                                        <div class="card-body py-2">
                                            <div class="row align-items-center">
                                                <div class="col-md-6">
                                                    <h6 class="mb-1">${taskIndex + 1}. ${task.title}</h6>
                                                    <small class="text-muted">${task.section}</small>
                                                </div>
                                                <div class="col-md-3">
                                                    <small>
                                                        <i class="fas fa-clock"></i> ${task.estimated_time}min<br>
                                                        <i class="fas fa-layer-group"></i> ${task.difficulty}
                                                    </small>
                                                </div>
                                                <div class="col-md-3">
                                                    <small>
                                                        <i class="fas fa-tasks"></i> ${task.problems.length} problems<br>
                                                        <span class="badge bg-secondary">${task.type}</span>
                                                    </small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `).join('') : '<p class="text-muted">No tasks for this day</p>'}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = planHTML;
    }

    async generateNewPlan() {
        try {
            this.showLoading(true);

            const response = await fetch(`${API_BASE_URL}/api/rebuild`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Failed to rebuild data');

            await this.loadPlanning();
            this.showSuccess('New study plan generated successfully!');

        } catch (error) {
            console.error('Error generating new plan:', error);
            this.showError('Failed to generate new plan');
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        console.log('showLoading called:', show);
        const modalElement = document.getElementById('loadingModal');
        console.log('Modal element:', modalElement);

        if (!modalElement) {
            console.warn('Loading modal not found, skipping modal display');
            return;
        }

        try {
            const modal = new bootstrap.Modal(modalElement);
            if (show) {
                modal.show();
            } else {
                modal.hide();
            }
        } catch (error) {
            console.error('Bootstrap modal error:', error);
        }
    }

    showError(message) {
        // Simple error display - could be enhanced with toast notifications
        console.error(message);
        alert(`Error: ${message}`);
    }

    showSuccess(message) {
        // Simple success display - could be enhanced with toast notifications
        console.log(message);
        alert(message);
    }
}

window.showSection = (section) => {
    window.app.showSection(section);
};

window.loadTopics = () => {
    window.app.loadTopics();
};

window.generateNewPlan = () => {
    window.app.generateNewPlan();
};

console.log('app.js loaded');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded fired, creating App');
    try {
        window.app = new App();
        console.log('App created successfully');
    } catch (error) {
        console.error('Failed to create App:', error);
    }
});