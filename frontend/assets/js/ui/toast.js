const CONTAINER_ID = 'app-toast-container';

const typeToIcon = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle',
};

function ensureContainer() {
    let container = document.getElementById(CONTAINER_ID);
    if (!container) {
        container = document.createElement('div');
        container.id = CONTAINER_ID;
        container.className = 'toast-container';
        container.setAttribute('role', 'status');
        container.setAttribute('aria-live', 'polite');
        document.body.appendChild(container);
    }
    return container;
}

export function showToast(message, { type = 'info', duration = 4000 } = {}) {
    const container = ensureContainer();
    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon"><i class="${typeToIcon[type] || typeToIcon.info}"></i></span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add('is-visible');
    });

    const hideDelay = Math.max(1500, duration - 400);

    setTimeout(() => {
        toast.classList.remove('is-visible');
        toast.classList.add('is-leaving');
    }, hideDelay);

    setTimeout(() => {
        toast.remove();
    }, duration + 200);
}
