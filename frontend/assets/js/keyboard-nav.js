/**
 * Keyboard Navigation Utilities
 * Provides keyboard accessibility enhancements for the application
 */

// ARIA attributes setup
function setupAriaAttributes() {
    // Set up main region
    const main = document.querySelector('main') || document.getElementById('app-root');
    if (main) {
        main.setAttribute('role', 'main');
        main.setAttribute('aria-live', 'polite');
    }
}

// Question card keyboard navigation
function setupQuestionCardKeyboardNav() {
    const questionCards = document.querySelectorAll('.question-card');

    questionCards.forEach(card => {
        // Make card focusable
        if (!card.hasAttribute('tabindex')) {
            card.setAttribute('tabindex', '0');
        }
        card.setAttribute('role', 'button');

        // Handle keyboard activation
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });
}

// Filter dropdown keyboard navigation
function setupFilterKeyboardNav() {
    const filters = document.querySelectorAll('.filters-container select, .filters-container input');

    filters.forEach(filter => {
        filter.setAttribute('aria-label', filter.previousElementSibling?.textContent || 'Filter');
    });
}

// Code editor keyboard shortcuts
function setupCodeEditorShortcuts() {
    const codeEditor = document.getElementById('code-editor');
    if (!codeEditor) return;

    const runButton = document.getElementById('run-code-btn');
    const submitButton = document.getElementById('submit-code-btn');

    codeEditor.addEventListener('keydown', (e) => {
        // Ctrl+Enter or Cmd+Enter to run code
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (runButton && !runButton.disabled) {
                runButton.click();
            }
        }

        // Ctrl+Shift+Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'Enter') {
            e.preventDefault();
            if (submitButton && !submitButton.disabled) {
                submitButton.click();
            }
        }

        // Escape to close modals/panels
        if (e.key === 'Escape') {
            const activePanel = document.querySelector('.panel.active');
            if (activePanel) {
                activePanel.classList.remove('active');
            }
        }
    });
}

// Focus trap for modals
function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                if (document.activeElement === firstFocusable) {
                    e.preventDefault();
                    lastFocusable.focus();
                }
            } else {
                if (document.activeElement === lastFocusable) {
                    e.preventDefault();
                    firstFocusable.focus();
                }
            }
        }
    });
}

// Skip to main content link
function setupSkipLink() {
    // Check if skip link already exists
    if (document.getElementById('skip-to-main')) return;

    const skipLink = document.createElement('a');
    skipLink.id = 'skip-to-main';
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'sr-only';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 0;
        background: #000;
        color: #fff;
        padding: 8px;
        text-decoration: none;
        z-index: 10000;
    `;

    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
    });

    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });

    document.body.prepend(skipLink);
}

// Screen reader announcements
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.style.cssText = `
        position: absolute;
        left: -10000px;
        width: 1px;
        height: 1px;
        overflow: hidden;
    `;
    announcement.textContent = message;

    document.body.appendChild(announcement);

    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

// Initialize all keyboard navigation features
function initKeyboardNavigation() {
    setupAriaAttributes();
    setupQuestionCardKeyboardNav();
    setupFilterKeyboardNav();
    setupCodeEditorShortcuts();
    setupSkipLink();

    // Announce page load to screen readers
    announceToScreenReader('Page loaded');
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initKeyboardNavigation);
} else {
    initKeyboardNavigation();
}

// Re-initialize when DOM changes (for dynamic content)
const observer = new MutationObserver(() => {
    setupQuestionCardKeyboardNav();
    setupFilterKeyboardNav();
});

// Start observing when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, { childList: true, subtree: true });
    });
} else {
    observer.observe(document.body, { childList: true, subtree: true });
}

// Initialize all keyboard navigation features
function initKeyboardNavigation() {
    setupAriaAttributes();
    setupQuestionCardKeyboardNav();
    setupFilterKeyboardNav();
    setupCodeEditorShortcuts();
    setupSkipLink();

    // Announce page load to screen readers
    announceToScreenReader('Page loaded');
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initKeyboardNavigation);
} else {
    initKeyboardNavigation();
}

// Re-initialize when DOM changes (for dynamic content)
const observer = new MutationObserver(() => {
    setupQuestionCardKeyboardNav();
    setupFilterKeyboardNav();
});

// Start observing when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, { childList: true, subtree: true });
    });
} else {
    observer.observe(document.body, { childList: true, subtree: true });
}

// Make functions available globally
window.KeyboardNav = {
    setupAriaAttributes,
    setupQuestionCardKeyboardNav,
    setupCodeEditorShortcuts,
    trapFocus,
    announceToScreenReader,
    initKeyboardNavigation,
};

