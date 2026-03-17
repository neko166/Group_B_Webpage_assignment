const SUMMARY_USER_ID = window.__SUMMARY_USER_ID__ || 1;

// ===== タブ切替 =====
function switchTab(tab, btn) {
  document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.summary-tab').forEach(el => el.classList.remove('active'));
  document.getElementById(tab === 'proposal' ? 'tabProposal' : 'tabAssign').style.display = 'block';
  btn.classList.add('active');
}

// ===== データ取得 =====
async function loadAll() {
  const [user, skills, careers] = await Promise.all([
    fetch(`/users/${SUMMARY_USER_ID}`).then(r => r.json()),
    fetch(`/users/${SUMMARY_USER_ID}/skills`).then(r => r.json()),
    fetch(`/users/${SUMMARY_USER_ID}/careers`).then(r => r.json()),
  ]);

  // ロードマップの現在ステップを取得してマッチング案件を検索
  let matchProjects = [];
  try {
    const roadmap = await fetch(`/api/roadmap/latest/${SUMMARY_USER_ID}`).then(r => r.json());
    if (roadmap && roadmap.content && roadmap.content.steps) {
      const currentStep = roadmap.content.steps.find(s => s.status === 'current')
        || roadmap.content.steps.find(s => s.status === 'completed')
        || roadmap.content.steps[0];
      if (currentStep) {
        // LLM生成の日本語スキル名 + ユーザーの実スキル名（英語）を合わせてマッチング精度を上げる
        const stepSkills = (currentStep.skills_to_acquire || []).join(',');
        const userSkillNames = skills.map(s => s.skill_name).join(',');
        const combinedSkills = [stepSkills, userSkillNames].filter(Boolean).join(',');
        const resp = await fetch(
          `/api/roadmap/step-projects?step_number=${currentStep.step_number}&skills=${encodeURIComponent(combinedSkills)}`
        ).then(r => r.json());
        matchProjects = resp.projects || [];
      }
    }
  } catch (e) {
    console.warn('ロードマップ取得失敗:', e);
  }

  // LLMで強みを生成（非同期で後から反映）
  renderProposal(user, skills, careers, matchProjects);
  renderAssign(user, skills, careers, matchProjects);

  // 強み・特徴をLLMで生成して後から差し込む
  loadStrengths();
}

async function loadStrengths() {
  const el = document.getElementById('p_strengths');
  el.innerHTML = '<li style="color:#aaa">AIが分析中...</li>';
  try {
    const data = await fetch(`/api/roadmap/skill-summary/${SUMMARY_USER_ID}`).then(r => r.json());
    const strengths = data.strengths || [];
    if (strengths.length > 0) {
      el.innerHTML = strengths.map(s => `<li>${s}</li>`).join('');
    } else {
      el.innerHTML = '<li style="color:#aaa">強みを生成できませんでした</li>';
    }
  } catch (e) {
    el.innerHTML = '<li style="color:#aaa">生成に失敗しました（Ollama未起動の可能性）</li>';
  }
}

// ===== 提案書フォーマット =====
function renderProposal(user, skills, careers, matchProjects) {
  // プロフィール
  document.getElementById('p_name').textContent      = user.name || '—';
  document.getElementById('p_age').textContent       = user.age ? `${user.age}歳` : '—';
  document.getElementById('p_exp').textContent       = user.experience_years ? `${user.experience_years}年` : '—';
  document.getElementById('p_available').textContent = user.available_from || '—';
  document.getElementById('p_locations').textContent = user.work_locations
    ? user.work_locations.split(',').map(s => s.trim()).filter(Boolean).join('・')
    : '—';
  document.getElementById('p_conditions').textContent = user.work_conditions || '—';

  // 技術スタック（カテゴリ別）
  const stackEl = document.getElementById('p_stack');
  const grouped = {};
  skills.forEach(s => {
    const cat = s.category || 'その他';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(s.skill_name);
  });
  if (Object.keys(grouped).length > 0) {
    stackEl.innerHTML = Object.entries(grouped).map(([cat, names]) => `
      <div class="stack-category">${cat}</div>
      <div class="stack-tags">${names.map(n => `<span class="stack-tag">${n}</span>`).join('')}</div>
    `).join('');
  } else {
    stackEl.innerHTML = '<p style="color:#aaa;font-size:13px">スキルを登録してください</p>';
  }

  // スキルレベル評価（個別スキルを5段階ドット表示）
  const barsEl = document.getElementById('p_level_bars');
  if (skills.length > 0) {
    barsEl.innerHTML = skills.map(s => {
      const level = s.skill_level || 0;
      const dots = Array.from({length: 5}, (_, i) =>
        `<span class="skill-dot ${i < level ? 'filled' : 'empty'}"></span>`
      ).join('');
      return `
        <div class="level-bar-row">
          <div class="level-bar-label">
            <span>${s.skill_name}</span>
            <span class="skill-dots">${dots}</span>
          </div>
        </div>`;
    }).join('');
  } else {
    barsEl.innerHTML = '<p style="color:#aaa;font-size:13px">スキルを登録してください</p>';
  }

  // 職務経歴
  const careersEl = document.getElementById('p_careers');
  if (careers.length === 0) {
    careersEl.innerHTML = '<p style="color:#aaa;font-size:13px">職務経歴を登録してください</p>';
  } else {
    careersEl.innerHTML = careers.map(c => {
      const start = c.period_start ? c.period_start.substring(0, 7).replace('-', '/') : '';
      const end   = c.period_end   ? c.period_end.substring(0, 7).replace('-', '/') : '現在';
      const techs = (c.tech_stack || '').split(',').map(s => s.trim()).filter(Boolean);
      const results = (c.description || '').split('\n').filter(Boolean);
      return `
        <div class="career-entry">
          <div class="career-period">${start}${start ? ' - ' : ''}${end}</div>
          <div class="career-company">${c.project_name}</div>
          <div class="career-role-text">${c.role || ''}</div>
          ${results.length > 0 ? `
            <div class="career-results-label">主な成果</div>
            <ul class="career-results">${results.map(r => `<li>${r}</li>`).join('')}</ul>
          ` : ''}
          <div class="career-tech-tags">${techs.map(t => `<span class="career-tech-tag">${t}</span>`).join('')}</div>
        </div>`;
    }).join('');
  }

  // マッチング案件提案（ロードマップ現在ステップベース）
  const projectsEl = document.getElementById('p_projects');
  if (matchProjects.length === 0) {
    projectsEl.innerHTML = '<p style="color:#aaa;font-size:13px">ロードマップを生成すると案件提案が表示されます</p>';
  } else {
    projectsEl.innerHTML = matchProjects.map(p => `
      <div class="project-card">
        <div class="project-card-header">
          <div>
            <div class="project-id">案件ID: P${String(p.project_id).padStart(3,'0')}</div>
            <div class="project-title">${p.project_name}</div>
            <div class="project-company-name">${p.company}</div>
          </div>
          <div style="text-align:right">
            <div class="match-pct-big">${p.match_rate}%</div>
            <div class="match-label">マッチ度</div>
          </div>
        </div>
        <div class="project-meta">
          <span>予算: ${p.budget ? `¥${p.budget.toLocaleString()} / 月` : '—'}</span>
          <span>期間: ${p.project_duration || '—'}</span>
        </div>
        <div class="proposal-reason">
          <div class="proposal-reason-label">提案理由</div>
          ${p.project_overview}
        </div>
      </div>`).join('');
  }
}

// ===== 案件アサインフォーマット =====
function renderAssign(user, skills, careers, matchProjects) {
  document.getElementById('a_name').textContent      = user.name || '—';
  document.getElementById('a_role').textContent      = user.current_role || '—';
  document.getElementById('a_available').textContent = user.available_from || '—';

  // 適性分析（カテゴリ別）
  const catAvg = {};
  skills.forEach(s => {
    const cat = s.category || 'その他';
    if (!catAvg[cat]) catAvg[cat] = { total: 0, count: 0 };
    catAvg[cat].total += s.skill_level;
    catAvg[cat].count++;
  });

  const suitEl = document.getElementById('a_suitability');
  const catEntries = Object.entries(catAvg).sort((a, b) => (b[1].total/b[1].count) - (a[1].total/a[1].count));
  const levelLabels = ['未設定', '入門', '初級', '中級', '上級', '専門'];

  suitEl.innerHTML = catEntries.map(([cat, v]) => {
    const avg        = v.total / v.count;
    const avgDisplay = Math.round(avg * 10) / 10;
    const catSkills  = skills.filter(s => (s.category || 'その他') === cat);

    const strong  = catSkills.filter(s => s.skill_level >= 4);
    const mid     = catSkills.filter(s => s.skill_level === 3);
    const weak    = catSkills.filter(s => s.skill_level <= 2 && s.skill_level > 0);

    const nameList = arr => arr.map(s => `${s.skill_name}（${levelLabels[s.skill_level] || `Lv.${s.skill_level}`}）`).join('、');

    let badge, narrative;

    if (avg >= 4) {
      badge = '<span class="badge-optimal">最適</span>';
      let text = `${nameList(strong)} を上位レベルで保有しており、${cat}案件に対して即戦力としてのアサインが可能です。`;
      if (mid.length > 0) text += ` ${nameList(mid)} についても実務レベルに達しており、幅広い要件に対応できます。`;
      text += ` 提案時は「${strong[0]?.skill_name || cat}の高度な専門性」を前面に出すことで、クライアントへの訴求力が高まります。`;
      narrative = text;
    } else if (avg >= 3) {
      badge = '<span class="badge-suitable">適性あり</span>';
      let text = '';
      if (strong.length > 0) text += `${nameList(strong)} は即戦力水準に達しており、${cat}案件の中核スキルとして評価できます。`;
      if (mid.length > 0)    text += ` ${nameList(mid)} は実務対応可能なレベルで、チームサポート役としての活躍が見込めます。`;
      if (weak.length > 0)   text += ` 一方、${nameList(weak)} はまだ習得途上のため、この領域をカバーできるチーム体制を整えることでアサイン可能となります。`;
      text += ` ${cat}案件へのアサインは「補完体制あり」を条件に提案することを推奨します。`;
      narrative = text;
    } else {
      badge = '<span class="badge-review">要検討</span>';
      let text = '';
      if (weak.length > 0 || mid.length > 0) {
        const partial = [...mid, ...weak];
        text += `${nameList(partial)} の知識は保有していますが、いずれも${cat}案件で求められる実務水準には達していません。`;
      } else {
        text += `${cat}分野のスキルが未登録または入門レベルのため、現時点での専門案件へのアサインは困難です。`;
      }
      if (strong.length > 0) text += ` ただし ${nameList(strong)} の強みを活かせる周辺ポジションへの提案は検討の余地があります。`;
      text += ` 今後 ${cat}分野のスキルを中級（Lv.3）以上に引き上げることで「適性あり」への移行が見込めます。`;
      narrative = text;
    }

    const skillRowsHtml = catSkills.map(s => {
      const lv   = s.skill_level || 0;
      const dots = Array.from({length: 5}, (_, i) =>
        `<span class="skill-dot ${i < lv ? 'filled' : 'empty'}"></span>`
      ).join('');
      return `
        <div class="suit-skill-row">
          <span class="suit-skill-name">${s.skill_name}</span>
          <span class="skill-dots">${dots}</span>
          <span class="suit-skill-level">${levelLabels[lv] || `Lv.${lv}`}</span>
        </div>`;
    }).join('');

    return `
      <div class="suitability-card">
        <div class="suitability-header">
          <div class="suitability-title">${cat}案件</div>
          ${badge}
        </div>
        <div class="suitability-score">平均スキルレベル：${avgDisplay} / 5.0（${v.count}スキル）</div>
        <div class="suitability-desc">${narrative}</div>
        <div class="suitability-skills">${skillRowsHtml}</div>
      </div>`;
  }).join('');

  // 推薦案件
  document.getElementById('a_projects').innerHTML = matchProjects.length > 0
    ? matchProjects.map(p => `
        <div class="assign-project-row">
          <div>
            <div class="assign-proj-id">P${String(p.project_id).padStart(3,'0')}: ${p.project_name}</div>
            <div class="assign-proj-company">${p.company}</div>
          </div>
          <span class="assign-match-badge">${p.match_rate}%</span>
        </div>`).join('')
    : '<p style="color:#aaa;font-size:13px">ロードマップを生成すると案件提案が表示されます</p>';

  // 注意事項
  const notes = [];
  if (user.work_locations) {
    const locs = user.work_locations.split(',').map(s => s.trim()).filter(Boolean);
    if (locs.length > 0) notes.push(`希望勤務地: ${locs.join('・')}`);
  }
  if (user.work_conditions) {
    const cond = user.work_conditions.trim();
    if (/リモート/i.test(cond)) notes.push('リモートワーク希望のため、出社必須案件は避ける');
    notes.push(`その他条件: ${cond}`);
  }
  if (user.available_from) notes.push(`稼働可能時期: ${user.available_from}`);
  if (user.target_role)    notes.push(`次のキャリアステップとして「${user.target_role}」を志向`);
  if (notes.length === 0)  notes.push('プロフィールを編集して注意事項を設定してください');
  document.getElementById('a_notes').innerHTML = notes.map(n => `<li>${n}</li>`).join('');
}

document.addEventListener('DOMContentLoaded', loadAll);

// ===== メール送信モーダル =====
function openEmailModal() {
  document.getElementById('emailTo').value = '';
  document.getElementById('emailError').style.display = 'none';
  document.getElementById('emailSendBtn').disabled = false;
  document.getElementById('emailSendBtn').textContent = '送信';
  const m = document.getElementById('emailModal');
  m.style.display = 'flex';
  setTimeout(() => document.getElementById('emailTo').focus(), 50);
}

function closeEmailModal() {
  document.getElementById('emailModal').style.display = 'none';
}

async function submitEmail() {
  const to = document.getElementById('emailTo').value.trim();
  const errEl = document.getElementById('emailError');
  if (!to || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) {
    errEl.textContent = '正しいメールアドレスを入力してください';
    errEl.style.display = 'block';
    return;
  }
  errEl.style.display = 'none';
  const btn = document.getElementById('emailSendBtn');
  btn.disabled = true;
  btn.textContent = '送信中...';
  try {
    const res = await fetch('/api/roadmap/send-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: SUMMARY_USER_ID, to_email: to }),
    });
    const data = await res.json();
    if (!res.ok) {
      errEl.textContent = data.detail || '送信に失敗しました';
      errEl.style.display = 'block';
      btn.disabled = false;
      btn.textContent = '送信';
      return;
    }
    closeEmailModal();
    showToast(`✓ ${to} にメールを送信しました`);
  } catch (e) {
    errEl.textContent = 'ネットワークエラーが発生しました';
    errEl.style.display = 'block';
    btn.disabled = false;
    btn.textContent = '送信';
  }
}

function showToast(msg) {
  const t = document.getElementById('emailToast');
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(() => { t.style.display = 'none'; }, 3500);
}

// モーダル外クリックで閉じる
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('emailModal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeEmailModal();
  });
});
