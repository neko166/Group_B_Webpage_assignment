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
        console.log(`[CHAT ${role.toUpperCase()}] ${text}`);
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

        console.log(`[CHAT SEND] ${message}`);
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

/**
 * Dify APIにリクエストを送信します。
 * @param {object} payload - リクエストペイロード
 * @returns {object} - レスポンスデータ
 */
async function sendToDify(payload) {
    console.log('[SEND PAYLOAD]', payload);
    const response = await fetch('/api/dify/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`API request failed: ${errorBody}`);
    }

    const data = await response.json();
    console.log('[RECEIVE RESPONSE]', data);
    return data;
}

/**
 * Difyのレスポンスをパースします。
 * @param {string} answerText - レスポンスのanswerテキスト
 * @returns {object} - パースされたデータ
 */
function parseDifyResponse(answerText) {
    console.log('[PARSE INPUT]', answerText);
    let parsedData = { message: answerText };
    try {
        // まず、```json ブロックを探す
        const jsonMatch = answerText.match(/```json\s*([\s\S]*?)\s*```/);
        if (jsonMatch) {
            parsedData = JSON.parse(jsonMatch[1]);
        } else {
            // 次に、全体が JSON かどうか試す
            parsedData = JSON.parse(answerText);
        }
    } catch (e) {
        // JSON でない場合は、message として扱う
        console.warn("JSON parse failed, treating as plain text:", e);
    }
    console.log('[PARSED DATA]', parsedData);
    return parsedData;
}

/**
 * オプションボタンを表示します。
 * @param {Array} options - オプションの配列
 */
function displayOptions(options) {
    if (!options || options.length === 0) return;

    const chatLog = document.querySelector('.chat-log') || document.getElementById('chat-log');
    if (!chatLog) return;

    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'chat-options-container';
    options.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'chat-option-btn';
        btn.textContent = opt;
        btn.addEventListener('click', () => {
            const input = document.getElementById('chat-input');
            const sendBtn = document.getElementById('send-button');
            if (input && sendBtn) {
                input.value = opt;
                sendBtn.click();
                optionsDiv.remove();
            }
        });
        optionsDiv.appendChild(btn);
    });
    chatLog.appendChild(optionsDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}