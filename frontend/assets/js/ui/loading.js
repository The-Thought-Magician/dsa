import { showToast } from './toast.js';

const ACTIVE_OPERATIONS = new Map();
const OVERLAY_ID = 'global-loading-overlay';
const MESSAGE_SELECTOR = '.loading-overlay__message';
const STATE = {
    idle: 'idle',
    loading: 'loading',
    error: 'error',
};

// Default timeout - can be overridden by window.Config.TIMEOUTS.DEFAULT
const DEFAULT_TIMEOUT_MS = 30000;

let overlayElement = null;
let messageElement = null;

function getTimeout() {
    return (window.Config && window.Config.TIMEOUTS && window.Config.TIMEOUTS.DEFAULT) || DEFAULT_TIMEOUT_MS;
}

function ensureOverlay() {
    if (overlayElement) {
        return overlayElement;
    }

    overlayElement = document.createElement('div');
    overlayElement.id = OVERLAY_ID;
    overlayElement.className = 'loading-overlay';
    overlayElement.setAttribute('aria-hidden', 'true');
    overlayElement.innerHTML = `
        <div class="loading-overlay__content" role="status" aria-live="polite">
            <div class="loading-overlay__spinner" aria-hidden="true"></div>
            <p class="loading-overlay__message">Loading...</p>
        </div>
    `;

    document.body.appendChild(overlayElement);
    messageElement = overlayElement.querySelector(MESSAGE_SELECTOR);
    return overlayElement;
}

function getAppRoot() {
    return document.getElementById('app-root');
}

function setBusyState(isBusy) {
    const root = getAppRoot();
    if (root) {
        if (isBusy) {
            root.setAttribute('aria-busy', 'true');
        } else {
            root.removeAttribute('aria-busy');
        }
    }
}

function updateOverlayVisibility() {
    ensureOverlay();
    if (ACTIVE_OPERATIONS.size > 0) {
        overlayElement.dataset.state = STATE.loading;
        overlayElement.classList.add('is-visible');
        overlayElement.setAttribute('aria-hidden', 'false');
    } else {
        overlayElement.classList.remove('is-visible');
        overlayElement.setAttribute('aria-hidden', 'true');
        overlayElement.dataset.state = STATE.idle;
    }
}

function setOverlayMessage(message) {
    ensureOverlay();
    if (messageElement) {
        messageElement.textContent = message;
    }
}

function handleTimeout(token, { timeoutMs }) {
    if (!ACTIVE_OPERATIONS.has(token)) {
        return;
    }

    ACTIVE_OPERATIONS.delete(token);
    overlayElement.dataset.state = STATE.error;
    setOverlayMessage('Still working... retry in a moment.');
    showToast(`Request timed out after ${Math.round(timeoutMs / 1000)}s`, { type: 'error' });
    setBusyState(false);

    setTimeout(() => {
        updateOverlayVisibility();
    }, 600);
}

export function beginLoading(label = 'Loading...', { timeoutMs } = {}) {
    ensureOverlay();
    const token = Symbol('loading');
    setOverlayMessage(label);
    setBusyState(true);

    const actualTimeout = timeoutMs || getTimeout();
    const timer = window.setTimeout(() => handleTimeout(token, { timeoutMs: actualTimeout }), actualTimeout);
    ACTIVE_OPERATIONS.set(token, { timer, label, timeoutMs: actualTimeout });

    updateOverlayVisibility();
    return token;
}

export function endLoading(token, { errorMessage } = {}) {
    const entry = ACTIVE_OPERATIONS.get(token);
    if (!entry) {
        return;
    }

    window.clearTimeout(entry.timer);
    ACTIVE_OPERATIONS.delete(token);

    if (errorMessage) {
        showToast(errorMessage, { type: 'error' });
    }

    if (ACTIVE_OPERATIONS.size === 0) {
        setBusyState(false);
    }

    updateOverlayVisibility();
}

export async function withLoading(task, { label = 'Loading...', timeoutMs, errorMessage } = {}) {
    const token = beginLoading(label, { timeoutMs });
    try {
        const result = await task();
        endLoading(token);
        return result;
    } catch (error) {
        if (errorMessage !== undefined) {
            const fallback = errorMessage || (error instanceof Error ? error.message : 'Something went wrong');
            endLoading(token, { errorMessage: fallback });
        } else {
            endLoading(token);
        }
        throw error;
    }
}
