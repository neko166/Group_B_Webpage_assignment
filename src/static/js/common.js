/**
 * Project Common JS
 */
const App = {
    init() {
        this.initBackToTop();
        this.initDoubleSubmitPrevention();
        this.initModals();
    },

    initBackToTop() {
        const btn = document.getElementById('back-to-top');
        if (!btn) return;
        window.addEventListener('scroll', () => {
            btn.style.display = window.scrollY > 300 ? 'flex' : 'none';
        });
        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    },

    initDoubleSubmitPrevention() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('.btn-primary');
                if (submitBtn) {
                    if (submitBtn.disabled) return e.preventDefault();
                    submitBtn.disabled = true;
                    submitBtn.textContent = '送信中...';
                }
            });
        });
    },

    modal: {
        open(id) {
            const target = document.getElementById(id);
            if (target) {
                target.classList.add('is-active');
                document.body.style.overflow = 'hidden';
            }
        },
        close(id) {
            const target = document.getElementById(id);
            if (target) {
                target.classList.remove('is-active');
                document.body.style.overflow = '';
            }
        }
    },

    initModals() {
        document.querySelectorAll('.c-modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.modal.close(modal.id);
            });
        });
    },

    chatApi: {
        async request({
            apiType,
            message,
            endpointMap,
            baseUrl = '',
            method = 'POST',
            headers = {},
            bodyBuilder
        }) {
            if (!apiType) {
                throw new Error('apiType is required');
            }
            if (!endpointMap || !endpointMap[apiType]) {
                throw new Error(`Endpoint is not defined for apiType: ${apiType}`);
            }

            const endpoint = endpointMap[apiType];
            const url = this.buildUrl(baseUrl, endpoint);
            const payload = typeof bodyBuilder === 'function'
                ? bodyBuilder({ apiType, message })
                : { message };

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                body: JSON.stringify(payload)
            });

            let data = null;
            try {
                data = await response.json();
            } catch (error) {
                data = null;
            }

            if (!response.ok) {
                const errorMessage = (data && (data.error || data.message)) || `HTTP ${response.status}`;
                throw new Error(errorMessage);
            }

            return data;
        },

        buildUrl(baseUrl, endpoint) {
            if (/^https?:\/\//.test(endpoint)) {
                return endpoint;
            }
            const normalizedBase = baseUrl.replace(/\/$/, '');
            const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
            return `${normalizedBase}${normalizedEndpoint}`;
        },

        getAssistantText(data) {
            if (!data) return 'レスポンスが空です。';
            if (typeof data === 'string') return data;
            if (typeof data.reply === 'string') return data.reply;
            if (typeof data.message === 'string') return data.message;
            if (typeof data.text === 'string') return data.text;
            return JSON.stringify(data, null, 2);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());

// ===== 全ページ共通モーダルヘルパー =====
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
