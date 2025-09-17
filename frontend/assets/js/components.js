class ComponentHelpers {
    static createStatusBadge(status) {
        const statusIcons = {
            'available': 'fas fa-check-circle',
            'partial': 'fas fa-exclamation-triangle',
            'missing': 'fas fa-times-circle'
        };

        const statusColors = {
            'available': 'success',
            'partial': 'warning',
            'missing': 'danger'
        };

        return `<span class="badge bg-${statusColors[status]} status-badge">
                    <i class="${statusIcons[status]}"></i> ${status}
                </span>`;
    }

    static createProgressBar(percentage, label = '') {
        const colorClass = percentage >= 80 ? 'success' : percentage >= 50 ? 'warning' : 'danger';

        return `
            <div class="mb-2">
                ${label && `<small class="text-muted">${label}</small>`}
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-${colorClass}" role="progressbar"
                         style="width: ${percentage}%"
                         aria-valuenow="${percentage}"
                         aria-valuemin="0"
                         aria-valuemax="100">
                        ${percentage.toFixed(1)}%
                    </div>
                </div>
            </div>
        `;
    }

    static createTaskTypeIcon(type) {
        const typeIcons = {
            'new_topic': 'fas fa-plus-circle text-primary',
            'review': 'fas fa-redo text-warning',
            'practice': 'fas fa-dumbbell text-success'
        };

        return `<i class="${typeIcons[type] || 'fas fa-circle'}"></i>`;
    }

    static createPriorityIndicator(priority) {
        const priorityConfig = {
            'high': { color: 'danger', icon: 'fas fa-exclamation' },
            'medium': { color: 'warning', icon: 'fas fa-minus' },
            'low': { color: 'info', icon: 'fas fa-arrow-down' }
        };

        const config = priorityConfig[priority] || priorityConfig['medium'];

        return `<span class="badge bg-${config.color}">
                    <i class="${config.icon}"></i> ${priority}
                </span>`;
    }

    static createTimeDisplay(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;

        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    }

    static createFilesList(files, maxDisplay = 3) {
        if (!files || files.length === 0) {
            return '<span class="text-muted">No files</span>';
        }

        const displayFiles = files.slice(0, maxDisplay);
        const remainingCount = files.length - maxDisplay;

        const fileItems = displayFiles.map(file => {
            const filename = file.split('/').pop();
            return `<span class="badge bg-light text-dark me-1" title="${file}">
                        <i class="fas fa-file-code"></i> ${filename}
                    </span>`;
        }).join('');

        const remaining = remainingCount > 0 ?
            `<span class="text-muted">+${remainingCount} more</span>` : '';

        return fileItems + remaining;
    }

    static createTagsList(tags, maxDisplay = 5) {
        if (!tags || tags.length === 0) {
            return '<span class="text-muted">No tags</span>';
        }

        const displayTags = tags.slice(0, maxDisplay);
        const remainingCount = tags.length - maxDisplay;

        const tagItems = displayTags.map(tag =>
            `<span class="badge bg-secondary me-1">${tag}</span>`
        ).join('');

        const remaining = remainingCount > 0 ?
            `<span class="text-muted">+${remainingCount} more</span>` : '';

        return tagItems + remaining;
    }

    static createLoadingSpinner(size = 'md') {
        const sizeClass = {
            'sm': 'spinner-border-sm',
            'md': '',
            'lg': ''
        };

        return `
            <div class="d-flex justify-content-center p-4">
                <div class="spinner-border text-primary ${sizeClass[size]}" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }

    static createEmptyState(title, message, iconClass = 'fas fa-info-circle') {
        return `
            <div class="text-center p-5">
                <i class="${iconClass} fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">${title}</h5>
                <p class="text-muted">${message}</p>
            </div>
        `;
    }

    static createErrorAlert(message, dismissible = true) {
        return `
            <div class="alert alert-danger ${dismissible ? 'alert-dismissible' : ''}" role="alert">
                <i class="fas fa-exclamation-triangle"></i> ${message}
                ${dismissible ? `
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                ` : ''}
            </div>
        `;
    }

    static createSuccessAlert(message, dismissible = true) {
        return `
            <div class="alert alert-success ${dismissible ? 'alert-dismissible' : ''}" role="alert">
                <i class="fas fa-check-circle"></i> ${message}
                ${dismissible ? `
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                ` : ''}
            </div>
        `;
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };

        return date.toLocaleDateString('en-US', options);
    }

    static highlightSearchTerm(text, searchTerm) {
        if (!searchTerm || searchTerm.trim() === '') {
            return text;
        }

        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<mark class="search-highlight">$1</mark>');
    }

    static createTooltip(element, content, placement = 'top') {
        return new bootstrap.Tooltip(element, {
            title: content,
            placement: placement,
            trigger: 'hover'
        });
    }

    static debounce(func, wait) {
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

    static copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                console.log('Copied to clipboard');
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        } else {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            textArea.remove();
        }
    }

    static animateValue(element, start, end, duration = 1000) {
        const startTimestamp = performance.now();
        const step = (timestamp) => {
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = value;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
}

const Components = ComponentHelpers;

window.Components = Components;