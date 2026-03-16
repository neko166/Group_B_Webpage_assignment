const USER    = window.__USER_DATA__ || {};
const USER_ID = USER.user_id || 1;

let currentRoadmap = null;

// ===== 初期化 =====
document.addEventListener('DOMContentLoaded', async () => {
  await loadLatestRoadmap();
});

// ===== 最新ロードマップ読み込み =====
async function loadLatestRoadmap() {
  // ロードマップ読み込み（ロード中スピナーはHTML初期値でdisplay:flex済み）
  try {
    const res = await fetch(`/api/roadmap/latest/${USER_ID}`);
    if (!res.ok) { showLoading(false); showEmpty(); return; }
    const data = await res.json();
    if (data && data.content && data.content.steps) {
      currentRoadmap = data;
      renderRoadmap(data);
    } else {
      showEmpty();
    }
  } catch (e) {
    console.error('ロードマップ取得エラー:', e);
    showEmpty();
  } finally {
    showLoading(false);
  }
}

// ===== ロードマップ描画 =====
function renderRoadmap(data) {
  try {
    const content = data.content;
    const steps   = content.steps || [];

    // レベル表示: "現在取り組み中" のステップ番号 / 全ステップ数
    const currentStep = steps.find(s => s.status === 'current');
    const levelNum    = currentStep
      ? currentStep.step_number
      : steps.filter(s => s.status === 'completed').length;
    const totalLevels = steps.length;

    // 目標カード
    document.getElementById('goalText').textContent =
      `${data.target_role}へのキャリアアップ`;
    document.getElementById('progressLabel').textContent =
      `レベル ${levelNum}/${totalLevels}`;
    document.getElementById('progressBar').style.width =
      `${content.overall_progress}%`;
    document.getElementById('durationLabel').textContent =
      `目安期間: ${content.estimated_total_duration}`;

    const created = new Date(data.created_at);
    document.getElementById('goalUpdated').textContent =
      `生成日時: ${created.toLocaleDateString('ja-JP')} ${created.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}`;

    // ステップ描画
    const container = document.getElementById('roadmapSteps');
    container.innerHTML = steps.map(step => renderStep(step, steps.length)).join('');

    document.getElementById('roadmapContent').style.display = 'block';
    hideEmpty();
  } catch (e) {
    console.error('ロードマップ描画エラー:', e);
    showEmpty();
  }
}

function renderStep(step, totalSteps) {
  const statusMap = {
    completed: { label: '完了',   cls: 'status-completed' },
    current:   { label: '進行中', cls: 'status-current'   },
    upcoming:  { label: '未着手', cls: 'status-upcoming'  },
  };
  const { label: statusLabel, cls: statusCls } =
    statusMap[step.status] || { label: step.status, cls: '' };

  // サークルアイコン
  let circleInner = '';
  if (step.status === 'completed') {
    circleInner = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>';
  } else if (step.status === 'current') {
    circleInner = '<div class="current-dot"></div>';
  }

  // スキルタグ
  const skillTags = step.skills_to_acquire
    .map(s => `<span class="skill-tag">${s}</span>`)
    .join('');

  // フッターテキスト + アクションボタン
  let footerHtml = '';
  if (step.status === 'completed') {
    footerHtml = '<span class="step-footer-text completed-text">完了済み</span>';
  } else if (step.status === 'current') {
    footerHtml = `
      <span class="step-footer-text current-text">現在進行中（残り ${step.duration}）</span>
      <button class="btn btn-sm btn-dark">学習を開始</button>`;
  } else {
    footerHtml = `<span class="step-footer-text upcoming-text">${step.duration}後に到達予定</span>`;
  }

  // コネクターライン（最後のステップには不要）
  const connector = step.step_number < totalSteps
    ? '<div class="step-line"></div>'
    : '';

  return `
    <div class="roadmap-step step-${step.status}">
      <div class="step-connector">
        <div class="step-circle ${step.status}">${circleInner}</div>
        ${connector}
      </div>
      <div class="step-card">
        <div class="step-card-header">
          <div class="step-badges">
            <span class="level-badge">レベル ${step.step_number}</span>
            <span class="step-status-badge ${statusCls}">${statusLabel}</span>
          </div>
          <button class="btn btn-sm" onclick="openStepDetail(${step.step_number})">詳細</button>
        </div>
        <h3 class="step-title">${step.title}</h3>
        <p class="step-description">${step.description}</p>
        <div class="step-skills-section">
          <div class="skills-header">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            <span class="skills-label">必要なスキル</span>
          </div>
          <div class="skills-tags">${skillTags}</div>
        </div>
        <div class="step-footer">${footerHtml}</div>
      </div>
    </div>
  `;
}

// ===== ステップ詳細モーダル（ステップ情報 + マッチ案件） =====
async function openStepDetail(stepNumber) {
  if (!currentRoadmap) return;
  const step = currentRoadmap.content.steps.find(s => s.step_number === stepNumber);
  if (!step) return;

  const statusLabel = { completed: '完了済み', current: '取り組み中', upcoming: '未着手' }[step.status] || step.status;
  const skillTagsHtml = step.skills_to_acquire
    .map(s => `<span class="skill-tag">${s}</span>`).join(' ');

  document.getElementById('stepDetailTitle').textContent = `STEP ${step.step_number}: ${step.title}`;
  document.getElementById('stepDetailBody').innerHTML = `
    <div class="detail-section">
      <div class="detail-row"><span class="detail-label">ステータス</span><span class="detail-value">${statusLabel}</span></div>
      <div class="detail-row"><span class="detail-label">期間</span><span class="detail-value">${step.duration}</span></div>
      <div class="detail-row"><span class="detail-label">説明</span><span class="detail-value">${step.description}</span></div>
      <div class="detail-row">
        <span class="detail-label">習得スキル</span>
        <span class="detail-value">${skillTagsHtml}</span>
      </div>
    </div>
    <div class="detail-divider"></div>
    <div class="detail-projects-header">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
      おすすめ案件（マッチ度上位2件）
    </div>
    <div id="stepProjectsList">
      <div class="projects-loading">案件を検索中...</div>
    </div>
  `;
  openModal('modalStepDetail');

  // マッチ案件を非同期ロード
  try {
    const skillsCsv = step.skills_to_acquire.join(',');
    const res = await fetch(
      `/api/roadmap/step-projects?step_number=${stepNumber}&skills=${encodeURIComponent(skillsCsv)}`
    );
    const data = await res.json();
    const projects = data.projects || [];

    document.getElementById('stepProjectsList').innerHTML = projects.length === 0
      ? '<p class="no-projects">マッチする案件が見つかりませんでした</p>'
      : projects.map(p => `
          <div class="project-card">
            <div class="project-card-header">
              <div>
                <div class="project-name">${p.project_name}</div>
                <div class="project-company">${p.company}</div>
              </div>
              <div class="project-match">
                <span class="match-badge">${p.match_rate}%</span>
                <span class="match-label">マッチ度</span>
              </div>
            </div>
            <p class="project-overview">${p.project_overview || ''}</p>
            <div class="project-tags">
              ${(p.required_skills || '').split(',').map(s =>
                `<span class="skill-tag">${s.trim()}</span>`
              ).join('')}
            </div>
            <div class="project-meta">
              <span>${p.employ_type || ''}</span>
              <span>${p.project_duration || ''}</span>
            </div>
          </div>
        `).join('');
  } catch (e) {
    document.getElementById('stepProjectsList').innerHTML =
      '<p style="color:#c0392b;font-size:13px">案件の取得に失敗しました</p>';
  }
}

// ===== UI ヘルパー =====
function showLoading(show) {
  document.getElementById('roadmapLoading').style.display = show ? 'flex' : 'none';
}
function showEmpty() {
  document.getElementById('roadmapEmpty').style.display = 'flex';
}
function hideEmpty() {
  document.getElementById('roadmapEmpty').style.display = 'none';
}
