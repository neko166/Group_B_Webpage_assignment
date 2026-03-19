/* ============================================================
   chat.js – AIキャリアアドバイザー チャット（会話履歴対応）
   ============================================================ */

const userData       = window.__USER_DATA__ || {};
const USER_ID        = userData.user_id || 1;
let attachedFiles    = [];
let isLoading        = false;
let currentSessionId = null;   // 現在アクティブなセッションID

// ===== モーダル共通 =====
function openModal(id)  { const el = document.getElementById(id); if (el) el.classList.add('open'); }
function closeModal(id) { const el = document.getElementById(id); if (el) el.classList.remove('open'); }

// ===== 初期化 =====
document.addEventListener('DOMContentLoaded', async () => {
  const input   = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');

  // テキストエリア自動リサイズ
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });

  // Enter送信（Shift+Enterで改行）
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  sendBtn.addEventListener('click', handleSend);
  document.getElementById('fileInput').addEventListener('change', handleFileAttach);
  document.getElementById('roadmapBtn').addEventListener('click', generateAndOpenRoadmap);
  document.getElementById('startNewChat').addEventListener('click', startNewChat);
  document.getElementById('newChatBtn').addEventListener('click', startNewChat);

  // バックドロップで閉じる
  document.querySelectorAll('.modal-backdrop').forEach(bd => {
    bd.addEventListener('click', e => { if (e.target === bd) bd.classList.remove('open'); });
  });

  // 会話履歴をサイドバーに読み込み、最新セッションを自動表示
  await loadSessions(true);
});

// ===== セッション一覧読み込み =====
async function loadSessions(autoLoadLatest = false) {
  try {
    const res = await fetch(`/api/chat/sessions?user_id=${USER_ID}`);
    if (!res.ok) return;
    const sessions = await res.json();
    renderSessionList(sessions);
    // 初回ロード時：最新セッションを自動で開く
    if (autoLoadLatest && sessions && sessions.length > 0 && !currentSessionId) {
      await loadSession(sessions[0].session_id);
    }
  } catch (e) {
    console.error('Session load error:', e);
  }
}

// ===== セッション一覧描画 =====
function renderSessionList(sessions) {
  const list = document.getElementById('historyList');
  if (!sessions || sessions.length === 0) {
    list.innerHTML = '<div class="history-empty">履歴はありません</div>';
    return;
  }
  list.innerHTML = sessions.map(s => `
    <div class="history-item ${s.session_id === currentSessionId ? 'active' : ''}"
         onclick="loadSession(${s.session_id})">
      <div class="history-item-header">
        <div class="history-item-title">${escapeHtml(s.title)}</div>
        <button class="history-delete-btn" onclick="deleteSession(event, ${s.session_id})" title="削除">×</button>
      </div>
      <div class="history-date">${formatSessionDate(s.updated_at)}</div>
    </div>
  `).join('');
}

// ===== セッション読み込み（履歴クリック） =====
async function loadSession(sessionId) {
  if (isLoading) return;
  if (sessionId === currentSessionId) return;

  try {
    const res = await fetch(`/api/chat/sessions/${sessionId}`);
    if (!res.ok) return;
    const data = await res.json();

    currentSessionId = sessionId;

    // チャットエリアをクリアして履歴を表示
    const container = document.getElementById('chatMessages');
    container.innerHTML = '';
    document.getElementById('chatSuggestions').style.display = 'none';

    if (data.messages.length === 0) {
      // メッセージなし → ウェルカム表示
      showWelcomeMessage();
      document.getElementById('chatSuggestions').style.display = 'flex';
    } else {
      data.messages.forEach(msg => {
        if (msg.role === 'user') {
          appendUserMessage(msg.content);
        } else {
          appendAIMessage(msg.content);
        }
      });
    }

    // サイドバーのアクティブ状態を更新
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.history-item').forEach(el => {
      if (el.getAttribute('onclick') === `loadSession(${sessionId})`) {
        el.classList.add('active');
      }
    });
  } catch (e) {
    console.error('Load session error:', e);
  }
}

// ===== セッション削除 =====
async function deleteSession(event, sessionId) {
  event.stopPropagation();
  try {
    await fetch(`/api/chat/sessions/${sessionId}`, { method: 'DELETE' });
    if (currentSessionId === sessionId) {
      currentSessionId = null;
      showWelcomeMessage();
      document.getElementById('chatSuggestions').style.display = 'flex';
    }
    await loadSessions();
  } catch (e) {
    console.error('Delete session error:', e);
  }
}

// ===== メッセージ送信 =====
async function handleSend() {
  if (isLoading) return;
  const input = document.getElementById('chatInput');
  const text  = input.value.trim();
  if (!text && attachedFiles.length === 0) return;

  // セッションがなければ新規作成
  if (!currentSessionId) {
    const ok = await createSession();
    if (!ok) return;
  }

  // サジェストを非表示
  document.getElementById('chatSuggestions').style.display = 'none';

  // ユーザーメッセージ表示 + DB保存
  appendUserMessage(text, attachedFiles);
  input.value = '';
  input.style.height = 'auto';
  clearAttachedFiles();

  await saveMessage('user', text);

  // AI返答（ストリーミング）+ DB保存
  await fetchAIResponse(text);

  // サイドバー更新（タイトルが変わっている場合のため）
  await loadSessions();
}

// ===== セッション新規作成 =====
async function createSession() {
  try {
    const res = await fetch('/api/chat/sessions', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ user_id: USER_ID }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    currentSessionId = data.session_id;
    return true;
  } catch (e) {
    console.error('Create session error:', e);
    return false;
  }
}

// ===== メッセージ DB 保存 =====
async function saveMessage(role, content) {
  if (!currentSessionId || !content.trim()) return;
  try {
    await fetch(`/api/chat/sessions/${currentSessionId}/messages`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ role, content }),
    });
  } catch (e) {
    console.error('Save message error:', e);
  }
}

// ===== ロードマップ生成 =====
async function generateAndOpenRoadmap() {
  if (isLoading) return;
  isLoading = true;
  document.getElementById('sendBtn').disabled = true;
  appendLoadingMessage();

  try {
    const res = await fetch('/api/roadmap/generate', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ user_id: USER_ID }),
    });
    removeLoadingMessage();
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      appendAIMessage('ロードマップの生成に失敗しました。Ollamaが起動しているか確認してください。\n詳細: ' + (err.detail || res.status));
      return;
    }
    window.location.href = '/roadmap';
  } catch (e) {
    removeLoadingMessage();
    appendAIMessage('ロードマップの生成に失敗しました。サーバーに接続できません。');
    console.error('Roadmap generation error:', e);
  } finally {
    isLoading = false;
    document.getElementById('sendBtn').disabled = false;
  }
}

function sendSuggestion(text) {
  document.getElementById('chatInput').value = text;
  handleSend();
}

// ===== メッセージ追加 =====
function appendUserMessage(text, files = []) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'message message-user';

  const filesHtml = files.map(f => `
    <div class="message-attachment">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
      ${f.name}
    </div>
  `).join('');

  div.innerHTML = `
    <div class="message-avatar">
      <svg viewBox="0 0 32 32" fill="none" width="22" height="22">
        <circle cx="16" cy="12" r="6" fill="#888"/>
        <path d="M4 28c0-6.627 5.373-12 12-12s12 5.373 12 12" fill="#888"/>
      </svg>
    </div>
    <div class="message-content">
      <div class="message-bubble">${escapeHtml(text)}${filesHtml}</div>
      <div class="message-label" style="text-align:right">あなた</div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

function appendAIMessage(text) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'message message-ai';
  div.innerHTML = `
    <div class="message-avatar">
      <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
        <circle cx="16" cy="16" r="16" fill="#c84b11" opacity="0.15"/>
        <circle cx="16" cy="16" r="5" fill="#c84b11"/>
      </svg>
    </div>
    <div class="message-content">
      <div class="message-bubble">${formatAIText(text)}</div>
      <div class="message-label">AIアドバイザー</div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

// ストリーミング用: 空バブルを追加してその要素を返す
function appendStreamingAIMessage() {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'message message-ai';
  div.innerHTML = `
    <div class="message-avatar">
      <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
        <circle cx="16" cy="16" r="16" fill="#c84b11" opacity="0.15"/>
        <circle cx="16" cy="16" r="5" fill="#c84b11"/>
      </svg>
    </div>
    <div class="message-content">
      <div class="message-bubble streaming-bubble"></div>
      <div class="message-label">AIアドバイザー</div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
  return div.querySelector('.streaming-bubble');
}

function appendLoadingMessage() {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'message message-ai';
  div.id = 'loadingMsg';
  div.innerHTML = `
    <div class="message-avatar">
      <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
        <circle cx="16" cy="16" r="16" fill="#c84b11" opacity="0.15"/>
        <circle cx="16" cy="16" r="5" fill="#c84b11"/>
      </svg>
    </div>
    <div class="message-content">
      <div class="message-bubble loading">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
      </div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

function removeLoadingMessage() {
  const el = document.getElementById('loadingMsg');
  if (el) el.remove();
}

// ===== AI API呼び出し（ストリーミング） =====
async function fetchAIResponse(userText) {
  isLoading = true;
  document.getElementById('sendBtn').disabled = true;
  appendLoadingMessage();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message:      userText,
        current_role: userData.current_role || '',
        target_role:  userData.target_role  || '',
        user_name:    userData.name         || '',
      }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    removeLoadingMessage();
    const bubble = appendStreamingAIMessage();

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer   = '';
    let fullText = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = line.slice(6).trim();
        if (payload === '[DONE]') break;
        try {
          const { token } = JSON.parse(payload);
          fullText += token;
          bubble.innerHTML = formatAIText(fullText);
          scrollToBottom();
        } catch (_) { /* ignore parse errors */ }
      }
    }

    if (!fullText.trim()) {
      bubble.innerHTML = 'エラーが発生しました。もう一度お試しください。';
    } else {
      // AI返答をDBに保存
      await saveMessage('assistant', fullText);
    }

  } catch (err) {
    removeLoadingMessage();
    appendAIMessage('申し訳ありません。エラーが発生しました。もう一度お試しください。');
    console.error('Chat API error:', err);
  } finally {
    isLoading = false;
    document.getElementById('sendBtn').disabled = false;
  }
}

// ===== ファイル添付 =====
function handleFileAttach(e) {
  const files = Array.from(e.target.files);
  files.forEach(f => {
    if (!attachedFiles.find(x => x.name === f.name)) attachedFiles.push(f);
  });
  renderAttachedFiles();
  e.target.value = '';
}

function renderAttachedFiles() {
  const container = document.getElementById('attachedFiles');
  container.innerHTML = attachedFiles.map((f, i) => `
    <div class="attached-file-chip">
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
      ${f.name}
      <button onclick="removeFile(${i})">×</button>
    </div>
  `).join('');
}

function removeFile(index) {
  attachedFiles.splice(index, 1);
  renderAttachedFiles();
}

function clearAttachedFiles() {
  attachedFiles = [];
  renderAttachedFiles();
}

// ===== 新しい相談 =====
function startNewChat() {
  currentSessionId = null;
  showWelcomeMessage();
  document.getElementById('chatSuggestions').style.display = 'flex';
  document.getElementById('chatInput').value = '';
  clearAttachedFiles();
  // サイドバーのアクティブ解除
  document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
}

// ===== ウェルカムメッセージ表示 =====
function showWelcomeMessage() {
  const container = document.getElementById('chatMessages');
  container.innerHTML = `
    <div class="message message-ai">
      <div class="message-avatar">
        <svg viewBox="0 0 32 32" fill="none" width="32" height="32">
          <circle cx="16" cy="16" r="16" fill="#c84b11" opacity="0.15"/>
          <circle cx="16" cy="16" r="5" fill="#c84b11"/>
        </svg>
      </div>
      <div class="message-content">
        <div class="message-bubble">
          こんにちは！私はあなたのAIキャリアアドバイザーです。社内のキャリア図鑑データを参照しながら、あなたの目標に最適なキャリアパスをご提案します。<br><br>
          現在のスキルや将来の目標について教えてください。例えば「3年以内にアーキテクトになりたい」「AIエンジニアに転向したい」など、どんなことでもお気軽にご相談ください。
        </div>
        <div class="message-label">AIアドバイザー</div>
      </div>
    </div>
  `;
}

// ===== ユーティリティ =====
function scrollToBottom() {
  const container = document.getElementById('chatMessages');
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
}

function formatAIText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

function formatSessionDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return '';
  const now  = new Date();
  const diff = now - d;
  const mins = Math.floor(diff / 60000);
  if (mins <   1) return 'たった今';
  if (mins <  60) return `${mins}分前`;
  const hrs = Math.floor(mins / 60);
  if (hrs  <  24) return `${hrs}時間前`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return '昨日';
  if (days  <  7) return `${days}日前`;
  return d.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' });
}
