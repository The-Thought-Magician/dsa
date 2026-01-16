/**
 * Centralized configuration for A2Z DSA Learning System
 */

// Detect environment
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

// Base API URL - uses relative path in production, localhost in development
const API_BASE_URL = isProduction ? '' : 'http://localhost:8000';

// API endpoints
const ENDPOINTS = {
    STATS: '/api/stats',
    TOPICS: '/api/topics',
    COVERAGE: '/api/coverage',
    QUESTIONS: '/api/questions',
    QUESTION_DETAIL: '/api/questions/{id}',
    RUN_CODE: '/api/questions/{id}/run',
    SUBMIT_CODE: '/api/questions/{id}/submit',
    VIEW_SOLUTION: '/api/questions/{id}/solution/view',
    AI_CHAT: '/api/ai/ask',
    STUDY_PLAN: '/api/study-plan',
    STUDY_PLAN_TODAY: '/api/study-plan/today',
    REBUILD: '/api/rebuild',
    HEALTH: '/health',
};

// Timeouts (in milliseconds)
const TIMEOUTS = {
    DEFAULT: 30000,
    CODE_EXECUTION: 10000,
    AI_CHAT: 60000,
    DATA_FETCH: 15000,
};

// Rate limit delays (in milliseconds) for retry logic
const RETRY_DELAYS = {
    DEFAULT: 2000,
    RATE_LIMIT: 5000,
};

// UI settings
const UI = {
    QUESTIONS_PER_PAGE: 50,
    CHART_ANIMATION_DURATION: 750,
    TOAST_DURATION: 4000,
    LOADING_MINIMUM_DISPLAY: 500,
    DEBOUNCE_DELAY: 300,
};

// Status values
const STATUS = {
    UNSOLVED: 'unsolved',
    ATTEMPTED: 'attempted',
    SOLVED: 'solved',
};

// Difficulty levels with associated colors
const DIFFICULTY = {
    EASY: { name: 'Easy', color: '#28a745', class: 'difficulty-easy' },
    MEDIUM: { name: 'Medium', color: '#ffc107', class: 'difficulty-medium' },
    HARD: { name: 'Hard', color: '#dc3545', class: 'difficulty-hard' },
};

// Error messages mapping
const ERROR_MESSAGES = {
    NETWORK: 'Network error. Please check your connection.',
    TIMEOUT: 'Request timeout. Please try again.',
    RATE_LIMIT: 'Too many requests. Please wait a moment.',
    NOT_FOUND: 'Resource not found.',
    SERVER_ERROR: 'Server error. Please try again later.',
    AI_UNAVAILABLE: 'AI service temporarily unavailable.',
    CODE_VALIDATION: 'Code contains disallowed operations.',
    DEFAULT: 'Something went wrong. Please try again.',
};

// Helper function to build endpoint URL with parameters
function buildEndpoint(endpointKey, params = {}) {
    let url = ENDPOINTS[endpointKey];
    if (!url) {
        throw new Error(`Unknown endpoint: ${endpointKey}`);
    }

    // Replace path parameters like {id}
    for (const [key, value] of Object.entries(params)) {
        url = url.replace(`{${key}}`, value);
    }

    return API_BASE_URL + url;
}

// Helper function to get full API URL
function getApiUrl(path = '') {
    return API_BASE_URL + path;
}

// Export configuration
window.Config = {
    // Environment
    isProduction,
    apiBaseUrl: API_BASE_URL,

    // Endpoints
    ENDPOINTS,
    buildEndpoint,
    getApiUrl,

    // Timeouts
    TIMEOUTS,

    // Retry delays
    RETRY_DELAYS,

    // UI settings
    UI,

    // Constants
    STATUS,
    DIFFICULTY,
    ERROR_MESSAGES,

    // Utilities
    getDifficultyColor(level) {
        const diff = DIFFICULTY[level.toUpperCase()];
        return diff ? diff.color : '#6c757d';
    },

    getDifficultyClass(level) {
        const diff = DIFFICULTY[level.toUpperCase()];
        return diff ? diff.class : 'difficulty-unknown';
    },

    getStatusLabel(status) {
        const labels = {
            [STATUS.UNSOLVED]: 'Not Started',
            [STATUS.ATTEMPTED]: 'In Progress',
            [STATUS.SOLVED]: 'Completed',
        };
        return labels[status] || status;
    },

    getErrorMessage(error) {
        const errorStr = String(error);
        if (errorStr.includes('Failed to fetch') || errorStr.includes('NetworkError')) {
            return ERROR_MESSAGES.NETWORK;
        }
        if (errorStr.includes('timeout') || errorStr.includes('Timeout')) {
            return ERROR_MESSAGES.TIMEOUT;
        }
        if (errorStr.includes('429')) {
            return ERROR_MESSAGES.RATE_LIMIT;
        }
        if (errorStr.includes('404')) {
            return ERROR_MESSAGES.NOT_FOUND;
        }
        if (errorStr.includes('500') || errorStr.includes('502')) {
            return ERROR_MESSAGES.SERVER_ERROR;
        }
        if (errorStr.includes('503') || errorStr.includes('AI')) {
            return ERROR_MESSAGES.AI_UNAVAILABLE;
        }
        return ERROR_MESSAGES.DEFAULT;
    },
};

export { API_BASE_URL, ENDPOINTS, TIMEOUTS };
export default window.Config;
