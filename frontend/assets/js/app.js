import { API_BASE_URL } from './config.js';
import { withLoading } from './ui/loading.js';
import { showToast } from './ui/toast.js';
import { QuestionsController } from './questions.js';

class App {
    constructor() {
        this.data = {
            stats: null,
            topics: [],
            coverage: null,
            studyPlan: null,
        };
        this.sections = {};
        this.navLinks = [];
        this.activeSection = 'dashboard';

        this.questionsController = new QuestionsController({
            onNavigate: this.handleQuestionsNavigate.bind(this),
            onStatusChange: this.handleQuestionStatusChange.bind(this),
        });

        document.addEventListener('DOMContentLoaded', () => this.bootstrap());
    }

    async bootstrap() {
        this.cacheDom();
        this.bindNavigation();
        this.bindTopicFilters();
        await this.loadInitialData();
        this.handleRoute();

        window.addEventListener('popstate', () => this.handleRoute());
        window.addEventListener('hashchange', () => this.handleRoute());
    }

    cacheDom() {
        this.sections = {
            dashboard: document.getElementById('dashboard-section'),
            topics: document.getElementById('topics-section'),
            coverage: document.getElementById('coverage-section'),
            planning: document.getElementById('planning-section'),
            questions: document.getElementById('questions-section'),
        };
        this.navLinks = Array.from(document.querySelectorAll('[data-route]'));
    }

    bindNavigation() {
        this.navLinks.forEach((link) => {
            link.addEventListener('click', (event) => {
                event.preventDefault();
                const route = link.getAttribute('data-route');
                if (route === 'questions') {
                    this.navigateToQuestions();
                } else {
                    this.navigateToSection(route || 'dashboard');
                }
            });
        });
    }

    bindTopicFilters() {
        const topicSearch = document.getElementById('topic-search');
        const statusFilter = document.getElementById('status-filter');
        const sectionFilter = document.getElementById('section-filter');

        if (topicSearch) {
            topicSearch.addEventListener('input', this.debounce(() => this.loadTopics(), 300));
        }
        statusFilter?.addEventListener('change', () => this.loadTopics());
        sectionFilter?.addEventListener('change', () => this.loadTopics());
    }

    async loadInitialData() {
        try {
            const [stats, topics, coverage] = await withLoading(
                async () => {
                    const [statsRes, topicsRes, coverageRes] = await Promise.all([
                        fetch(`${API_BASE_URL}/api/stats`),
                        fetch(`${API_BASE_URL}/api/topics`),
                        fetch(`${API_BASE_URL}/api/coverage`),
                    ]);

                    if (!statsRes.ok || !topicsRes.ok || !coverageRes.ok) {
                        throw new Error('Failed to load initial data');
                    }

                    return Promise.all([statsRes.json(), topicsRes.json(), coverageRes.json()]);
                },
                { label: 'Loading dashboard data...' }
            );

            this.data.stats = stats;
            this.data.topics = topics;
            this.data.coverage = coverage;
            this.renderDashboard();
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to load initial data';
            showToast(message, { type: 'error' });
        }
    }

    handleRoute() {
        const path = window.location.pathname;
        if (path.startsWith('/questions')) {
            const [, , questionId] = path.split('/');
            this.showSection('questions');
            if (questionId) {
                this.questionsController
                    .showDetail(questionId)
                    .catch((error) => {
                        const message = error instanceof Error ? error.message : 'Question unavailable';
                        showToast(message, { type: 'error' });
                        this.navigateToQuestions();
                    });
            } else {
                this.questionsController.showList();
            }
            this.updateNav('questions');
            return;
        }

        const hashSection = window.location.hash.replace('#', '') || 'dashboard';
        this.showSection(hashSection);
        this.updateNav(hashSection);
    }

    navigateToSection(section) {
        if (section === 'questions') {
            this.navigateToQuestions();
            return;
        }
        window.history.pushState({}, '', `#${section}`);
        this.handleRoute();
    }

    navigateToQuestions(questionId = '') {
        const suffix = questionId ? `/${questionId}` : '';
        window.history.pushState({}, '', `/questions${suffix}`);
        this.handleRoute();
    }

    showSection(sectionName) {
        Object.entries(this.sections).forEach(([name, element]) => {
            if (!element) return;
            if (name === sectionName) {
                element.classList.add('active');
            } else {
                element.classList.remove('active');
            }
        });

        this.activeSection = sectionName;

        switch (sectionName) {
            case 'topics':
                this.loadTopics();
                break;
            case 'coverage':
                this.loadCoverage();
                break;
            case 'planning':
                this.loadPlanning();
                break;
            default:
                break;
        }
    }

    updateNav(activeRoute) {
        this.navLinks.forEach((link) => {
            const route = link.getAttribute('data-route');
            if (route === activeRoute) {
                link.classList.add('active');
            } else if (route !== 'questions' && activeRoute !== 'questions') {
                // ensure other links lose active state unless questions route
                link.classList.toggle('active', route === activeRoute);
            } else {
                link.classList.remove('active');
            }
        });
        if (activeRoute === 'questions') {
            const questionsLink = this.navLinks.find((link) => link.getAttribute('data-route') === 'questions');
            questionsLink?.classList.add('active');
        }
    }

    handleQuestionsNavigate({ view, questionId }) {
        if (view === 'detail' && questionId) {
            this.navigateToQuestions(questionId);
        } else {
            this.navigateToQuestions();
        }
    }

    handleQuestionStatusChange() {
        // Re-render list view after status updates; no-op for now but hook kept for analytics.
    }

    async loadTopics() {
        try {
            const searchTerm = document.getElementById('topic-search')?.value ?? '';
            const statusFilter = document.getElementById('status-filter')?.value ?? '';
            const sectionFilter = document.getElementById('section-filter')?.value ?? '';

            const params = new URLSearchParams();
            if (sectionFilter) params.append('section', sectionFilter);
            if (statusFilter) params.append('status', statusFilter);
            else if (searchTerm) params.append('section', searchTerm);

            const response = await withLoading(
                async () => {
                    const res = await fetch(`${API_BASE_URL}/api/topics?${params.toString()}`);
                    if (!res.ok) {
                        throw new Error('Failed to load topics');
                    }
                    return res.json();
                },
                { label: 'Refreshing topics...' }
            );

            this.renderTopics(response);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to load topics';
            showToast(message, { type: 'error' });
        }
    }

    renderTopics(topics) {
        const container = document.getElementById('topics-container');
        if (!container) return;

        if (!topics.length) {
            container.innerHTML = '<div class="alert alert-info">No topics found.</div>';
            return;
        }

        container.innerHTML = topics
            .map((topic) => `
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
                                <div class="small">Tags</div>
                                <strong>${topic.tags.length}</strong>
                            </div>
                        </div>
                    </div>
                </div>
            `)
            .join('');
    }

    async loadCoverage() {
        try {
            if (!this.data.coverage) {
                this.data.coverage = await withLoading(
                    async () => {
                        const res = await fetch(`${API_BASE_URL}/api/coverage`);
                        if (!res.ok) {
                            throw new Error('Failed to load coverage data');
                        }
                        return res.json();
                    },
                    { label: 'Loading coverage data...' }
                );
            }
            this.renderCoverage();
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to load coverage';
            showToast(message, { type: 'error' });
        }
    }

    renderCoverage() {
        const coverage = this.data.coverage;
        if (!coverage) return;

        const gapsContainer = document.getElementById('gaps-container');
        if (gapsContainer) {
            gapsContainer.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-exclamation-circle text-warning"></i> Missing Python Implementations</h6>
                        ${coverage.gaps.missing_python
                            .slice(0, 10)
                            .map((item) => `<div class="gap-item">${item}</div>`)
                            .join('')}
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-lightbulb text-info"></i> Recommendations</h6>
                        ${coverage.recommendations.map((rec) => `<div class="recommendation-item">${rec}</div>`).join('')}
                    </div>
                </div>
            `;
        }

        const tableBody = document.querySelector('#coverage-table tbody');
        if (tableBody) {
            tableBody.innerHTML = Object.entries(coverage.coverage_by_section)
                .sort((a, b) => a[1].step_number - b[1].step_number)
                .map(([title, info]) => `
                    <tr>
                        <td><span class="badge bg-primary">${info.step_number}</span></td>
                        <td>${title}</td>
                        <td><span class="status-badge status-${info.status}">${info.status}</span></td>
                        <td>${info.problem_count}</td>
                        <td>${info.file_count}</td>
                    </tr>
                `)
                .join('');
        }

        if (window.renderCharts) {
            window.renderCharts();
        }
    }

    async loadPlanning() {
        try {
            const [todayPlan, studyPlan] = await withLoading(
                async () => {
                    const today = await fetch(`${API_BASE_URL}/api/study-plan/today`).then((res) => res.json().catch(() => null));
                    const plan = await fetch(`${API_BASE_URL}/api/study-plan`).then((res) => {
                        if (!res.ok) throw new Error('Failed to load study plan');
                        return res.json();
                    });
                    return [today, plan];
                },
                { label: 'Loading study plan...' }
            );
            this.renderPlanning(todayPlan, studyPlan);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to load planning data';
            showToast(message, { type: 'error' });
        }
    }

    renderPlanning(todayPlan, studyPlan) {
        const todayContainer = document.getElementById('today-plan');
        if (todayContainer && todayPlan) {
            todayContainer.innerHTML = `
                <h4><i class="fas fa-calendar-day"></i> Today's Plan - ${todayPlan.day_name}</h4>
                <p><i class="fas fa-clock"></i> Total time: ${Math.floor(todayPlan.total_time / 60)}h ${todayPlan.total_time % 60}m |
                   <i class="fas fa-tasks"></i> ${todayPlan.task_count} tasks</p>
                <div class="row">
                    ${todayPlan.tasks
                        .map(
                            (task) => `
                                <div class="col-md-6 mb-3">
                                    <div class="card task-card">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <h5 class="card-title">${task.title}</h5>
                                                <span class="badge bg-secondary">${task.difficulty}</span>
                                            </div>
                                            <p class="card-text">
                                                <i class="fas fa-clock"></i> ${task.estimated_time} min
                                                <br>
                                                <i class="fas fa-tags"></i> ${task.section}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            `
                        )
                        .join('')}
                </div>
            `;
        }

        const planContainer = document.getElementById('study-plan-container');
        if (planContainer && studyPlan) {
            planContainer.innerHTML = studyPlan.plans
                .map(
                    (plan) => `
                        <div class="card mb-3">
                            <div class="card-header">
                                <h5 class="mb-0">${plan.day_name} - ${plan.date}</h5>
                            </div>
                            <div class="card-body">
                                <p><i class="fas fa-clock"></i> ${plan.total_time} minutes | <i class="fas fa-tasks"></i> ${plan.task_count} tasks</p>
                                <ul class="list-group list-group-flush">
                                    ${plan.tasks
                                        .map(
                                            (task) => `
                                                <li class="list-group-item">
                                                    <div class="d-flex justify-content-between">
                                                        <strong>${task.title}</strong>
                                                        <span class="badge bg-light text-dark">${task.difficulty}</span>
                                                    </div>
                                                    <div class="text-muted small">
                                                        ${task.estimated_time} min • ${task.type}
                                                    </div>
                                                </li>
                                            `
                                        )
                                        .join('')}
                                </ul>
                            </div>
                        </div>
                    `
                )
                .join('');
        }
    }

    async generateNewPlan() {
        try {
            await withLoading(
                async () => {
                    const res = await fetch(`${API_BASE_URL}/api/rebuild`, { method: 'POST' });
                    if (!res.ok) {
                        throw new Error('Failed to rebuild data');
                    }
                },
                { label: 'Regenerating plan...' }
            );
            await this.loadPlanning();
            showToast('New study plan generated successfully!', { type: 'success' });
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to generate new plan';
            showToast(message, { type: 'error' });
        }
    }

    renderDashboard() {
        this.renderStatsCards();
        if (window.renderCharts) {
            window.renderCharts();
        }
    }

    renderStatsCards() {
        const stats = this.data.stats;
        const coverage = this.data.coverage;
        const container = document.getElementById('stats-cards');
        if (!stats || !container) return;

        container.innerHTML = `
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
    }

    debounce(func, wait) {
        let timeout;
        return (...args) => {
            window.clearTimeout(timeout);
            timeout = window.setTimeout(() => func.apply(this, args), wait);
        };
    }
}

window.App = App;
window.app = new App();

window.generateNewPlan = () => window.app.generateNewPlan();
