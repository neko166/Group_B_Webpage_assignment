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
  const [user, skills, careers, projects] = await Promise.all([
    fetch(`/users/${SUMMARY_USER_ID}`).then(r => r.json()),
    fetch(`/users/${SUMMARY_USER_ID}/skills`).then(r => r.json()),
    fetch(`/users/${SUMMARY_USER_ID}/careers`).then(r => r.json()),
    fetch(`/api/roadmap/projects`).then(r => r.json()),
  ]);

  renderProposal(user, skills, careers, projects);
  renderAssign(user, skills, careers, projects);
}

function formatRate(min, max) {
  if (!min && !max) return '—';
  const fmt = v => `¥${(v / 10000).toLocaleString()}万`;
  if (min && max) return `${fmt(min)} - ${fmt(max)} / 月`;
  if (min) return `${fmt(min)}〜 / 月`;
  return `〜${fmt(max)} / 月`;
}

// ===== 提案書フォーマット =====
function renderProposal(user, skills, careers, projects) {
  // プロフィール
  document.getElementById('p_name').textContent      = user.name || '—';
  document.getElementById('p_age').textContent       = user.age ? `${user.age}歳` : '—';
  document.getElementById('p_exp').textContent       = user.experience_years ? `${user.experience_years}年` : '—';
  document.getElementById('p_role').textContent      = user.current_role || '—';
  document.getElementById('p_available').textContent = user.available_from || '—';
  document.getElementById('p_locations').textContent = user.work_locations
    ? user.work_locations.split(',').map(s => s.trim()).filter(Boolean).join('・')
    : '—';
  document.getElementById('p_rate').textContent      = formatRate(user.desired_rate_min, user.desired_rate_max);

  // スキル強み（スキルレベル4以上を強みとして列挙）
  const topSkills = skills.filter(s => s.skill_level >= 4);
  const strengths = document.getElementById('p_strengths');
  if (topSkills.length > 0) {
    strengths.innerHTML = topSkills.map(s =>
      `<li>${s.skill_name}（レベル${s.skill_level}）を活用した開発・構築</li>`
    ).join('');
  } else {
    strengths.innerHTML = '<li>スキルを登録してください</li>';
  }

  // 技術スタック（カテゴリ別）
  const stackEl = document.getElementById('p_stack');
  const grouped = {};
  skills.forEach(s => {
    const cat = s.category || 'その他';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(s.skill_name);
  });
  stackEl.innerHTML = Object.entries(grouped).map(([cat, names]) => `
    <div class="stack-category">${cat}</div>
    <div class="stack-tags">${names.map(n => `<span class="stack-tag">${n}</span>`).join('')}</div>
  `).join('');

  // スキルレベルバー（カテゴリ別平均）
  const barsEl = document.getElementById('p_level_bars');
  const catAvg = {};
  skills.forEach(s => {
    const cat = s.category || 'その他';
    if (!catAvg[cat]) catAvg[cat] = { total: 0, count: 0 };
    catAvg[cat].total += s.skill_level;
    catAvg[cat].count++;
  });
  barsEl.innerHTML = Object.entries(catAvg).map(([cat, v]) => {
    const pct = Math.round(v.total / v.count / 5 * 100);
    return `
      <div class="level-bar-row">
        <div class="level-bar-label"><span>${cat}</span><span>${pct}%</span></div>
        <div class="level-bar-bg"><div class="level-bar-fill" style="width:${pct}%"></div></div>
      </div>`;
  }).join('');

  // 職務経歴
  const careersEl = document.getElementById('p_careers');
  if (careers.length === 0) {
    careersEl.innerHTML = '<p style="color:#aaa;font-size:13px">職務経歴を登録してください</p>';
  } else {
    careersEl.innerHTML = careers.map(c => {
      const start = c.period_start ? c.period_start.substring(0, 7).replace('-', '/') : '';
      const end   = c.period_end   ? c.period_end.substring(0, 7).replace('-', '/') : '現在';
      const techs = (c.tech_stack || '').split(',').map(s => s.trim()).filter(Boolean);
      return `
        <div class="career-entry">
          <div class="career-period">${start}${start ? ' - ' : ''}${end}</div>
          <div class="career-company">${c.project_name}</div>
          <div class="career-role-text">${c.role || ''}</div>
          ${c.description ? `
            <div class="career-results-label">主な業務内容</div>
            <ul class="career-results"><li>${c.description}</li></ul>
          ` : ''}
          <div class="career-tech-tags">${techs.map(t => `<span class="career-tech-tag">${t}</span>`).join('')}</div>
        </div>`;
    }).join('');
  }

  // マッチング案件（match_rate上位3件）
  const sorted = [...projects].sort((a, b) => b.match_rate - a.match_rate).slice(0, 3);
  const projectsEl = document.getElementById('p_projects');
  projectsEl.innerHTML = sorted.map((p, i) => `
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
        <span>勤務形態: ${p.employ_type}</span>
      </div>
      <div class="proposal-reason">
        <div class="proposal-reason-label">提案理由</div>
        ${p.project_overview}
      </div>
    </div>`).join('');
}

// ===== 案件アサインフォーマット =====
function renderAssign(user, skills, careers, projects) {
  document.getElementById('a_name').textContent      = user.name || '—';
  document.getElementById('a_role').textContent      = user.current_role || '—';
  document.getElementById('a_available').textContent = user.available_from || '—';
  document.getElementById('a_rate').textContent      = formatRate(user.desired_rate_min, user.desired_rate_max);

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
  suitEl.innerHTML = catEntries.map(([cat, v]) => {
    const avg = v.total / v.count;
    let badge, desc;
    if (avg >= 4) {
      badge = '<span class="badge-optimal">最適</span>';
      desc  = `${cat}分野に高い適性。即戦力として期待できる。`;
    } else if (avg >= 3) {
      badge = '<span class="badge-suitable">適性あり</span>';
      desc  = `${cat}の基礎知識あり。補完的なサポートがあれば対応可能。`;
    } else {
      badge = '<span class="badge-review">要検討</span>';
      desc  = `${cat}専門案件には向いていない。`;
    }
    return `
      <div class="suitability-card">
        <div>
          <div class="suitability-title">${cat}案件</div>
          <div class="suitability-desc">${desc}</div>
        </div>
        ${badge}
      </div>`;
  }).join('');

  // 推薦案件（上位3件）
  const sorted = [...projects].sort((a, b) => b.match_rate - a.match_rate).slice(0, 3);
  document.getElementById('a_projects').innerHTML = sorted.map(p => `
    <div class="assign-project-row">
      <div>
        <div class="assign-proj-id">P${String(p.project_id).padStart(3,'0')}: ${p.project_name}</div>
        <div class="assign-proj-company">${p.company}</div>
      </div>
      <span class="assign-match-badge">${p.match_rate}%</span>
    </div>`).join('');

  // 注意事項
  const notes = [];
  if (user.work_locations) {
    const locs = user.work_locations.split(',').map(s => s.trim()).filter(Boolean);
    if (locs.includes('フルリモート')) notes.push('リモートワーク希望のため、出社必須案件は避ける');
    if (locs.length > 0) notes.push(`希望勤務地: ${locs.join('・')}`);
  }
  if (user.available_from) notes.push(`稼働可能時期: ${user.available_from}`);
  if (user.target_role)    notes.push(`次のキャリアステップとして「${user.target_role}」を志向`);
  if (notes.length === 0)  notes.push('プロフィールを編集して注意事項を設定してください');
  document.getElementById('a_notes').innerHTML = notes.map(n => `<li>${n}</li>`).join('');
}

document.addEventListener('DOMContentLoaded', loadAll);
