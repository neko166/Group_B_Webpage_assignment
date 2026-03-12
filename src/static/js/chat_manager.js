/**
 * チャット機能を初期化します。
 * @param {object} config - 設定オブジェクト
 * @param {function(string, function)} config.handleSubmit - メッセージ送信時のコールバック関数
 * @param {string} [config.initialMessage] - 初期表示メッセージ
 * @returns {object} - { appendMessage } 外部からメッセージを追加するための関数
 */
function setupChat(config) {
    // --- UI Elements ---
    const chatLog = document.getElementById('chat-log');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    // Sidebar-specific elements
    const toggleChatBtn = document.getElementById('toggle-chat-btn');
    const chatArea = document.getElementById('chat-area');
    const resizer = document.getElementById('chat-resizer');

    // --- Common Functions ---
    const appendMessage = (role, text) => {
        const row = document.createElement('div');
        row.className = `chat-row chat-row--${role}`;
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble chat-bubble--${role}`;
        bubble.textContent = text;

        row.appendChild(bubble);
        chatLog.appendChild(row);
        chatLog.scrollTop = chatLog.scrollHeight;
        return bubble;
    };

    // --- Event Listeners ---
    // フォーム送信
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        chatInput.value = '';
        chatInput.style.height = 'auto';
        sendButton.disabled = true;

        try {
            if (config.handleSubmit) {
                await config.handleSubmit(message, appendMessage);
            }
        } catch (error) {
            console.error('Chat Error:', error);
            appendMessage('assistant', `エラーが発生しました: ${error.message || '不明なエラー'}`);
        } finally {
            sendButton.disabled = false;
            chatInput.focus();
        }
    });

    // キー入力 (Enterで送信、Shift+Enter/Alt+Enterで改行)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !e.altKey) {
            // 日本語変換確定のEnterでないことを確認（isComposingはブラウザによるが念のため）
            if (!e.isComposing) {
                e.preventDefault();
                chatForm.requestSubmit();
            }
        }
    });

    // 自動リサイズ
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });

    // --- Sidebar Logic (Resizer & Toggle) ---
    if (resizer && toggleChatBtn && chatArea) {
        let isResizing = false;
        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            chatArea.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            e.preventDefault();
        });
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            const newWidth = window.innerWidth - e.clientX;
            if (newWidth > 250 && newWidth < window.innerWidth * 0.8) {
                chatArea.style.width = `${newWidth}px`;
            }
        });
        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                chatArea.classList.remove('resizing');
                document.body.style.cursor = '';
            }
        });

        toggleChatBtn.addEventListener('click', () => {
            chatArea.classList.toggle('closed');
            if (chatArea.classList.contains('closed')) {
                toggleChatBtn.textContent = '〈';
                toggleChatBtn.title = 'チャットパネルを開く';
            } else {
                toggleChatBtn.textContent = '〉';
                toggleChatBtn.title = 'チャットパネルを閉じる';
            }
        });
    }

    // --- Init ---
    if (config.initialMessage) {
        appendMessage('assistant', config.initialMessage);
    }

    return { appendMessage };
}