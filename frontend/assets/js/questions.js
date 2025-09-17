import { API_BASE_URL } from './config.js';
import { withLoading, beginLoading, endLoading } from './ui/loading.js';
import { showToast } from './ui/toast.js';
import { AIChatPanel } from './ai_chat.js';

const STATUS_ICON = {
    unsolved: 'far fa-circle',
    attempted: 'fas fa-hourglass-half',
    solved: 'fas fa-check-circle',
};

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value;
    return div.innerHTML;
}

function renderMarkdown(markdown) {
    if (!markdown) {
        return '';
    }

    const codeBlocks = [];
    const fenced = markdown.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang = '', code) => {
        const index = codeBlocks.length;
        codeBlocks.push({ lang, code });
        return `@@CODE${index}@@`;
    });

    let html = escapeHtml(fenced);

    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/^(?:- |\* )(.*)$/gm, '<li>$1</li>');

    html = html
        .split(/\n{2,}/)
        .map((paragraph) => {
            if (paragraph.startsWith('<li>')) {
                return `<ul>${paragraph}</ul>`;
            }
            return `<p>${paragraph}</p>`;
        })
        .join('');

    html = html.replace(/@@CODE(\d+)@@/g, (_, index) => {
        const block = codeBlocks[Number(index)];
        const escaped = escapeHtml(block.code.trim());
        const langAttr = block.lang ? ` data-lang="${escapeHtml(block.lang)}"` : '';
        return `<pre><code${langAttr}>${escaped}</code></pre>`;
    });

    return html;
}

export class QuestionsController {
    constructor({ onNavigate, onStatusChange } = {}) {
        this.apiBaseUrl = API_BASE_URL;
        this.onNavigate = onNavigate || (() => {});
        this.onStatusChange = onStatusChange || (() => {});
        this.questions = [];
        this.questionDetails = new Map();
        this.ready = false;
        this.filters = {
            search: '',
            status: '',
            difficulty: '',
        };
        this.activeQuestionId = null;
        this.aiChatPanel = new AIChatPanel({
            contextProvider: () => ({
                questionId: this.activeQuestionId,
                code: this.elements?.editor?.value || '',
                language: 'python',
            }),
        });
    }

    async init() {
        if (this.ready) {
            return;
        }
        await this.loadComponents();
        this.cacheElements();
        this.bindEvents();
        this.aiChatPanel.mount({
            messagesEl: this.elements.chatMessages,
            inputEl: this.elements.chatInput,
            sendButton: this.elements.chatSend,
        });
        await this.fetchQuestions();
        this.renderList();
        this.ready = true;
    }

    async loadComponents() {
        const container = document.getElementById('questions-section');
        if (!container) {
            throw new Error('Questions container missing');
        }

        const [listHtml, detailHtml] = await Promise.all([
            fetch('components/questions-list.html').then((res) => res.text()),
            fetch('components/question-detail.html').then((res) => res.text()),
        ]);

        container.innerHTML = `${listHtml}\n${detailHtml}`;
        this.container = container;
    }

    cacheElements() {
        this.elements = {
            listView: document.getElementById('questions-list-view'),
            detailView: document.getElementById('question-detail-view'),
            listContainer: document.getElementById('questions-list-container'),
            searchInput: document.getElementById('questions-search'),
            statusFilter: document.getElementById('questions-status-filter'),
            difficultyFilter: document.getElementById('questions-difficulty-filter'),
            backButton: document.getElementById('question-back-button'),
            title: document.getElementById('question-detail-heading'),
            meta: document.getElementById('question-meta'),
            statement: document.getElementById('question-statement'),
            approachSection: document.querySelector('.question-approach'),
            approach: document.getElementById('question-approach'),
            theorySection: document.querySelector('.question-theory'),
            theory: document.getElementById('question-theory'),
            conceptsSection: document.querySelector('.question-concepts'),
            concepts: document.getElementById('question-concepts'),
            resourcesList: document.getElementById('question-resources-list'),
            samplesContainer: document.getElementById('question-samples-container'),
            viewSolutionButton: document.getElementById('question-view-solution-btn'),
            solutionBody: document.getElementById('question-solution-body'),
            solutionStatus: document.getElementById('question-solution-status'),
            editor: document.getElementById('question-editor'),
            runButton: document.getElementById('question-run-btn'),
            submitButton: document.getElementById('question-submit-btn'),
            resultsContainer: document.getElementById('question-results'),
            chatMessages: document.getElementById('chat-messages'),
            chatInput: document.getElementById('chat-input'),
            chatSend: document.getElementById('chat-send-btn'),
        };
    }

    bindEvents() {
        this.elements.searchInput?.addEventListener('input', (event) => {
            this.filters.search = event.target.value.trim().toLowerCase();
            this.renderList();
        });

        this.elements.statusFilter?.addEventListener('change', (event) => {
            this.filters.status = event.target.value;
            this.renderList();
        });

        this.elements.difficultyFilter?.addEventListener('change', (event) => {
            this.filters.difficulty = event.target.value;
            this.renderList();
        });

        this.elements.backButton?.addEventListener('click', () => {
            this.onNavigate({ view: 'list' });
        });

        this.elements.runButton?.addEventListener('click', () => this.handleRun(false));
        this.elements.submitButton?.addEventListener('click', () => this.handleRun(true));
        this.elements.viewSolutionButton?.addEventListener('click', () => this.handleViewSolution());
    }

    async fetchQuestions(force = false) {
        if (this.questions.length > 0 && !force) {
            return;
        }
        const data = await withLoading(
            async () => {
                const response = await fetch(`${this.apiBaseUrl}/api/questions`);
                if (!response.ok) {
                    throw new Error('Unable to load questions');
                }
                return response.json();
            },
            { label: 'Loading questions...' }
        );

        this.questions = data;
        this.questions.forEach((item) => {
            this.questionDetails.set(item.id, { ...this.questionDetails.get(item.id), ...item });
        });
    }

    filterQuestions() {
        return this.questions.filter((question) => {
            const matchesSearch =
                !this.filters.search ||
                question.title.toLowerCase().includes(this.filters.search) ||
                question.tags.some((tag) => tag.toLowerCase().includes(this.filters.search));

            const matchesStatus = !this.filters.status || question.status === this.filters.status;
            const matchesDifficulty = !this.filters.difficulty || question.difficulty === this.filters.difficulty;

            return matchesSearch && matchesStatus && matchesDifficulty;
        });
    }

    renderList() {
        if (!this.elements.listContainer) {
            return;
        }

        const filtered = this.filterQuestions();
        if (filtered.length === 0) {
            this.elements.listContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        No questions match the current filters.
                    </div>
                </div>
            `;
            return;
        }

        const cards = filtered
            .map((question) => {
                const tags = question.tags
                    .slice(0, 4)
                    .map((tag) => `<span class="badge bg-light text-dark">${escapeHtml(tag)}</span>`)
                    .join(' ');
                const statusIcon = STATUS_ICON[question.status] || STATUS_ICON.unsolved;
                const statusLabel = question.status;
                const viewedBadge = question.solution_viewed
                    ? '<span class="badge bg-success-subtle text-success-emphasis">Solution viewed</span>'
                    : '';

                return `
                    <div class="col-12 col-md-6 col-xl-4">
                        <article class="questions-card h-100" data-question-id="${question.id}" tabindex="0">
                            <div class="p-3 d-flex flex-column gap-2 h-100">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h3 class="h5 mb-0">${escapeHtml(question.title)}</h3>
                                    <span class="question-status" data-status="${statusLabel}">
                                        <i class="${statusIcon}"></i> ${statusLabel}
                                    </span>
                                </div>
                                <div class="text-muted small">${escapeHtml(question.difficulty)}</div>
                                <div class="d-flex gap-2 flex-wrap">${tags}</div>
                                ${viewedBadge}
                            </div>
                        </article>
                    </div>
                `;
            })
            .join('');

        this.elements.listContainer.innerHTML = cards;
        this.elements.listContainer.querySelectorAll('[data-question-id]').forEach((card) => {
            card.addEventListener('click', () => {
                const id = card.getAttribute('data-question-id');
                this.onNavigate({ view: 'detail', questionId: id });
            });
            card.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    card.click();
                }
            });
        });
    }

    async ensureDetail(questionId) {
        if (this.questionDetails.has(questionId) && this.questionDetails.get(questionId)?.statement_markdown) {
            return this.questionDetails.get(questionId);
        }

        const token = beginLoading('Loading question...');
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/questions/${questionId}`);
            if (!response.ok) {
                throw new Error('Question not found');
            }
            const detail = await response.json();
            this.questionDetails.set(questionId, detail);
            return detail;
        } finally {
            endLoading(token);
        }
    }

    async showList() {
        await this.init();
        this.activeQuestionId = null;
        this.elements.detailView?.classList.add('visually-hidden');
        this.elements.listView?.classList.remove('visually-hidden');
        this.container?.classList.add('section-active-list');
    }

    async showDetail(questionId) {
        await this.init();
        this.activeQuestionId = questionId;
        const detail = await this.ensureDetail(questionId);
        this.renderDetail(detail);
        this.elements.listView?.classList.add('visually-hidden');
        this.elements.detailView?.classList.remove('visually-hidden');
        this.aiChatPanel.setQuestion(questionId, {
            title: detail.title,
            solutionViewed: detail.solution_viewed,
        });
    }

    renderDetail(detail) {
        const metaHtml = [
            `<span class="badge bg-primary-subtle text-primary-emphasis">${escapeHtml(detail.difficulty)}</span>`,
            `<span class="badge bg-light text-dark">${detail.tags.length} tags</span>`,
            `<span class="badge bg-light text-dark">Status: ${escapeHtml(detail.status)}</span>`,
        ];

        this.elements.title.textContent = detail.title;
        this.elements.meta.innerHTML = metaHtml.join(' ');
        this.elements.statement.innerHTML = renderMarkdown(detail.statement_markdown);
        if (detail.approach_markdown) {
            this.elements.approach.innerHTML = renderMarkdown(detail.approach_markdown);
            this.elements.approachSection.classList.remove('visually-hidden');
        } else {
            this.elements.approachSection.classList.add('visually-hidden');
            this.elements.approach.innerHTML = '';
        }
        if (detail.theory_markdown) {
            this.elements.theory.innerHTML = renderMarkdown(detail.theory_markdown);
            this.elements.theorySection.classList.remove('visually-hidden');
        } else {
            this.elements.theorySection.classList.add('visually-hidden');
            this.elements.theory.innerHTML = '';
        }
        if (Array.isArray(detail.concepts) && detail.concepts.length) {
            this.elements.concepts.innerHTML = detail.concepts
                .map((c) => `
                    <div class="col-md-4">
                        <div class="border rounded-3 p-3 h-100">
                            <h4 class="h6 mb-2">${escapeHtml(c.name || '')}</h4>
                            <div class="small text-muted mb-2">${escapeHtml(c.summary || '')}</div>
                            ${c.why_it_matters ? `<div class="small"><strong>Why:</strong> ${escapeHtml(c.why_it_matters)}</div>` : ''}
                            ${c.practice_tips ? `<div class="small mt-1"><strong>Practice:</strong> ${escapeHtml(c.practice_tips)}</div>` : ''}
                        </div>
                    </div>
                `)
                .join('');
            this.elements.conceptsSection.classList.remove('visually-hidden');
        } else {
            this.elements.concepts.innerHTML = '';
            this.elements.conceptsSection.classList.add('visually-hidden');
        }
        this.elements.editor.value = detail.starter_code || '';

        this.renderResources(detail.resources || []);
        this.renderSamples(detail.sample_tests || []);
        this.updateSolutionState(detail.solution_viewed);
        this.elements.resultsContainer.classList.add('visually-hidden');
        this.elements.resultsContainer.innerHTML = '';
    }

    renderResources(resources) {
        this.elements.resourcesList.innerHTML = resources
            .map((resource) => {
                const title = escapeHtml(resource.title);
                const url = escapeHtml(resource.url);
                const notes = resource.notes ? `<small class="d-block text-muted">${escapeHtml(resource.notes)}</small>` : '';
                return `<li><a href="${url}" target="_blank" rel="noopener">${title}</a>${notes}</li>`;
            })
            .join('');
    }

    renderSamples(samples) {
        if (!samples.length) {
            this.elements.samplesContainer.innerHTML = '<p class="text-muted">No sample tests available.</p>';
            return;
        }

        this.elements.samplesContainer.innerHTML = samples
            .map((sample) => {
                const input = escapeHtml(sample.input.trim());
                const output = escapeHtml(sample.output.trim());
                const explanation = sample.explanation ? `<p class="small mb-0">${escapeHtml(sample.explanation)}</p>` : '';
                return `
                    <div class="border rounded-3 p-3">
                        <h4 class="h6">Sample ${sample.id}</h4>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <span class="d-block text-muted small fw-semibold">Input</span>
                                <pre class="mb-0"><code>${input}</code></pre>
                            </div>
                            <div class="col-md-6">
                                <span class="d-block text-muted small fw-semibold">Output</span>
                                <pre class="mb-0"><code>${output}</code></pre>
                            </div>
                        </div>
                        ${explanation}
                    </div>
                `;
            })
            .join('');
    }

    updateSolutionState(viewed) {
        if (viewed) {
            this.elements.solutionStatus.textContent = 'Viewed';
            this.elements.solutionStatus.className = 'badge bg-success';
            this.elements.solutionBody.classList.remove('visually-hidden');
            this.elements.viewSolutionButton.classList.add('btn-outline-secondary');
            this.elements.viewSolutionButton.disabled = true;
        } else {
            this.elements.solutionStatus.textContent = 'Hidden';
            this.elements.solutionStatus.className = 'badge bg-secondary';
            this.elements.solutionBody.classList.add('visually-hidden');
            this.elements.solutionBody.innerHTML = '';
            this.elements.viewSolutionButton.classList.remove('btn-outline-secondary');
            this.elements.viewSolutionButton.disabled = false;
        }
    }

    async handleRun(finalize) {
        if (!this.activeQuestionId) {
            showToast('Open a question to run code.', { type: 'info' });
            return;
        }
        const code = this.elements.editor.value;
        if (!code.trim()) {
            showToast('Write some code before running.', { type: 'info' });
            return;
        }

        const endpoint = finalize ? 'submit' : 'run';

        try {
            const response = await withLoading(
                async () => {
                    const res = await fetch(`${this.apiBaseUrl}/api/questions/${this.activeQuestionId}/${endpoint}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code, language: 'python' }),
                    });
                    if (!res.ok) {
                        const detail = await res.json().catch(() => ({}));
                        const message = detail.detail || 'Execution failed';
                        throw new Error(message);
                    }
                    return res.json();
                },
                { label: finalize ? 'Submitting solution...' : 'Running code...' }
            );

            this.renderResults(response);
            this.updateQuestionStatus(this.activeQuestionId, {
                status: response.updated_status,
                solution_viewed: this.questionDetails.get(this.activeQuestionId)?.solution_viewed || false,
            });

            if (finalize) {
                const toastType = response.verdict === 'passed' ? 'success' : 'info';
                const message = response.verdict === 'passed' ? 'All sample tests passed! Marked as solved.' : 'Submission recorded. Check failing cases above.';
                showToast(message, { type: toastType });
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Execution failed';
            showToast(message, { type: 'error' });
        }
    }

    renderResults(result) {
        const container = this.elements.resultsContainer;
        if (!container) {
            return;
        }
        container.classList.remove('visually-hidden');

        const items = result.results
            .map((test) => {
                const statusClass = test.passed ? 'text-success' : 'text-danger';
                const summary = test.passed ? '<i class="fas fa-check-circle me-1"></i> Passed' : '<i class="fas fa-times-circle me-1"></i> Failed';
                const detail = test.passed
                    ? ''
                    : `<div class="small text-muted mt-2">
                            <div><strong>Expected:</strong> ${escapeHtml(test.expected_output)}</div>
                            <div><strong>Actual:</strong> ${escapeHtml(test.actual_output)}</div>
                            ${test.stderr ? `<div><strong>stderr:</strong> ${escapeHtml(test.stderr)}</div>` : ''}
                       </div>`;
                return `
                    <div class="result-item">
                        <span>Test ${test.index}</span>
                        <span class="${statusClass}">${summary}</span>
                    </div>
                    ${detail}
                `;
            })
            .join('');

        container.innerHTML = `
            <div class="p-3 border-bottom">
                <strong>${escapeHtml(result.summary)}</strong>
                <span class="badge ${result.verdict === 'passed' ? 'bg-success' : 'bg-warning text-dark'} ms-2">${result.verdict}</span>
            </div>
            <div class="p-2">${items}</div>
        `;
    }

    async handleViewSolution() {
        if (!this.activeQuestionId) {
            return;
        }

        try {
            const data = await withLoading(
                async () => {
                    const res = await fetch(`${this.apiBaseUrl}/api/questions/${this.activeQuestionId}/solution/view`, {
                        method: 'POST',
                    });
                    if (!res.ok) {
                        const detail = await res.json().catch(() => ({}));
                        throw new Error(detail.detail || 'Solution not available');
                    }
                    return res.json();
                },
                { label: 'Revealing solution...' }
            );

            this.elements.solutionBody.innerHTML = renderMarkdown(data.solution_markdown);
            this.updateSolutionState(true);

            const cached = this.questionDetails.get(this.activeQuestionId) || {};
            cached.solution_viewed = true;
            this.questionDetails.set(this.activeQuestionId, cached);
            this.updateQuestionStatus(this.activeQuestionId, {
                status: cached.status || 'attempted',
                solution_viewed: true,
            });

            showToast('Solution unlocked. Remember to reflect on the approach!', { type: 'info' });
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Unable to fetch solution';
            showToast(message, { type: 'error' });
        }
    }

    updateQuestionStatus(questionId, { status, solution_viewed }) {
        this.questions = this.questions.map((item) =>
            item.id === questionId ? { ...item, status, solution_viewed } : item
        );
        this.questionDetails.set(questionId, {
            ...(this.questionDetails.get(questionId) || {}),
            status,
            solution_viewed,
        });
        this.renderList();
        this.onStatusChange({ questionId, status, solution_viewed });
    }
}
