# Frontend & UX Plan

## Overview

This plan addresses frontend user experience issues including mobile responsiveness, loading states, error handling, accessibility, and visual consistency.

## Current Status Assessment

### What Works
- Bootstrap 5 responsive grid
- Basic SPA navigation
- Chart.js integration for progress visualization
- AI chat interface
- Question browser with filtering

### Known Issues

| Area | Issue | Priority |
|------|-------|----------|
| Mobile | Layout not tested on small screens | High |
| Loading | Overlay timeout behavior undefined | High |
| Errors | Generic toast messages | Medium |
| Accessibility | Keyboard navigation incomplete | Medium |
| Charts | Global `App` reference issues | Medium |
| Favicon | 404 errors on `/favicon.ico` | Low |
| Config | Hardcoded API URLs | Medium |

## Phase 1: Mobile Responsiveness

### 1.1 Breakpoint Testing

**Devices to Test**:
- Mobile: 375px (iPhone SE), 390px (iPhone 13), 428px (iPhone Pro Max)
- Tablet: 768px (iPad), 1024px (iPad Pro)
- Desktop: 1366px, 1920px, 2560px

**Pages to Test**:
- Dashboard (stats, charts)
- Topics list
- Questions list/detail
- AI Chat panel
- Planning view

### 1.2 Responsive Components

**File**: `frontend/assets/css/responsive.css`

```css
/* Mobile-first adjustments */

/* Questions list - card layout */
@media (max-width: 768px) {
    .question-card {
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    }

    .question-card .difficulty-badge {
        font-size: 0.7rem;
        padding: 0.2rem 0.4rem;
    }

    /* Stack filters vertically */
    .filters-container {
        flex-direction: column;
        gap: 0.5rem;
    }

    .filters-container select,
    .filters-container input {
        width: 100%;
    }
}

/* Code editor on mobile */
@media (max-width: 768px) {
    .code-editor-container {
        flex-direction: column;
    }

    .code-editor,
    .output-panel {
        min-height: 200px;
        font-size: 14px;
    }
}

/* Chat panel */
@media (max-width: 768px) {
    .ai-chat-panel {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 60vh;
        border-radius: 1rem 1rem 0 0;
        transform: translateY(100%);
        transition: transform 0.3s ease;
    }

    .ai-chat-panel.open {
        transform: translateY(0);
    }
}

/* Dashboard charts */
@media (max-width: 768px) {
    .chart-container {
        height: 200px;
    }

    .stats-card {
        margin-bottom: 1rem;
    }
}
```

### 1.3 Touch Targets

Ensure all interactive elements meet minimum touch target size (44x44px):

```css
.btn, .question-card, .nav-link {
    min-height: 44px;
    min-width: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
```

## Phase 2: Loading & Feedback

### 2.1 Loading Overlay Enhancement

**File**: `frontend/assets/js/ui/loading.js`

```javascript
// Current overlay issues:
// - No timeout behavior defined
// - Shows within 100ms requirement (good)
// - Missing retry CTA

const LoadingOverlay = {
    overlay: null,
    timeoutId: null,
    TIMEOUT_MS: 30000, // 30 second timeout

    show(message = "Loading...", options = {}) {
        if (!this.overlay) {
            this.overlay = this.create();
        }
        this.overlay.classList.remove('hidden');
        this.overlay.querySelector('.message').textContent = message;

        // Auto-hide after timeout
        if (this.timeoutId) clearTimeout(this.timeoutId);
        this.timeoutId = setTimeout(() => {
            this.showTimeout(options.onRetry);
        }, this.TIMEOUT_MS);

        // Show within 100ms requirement already met
    },

    hide() {
        if (this.timeoutId) clearTimeout(this.timeoutId);
        this.overlay?.classList.add('hidden');
    },

    showTimeout(onRetry) {
        const overlay = this.overlay;
        overlay.querySelector('.message').textContent = "Taking longer than expected...";
        const retryBtn = overlay.querySelector('.retry-btn');
        retryBtn.classList.remove('hidden');
        retryBtn.onclick = () => {
            overlay.classList.add('hidden');
            if (onRetry) onRetry();
        };
    },

    create() {
        const div = document.createElement('div');
        div.className = 'loading-overlay hidden';
        div.innerHTML = `
            <div class="spinner"></div>
            <p class="message">Loading...</p>
            <button class="retry-btn hidden">Retry</button>
        `;
        document.body.appendChild(div);
        return div;
    }
};

// Keyboard support: Esc to close
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        LoadingOverlay.hide();
    }
});
```

### 2.2 Toast Notifications

**File**: `frontend/assets/js/ui/toast.js`

```javascript
const Toast = {
    container: null,

    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    },

    show(message, type = 'info', duration = 5000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-message">${message}</span>
            <button class="toast-close">&times;</button>
        `;

        this.container.appendChild(toast);

        // Auto-dismiss
        const timeout = setTimeout(() => this.dismiss(toast), duration);

        // Manual dismiss
        toast.querySelector('.toast-close').onclick = () => {
            clearTimeout(timeout);
            this.dismiss(toast);
        };

        return toast;
    },

    dismiss(toast) {
        toast.classList.add('toast-dismissing');
        setTimeout(() => toast.remove(), 300);
    },

    // Convenience methods
    success(message, duration) { return this.show(message, 'success', duration); },
    error(message, duration) { return this.show(message, 'error', duration); },
    warning(message, duration) { return this.show(message, 'warning', duration); },
    info(message, duration) { return this.show(message, 'info', duration); }
};
```

### 2.3 Error Toast Messages

**File**: `frontend/assets/js/app.js`

Map specific API errors to user-friendly messages:

```javascript
const ErrorMessages = {
    // Network errors
    'Failed to fetch': 'Network error. Please check your connection.',
    'NetworkError': 'Network error. Please check your connection.',

    // API errors
    429: 'Too many requests. Please wait a moment.',
    503: 'Service temporarily unavailable. Please try again.',
    504: 'Request timeout. The server took too long to respond.',
    500: 'Server error. Please try again later.',

    // Code execution errors
    'Execution timeout': 'Code execution exceeded time limit.',
    'not allowed': 'That operation is not allowed.',
    'syntax error': 'Your code has a syntax error.',

    // AI chat errors
    'quota': 'AI rate limit exceeded. Please wait.',
    'key': 'AI service configuration error.',

    default: 'Something went wrong. Please try again.'
};

function getErrorMessage(error) {
    const errorStr = String(error);
    for (const [key, message] of Object.entries(ErrorMessages)) {
        if (errorStr.includes(key)) {
            return message;
        }
    }
    return ErrorMessages.default;
}
```

## Phase 3: Accessibility

### 3.1 Keyboard Navigation

**File**: `frontend/assets/js/questions.js`

```javascript
// Question cards keyboard interaction
function setupQuestionKeyboardNav() {
    document.querySelectorAll('.question-card').forEach(card => {
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');

        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });
}
```

### 3.2 ARIA Attributes

**File**: `frontend/components/question-detail.html`

```html
<div id="question-detail" role="main" aria-live="polite">
    <h1 id="question-title">{{title}}</h1>

    <div class="question-meta" aria-label="Question metadata">
        <span class="difficulty-badge" aria-label="Difficulty: {{difficulty}}">
            {{difficulty}}
        </span>
        <span class="tags" aria-label="Topics: {{tags}}">{{tags}}</span>
    </div>

    <button id="run-code-btn" aria-describedby="run-code-hint">
        Run Code
    </button>
    <span id="run-code-hint" class="sr-only">Executes your code and shows output</span>
</div>
```

### 3.3 Focus Management

```javascript
// Preserve focus during page transitions
let focusedElement = null;

function saveFocus() {
    focusedElement = document.activeElement;
}

function restoreFocus() {
    if (focusedElement) {
        focusedElement.focus();
    }
}

// Set focus to main content after navigation
function navigateTo(page) {
    saveFocus();
    // ... navigation logic ...
    setTimeout(() => {
        document.querySelector('[role="main"]')?.focus();
    }, 100);
}
```

### 3.4 Screen Reader Support

```css
/* Screen reader only content */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* But visible when focused */
.sr-only:focus {
    position: static;
    width: auto;
    height: auto;
    padding: inherit;
    margin: inherit;
    overflow: visible;
    clip: auto;
    white-space: normal;
}
```

### 3.5 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

## Phase 4: Chart.js Integration

### 4.1 Remove Global App Reference

**File**: `frontend/assets/js/charts.js`

```javascript
// BEFORE: Uses global App (buggy)
// const totalQuestions = App.state.totalQuestions;

// AFTER: Use window.app
const initCharts = () => {
    const app = window.app;
    if (!app) {
        console.warn('App not initialized');
        return;
    }

    const stats = app.state.stats;
    // ... chart initialization ...
};
```

### 4.2 Ensure Chart.js Loads First

**File**: `frontend/index.html`

```html
<head>
    <!-- Load Chart.js before custom scripts -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <!-- ... -->
    <script src="/assets/js/config.js"></script>
    <script src="/assets/js/charts.js"></script>
    <script src="/assets/js/app.js"></script>
</body>
```

### 4.3 Chart Canvas Elements

**File**: `frontend/assets/js/app.js`

```javascript
function renderCharts(stats) {
    // Verify canvas elements exist
    const coverageCanvas = document.getElementById('coverageChart');
    const progressCanvas = document.getElementById('progressChart');

    if (!coverageCanvas || !progressCanvas) {
        console.warn('Chart canvas elements not found');
        return;
    }

    // Destroy existing charts before re-rendering
    if (window.coverageChart) {
        window.coverageChart.destroy();
    }
    if (window.progressChart) {
        window.progressChart.destroy();
    }

    // Create new charts
    window.coverageChart = new Chart(coverageCanvas, { /* ... */ });
}
```

## Phase 5: Configuration Management

### 5.1 Centralized Config

**File**: `frontend/assets/js/config.js`

```javascript
// BEFORE: Hardcoded URLs scattered across files
// const response = await fetch('http://localhost:8000/api/stats');

// AFTER: Centralized configuration
window.Config = {
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : '',  // Use relative path in production

    ENDPOINTS: {
        STATS: '/api/stats',
        TOPICS: '/api/topics',
        COVERAGE: '/api/coverage',
        QUESTIONS: '/api/questions',
        RUN_CODE: '/api/questions/{id}/run',
        AI_CHAT: '/api/ai/chat'
    },

    get url() {
        return this.API_BASE_URL;
    },

    endpoint(key) {
        return this.API_BASE_URL + this.ENDPOINTS[key];
    }
};

// Usage
const response = await fetch(Config.endpoint('STATS'));
```

## Phase 6: Visual Polish

### 6.1 Fix Favicon

**File**: `frontend/favicon.ico`

- Ensure favicon exists at `frontend/favicon.ico`
- Add fallback in index.html:

```html
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
```

### 6.2 Consistent Color Scheme

```css
:root {
    /* Primary colors */
    --color-primary: #4F46E5;
    --color-primary-dark: #4338CA;
    --color-primary-light: #818CF8;

    /* Semantic colors */
    --color-success: #10B981;
    --color-warning: #F59E0B;
    --color-error: #EF4444;
    --color-info: #3B82F6;

    /* Neutral colors */
    --color-bg: #F9FAFB;
    --color-surface: #FFFFFF;
    --color-text: #111827;
    --color-text-muted: #6B7280;
    --color-border: #E5E7EB;
}

/* Difficulty colors */
.difficulty-easy { color: var(--color-success); }
.difficulty-medium { color: var(--color-warning); }
.difficulty-hard { color: var(--color-error); }
```

### 6.3 Empty States

**File**: `frontend/assets/js/components.js`

```javascript
function renderEmptyState(message, actionText, actionCallback) {
    return `
        <div class="empty-state">
            <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="empty-message">${message}</p>
            ${actionText ? `<button class="btn btn-primary" id="empty-action">${actionText}</button>` : ''}
        </div>
    `;
}
```

## Execution Order

| Step | Task | Priority | Dependencies |
|------|------|----------|--------------|
| 1 | Add favicon to frontend/ | Low | - |
| 2 | Create responsive.css | High | - |
| 3 | Test and fix mobile layouts | High | Step 2 |
| 4 | Enhance loading overlay with timeout | High | - |
| 5 | Improve error toast messages | Medium | - |
| 6 | Add keyboard navigation to question cards | Medium | - |
| 7 | Fix Chart.js global App reference | Medium | - |
| 8 | Create centralized config.js | Medium | - |
| 9 | Add ARIA attributes | Medium | - |
| 10 | Add reduced motion support | Low | - |

## Success Criteria

- [ ] All pages work on mobile (375px - 428px)
- [ ] Loading overlay shows within 100ms
- [ ] Loading overlay times out after 30s with retry option
- [ ] All errors show actionable user-friendly messages
- [ ] Question cards activate with Enter/Space keys
- [ ] Charts render without console errors
- [ ] Favicon loads without 404
- [ ] Config uses relative API URLs
- [ ] Reduced motion preference is respected
- [ ] Focus management works for SPA navigation

## Browser Testing Checklist

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)
