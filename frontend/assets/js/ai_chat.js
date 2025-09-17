import { API_BASE_URL } from './config.js';
import { withLoading } from './ui/loading.js';
import { showToast } from './ui/toast.js';

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value;
    return div.innerHTML;
}

export class AIChatPanel {
    constructor({ contextProvider } = {}) {
        this.contextProvider = contextProvider;
        this.elements = {};
        this.history = [];
        this.questionId = null;
        this.isSending = false;
    }

    mount({ messagesEl, inputEl, sendButton }) {
        this.elements.messages = messagesEl;
        this.elements.input = inputEl;
        this.elements.sendButton = sendButton;

        if (sendButton) {
            sendButton.addEventListener('click', () => this.handleSend());
        }

        if (inputEl) {
            inputEl.addEventListener('keydown', (event) => {
                if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                    event.preventDefault();
                    this.handleSend();
                }
            });
        }
    }

    setContextProvider(provider) {
        this.contextProvider = provider;
    }

    reset() {
        this.history = [];
        this.renderMessages();
        if (this.elements.input) {
            this.elements.input.value = '';
        }
    }

    setQuestion(questionId, { title, solutionViewed }) {
        this.questionId = questionId;
        this.reset();
        if (!this.elements.messages) {
            return;
        }

        const intro = solutionViewed
            ? `You're looking at "${title}". Feel free to ask about optimisations or clarifications.`
            : `You're working on "${title}". Ask for hints, edge cases, or explanations—editorial code stays hidden until you reveal it.`;

        this.appendAssistantMessage(intro, { subtle: true });
    }

    appendAssistantMessage(content, { subtle = false } = {}) {
        this.history.push({ role: 'assistant', content });
        this.renderMessages();
        if (subtle) {
            const last = this.elements.messages?.lastElementChild;
            if (last) {
                last.classList.add('chat-message-info');
            }
        }
    }

    appendUserMessage(content) {
        this.history.push({ role: 'user', content });
        this.renderMessages();
    }

    renderMessages() {
        if (!this.elements.messages) {
            return;
        }
        this.elements.messages.textContent = '';
        for (const message of this.history) {
            const bubble = document.createElement('div');
            bubble.className = `chat-message ${message.role}`;
            bubble.innerHTML = escapeHtml(message.content).replace(/\n/g, '<br />');
            this.elements.messages.appendChild(bubble);
        }
        this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }

    setSending(state) {
        this.isSending = state;
        if (this.elements.sendButton) {
            this.elements.sendButton.disabled = state;
        }
        if (this.elements.input) {
            this.elements.input.disabled = state;
        }
    }

    async handleSend() {
        const text = this.elements.input?.value.trim();
        if (!text) {
            return;
        }
        if (!this.questionId) {
            showToast('Select a question to start the chat.', { type: 'info' });
            return;
        }
        const context = this.contextProvider ? this.contextProvider() : {};
        await this.sendMessage(text, context);
    }

    async sendMessage(content, context = {}) {
        if (this.isSending) {
            return;
        }

        const { code = '', language = 'python' } = context;
        const payload = {
            question_id: this.questionId,
            messages: this.history.map((msg) => ({ role: msg.role, content: msg.content })),
            code,
            language,
        };

        this.appendUserMessage(content);
        this.setSending(true);
        this.elements.input.value = '';

        try {
            const response = await withLoading(
                async () => {
                    const res = await fetch(`${API_BASE_URL}/api/ai/ask`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ...payload, messages: payload.messages }),
                    });
                    if (!res.ok) {
                        const detail = await res.json().catch(() => ({}));
                        const message = detail.detail || 'AI assistant unavailable right now.';
                        throw new Error(message);
                    }
                    return res.json();
                },
                { label: 'Checking with Gemini...' }
            );

            this.history.push({ role: 'assistant', content: response.message });
            this.renderMessages();

            if (response.guardrail_triggered) {
                showToast('Guardrails active: sharing hints only until the solution is unlocked.', { type: 'info' });
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'AI assistant unavailable right now.';
            showToast(message, { type: 'error' });
            // Remove the last user message so conversation stays consistent when retrying.
            this.history = this.history.filter((msg) => !(msg.role === 'user' && msg.content === content));
            this.renderMessages();
        } finally {
            this.setSending(false);
        }
    }
}
