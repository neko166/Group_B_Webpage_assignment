/* ==========================================================
   dashboard.js  – エンジニアダッシュボード専用スクリプト
   依存: common.js (openModal, closeModal)
   ========================================================== */

const USER_ID = (window.__INIT_DATA__ || {}).user_id || 1;

// ===== API ヘルパー =====
async function apiFetch(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body !== null) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (method === 'DELETE' && res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error((data && data.detail) || `HTTP ${res.status}`);
  return data;
}

// ===== ユーティリティ =====
function formatMonth(dateStr) {
  if (!dateStr) return '現在';
  const parts = dateStr.split('-');
  if (parts.length >= 2) return `${parts[0]}年${parseInt(parts[1], 10)}月`;
  return dateStr;
}
function toMonthInput(dateStr) { return dateStr ? dateStr.substring(0, 7) : ''; }
function toDateStr(monthInput) { return monthInput ? monthInput + '-01' : null; }

// ===== 初期データ (Jinja2 から埋め込まれた値を取得) =====
let skills   = (window.__INIT_DATA__ || {}).skills   || [];
let careers  = (window.__INIT_DATA__ || {}).careers  || [];
const trainings = (window.__INIT_DATA__ || {}).trainings || [];

let editingSkillId  = null;   // UserSkill.id
let editingCareerId = null;   // CareerHistory.career_id
let confirmCallback = null;
let starLevel       = 3;
let skillMaster     = [];     // Skill master list from API
let chartMode       = 'radar';
let skillFilter     = 'all';

// ===== スキルマスタ読み込み =====
async function loadSkillMaster() {
  try {
    const data = await apiFetch('/users/skills/master');
    if (Array.isArray(data)) {
      skillMaster = data;
      const dl = document.getElementById('skillMasterList');
      if (dl) {
        dl.innerHTML = skillMaster.map(s =>
          `<option value="${s.skill_name}" data-id="${s.skill_id}" data-cat="${s.category || ''}">`
        ).join('');
      }
    }
  } catch (e) {
    console.error('スキルマスタ読み込み失敗', e);
  }
}

// ===== スキル再読み込み =====
async function reloadSkills() {
  try {
    const data = await apiFetch(`/users/${USER_ID}/skills`);
    if (Array.isArray(data)) {
      skills = data;
      renderSkills();
    }
  } catch (e) {
    console.error('スキル再読み込み失敗', e);
  }
}

// ===== 職務経歴再読み込み =====
async function reloadCareers() {
  try {
    const data = await apiFetch(`/users/${USER_ID}/careers`);
    if (Array.isArray(data)) {
      careers = data;
      renderCareers();
    }
  } catch (e) {
    console.error('職務経歴再読み込み失敗', e);
  }
}

// ===== カテゴリ集計 =====
function buildCategoryData() {
  const map = {};
  skills.forEach(s => {
    const cat = s.category || 'その他';
    if (!map[cat]) map[cat] = { total: 0, count: 0 };
    map[cat].total += s.skill_level;
    map[cat].count++;
  });
  return Object.entries(map)
    .map(([name, v]) => ({ name, avg: v.total / v.count, count: v.count }))
    .sort((a, b) => b.avg - a.avg);
}

// ===== スキルKPIサマリー =====
function renderSkillStats() {
  const el = document.getElementById('skillStatsGrid');
  if (!el) return;
  if (skills.length === 0) { el.innerHTML = ''; return; }
  const total = skills.length;
  const avgLevel = (skills.reduce((s, x) => s + x.skill_level, 0) / total).toFixed(1);
  const catData = buildCategoryData();
  const catCount = catData.length;
  const topCat = catData[0] ? catData[0].name : '-';
  el.innerHTML = `
    <div class="stat-card"><div class="stat-val">${total}</div><div class="stat-label">保有スキル数</div></div>
    <div class="stat-card"><div class="stat-val">${avgLevel}</div><div class="stat-label">平均レベル</div></div>
    <div class="stat-card"><div class="stat-val">${catCount}</div><div class="stat-label">カバー領域数</div></div>
    <div class="stat-card"><div class="stat-val" style="font-size:${topCat.length > 8 ? '11px' : '16px'}">${topCat}</div><div class="stat-label">得意領域</div></div>
  `;
}

// ===== チャート切替 =====
function setChartMode(mode) {
  chartMode = mode;
  document.getElementById('tabRadar').classList.toggle('active', mode === 'radar');
  document.getElementById('tabBar').classList.toggle('active', mode === 'bar');
  const radarWrapper = document.querySelector('.radar-wrapper');
  const barWrapper = document.getElementById('barChartWrapper');
  if (radarWrapper) radarWrapper.style.display = mode === 'radar' ? '' : 'none';
  if (barWrapper) barWrapper.style.display = mode === 'bar' ? '' : 'none';
  if (mode === 'radar') { drawRadar(); renderRadarLegend(); }
  else drawSkillBars();
}

// ===== スキル詳細バーチャート =====
function drawSkillBars() {
  const el = document.getElementById('barChartWrapper');
  if (!el) return;
  if (skills.length === 0) {
    el.innerHTML = '<p style="color:var(--gray-light);font-size:13px;padding:16px 0 8px">スキルがありません</p>';
    return;
  }
  const catMap = {};
  skills.forEach(s => {
    const cat = s.category || 'その他';
    if (!catMap[cat]) catMap[cat] = [];
    catMap[cat].push(s);
  });
  Object.values(catMap).forEach(arr => arr.sort((a, b) => b.skill_level - a.skill_level));
  el.innerHTML = Object.entries(catMap).map(([cat, items]) => `
    <div class="bar-group">
      <div class="bar-group-title">${cat}<span class="bar-group-count">${items.length}スキル</span></div>
      ${items.map(s => `
        <div class="bar-row">
          <div class="bar-name" title="${s.skill_name}">${s.skill_name}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${s.skill_level / 5 * 100}%"></div></div>
          <div class="bar-level">Lv.${s.skill_level}</div>
        </div>
      `).join('')}
    </div>
  `).join('');
}

// ===== カテゴリフィルタータブ =====
function renderCatTabs() {
  const el = document.getElementById('catTabs');
  if (!el) return;
  const cats = [...new Set(skills.map(s => s.category || 'その他'))];
  if (cats.length === 0) { el.innerHTML = ''; return; }
  el.innerHTML = [
    `<button class="cat-tab${skillFilter === 'all' ? ' active' : ''}" onclick="setSkillFilter('all')">すべて</button>`,
    ...cats.map(c => `<button class="cat-tab${skillFilter === c ? ' active' : ''}" onclick="setSkillFilter('${c.replace(/'/g, "\\'")}')">${c}</button>`)
  ].join('');
}

function setSkillFilter(cat) {
  skillFilter = cat;
  renderCatTabs();
  renderFilteredSkills();
}

// ===== フィルター適用スキルテーブル描画 =====
function renderFilteredSkills() {
  const filtered = skillFilter === 'all'
    ? skills
    : skills.filter(s => (s.category || 'その他') === skillFilter);
  const sorted = [...filtered].sort((a, b) => b.skill_level - a.skill_level);

  const badge = document.getElementById('skillCount');
  if (badge) badge.textContent = `${skills.length}件`;

  const tbody = document.getElementById('skillTableBody');
  if (!tbody) return;
  tbody.innerHTML = sorted.map(s => `
    <tr>
      <td style="font-weight:600">${s.skill_name}</td>
      <td><span class="skill-category">${s.category || ''}</span></td>
      <td>
        <span class="stars">${'★'.repeat(s.skill_level)}</span><span class="stars-empty">${'★'.repeat(5 - s.skill_level)}</span>
      </td>
      <td>
        <div class="skill-actions">
          <button class="btn btn-sm" onclick="openEditSkill(${s.id})">編集</button>
          <button class="btn btn-sm btn-danger" onclick="confirmDelete('skill',${s.id},'${s.skill_name.replace(/'/g, "\\'")}')">削除</button>
        </div>
      </td>
    </tr>
  `).join('');
}

// ===== 現在ロール =====
async function saveCurrentRole() {
  const v = document.getElementById('currentRoleSelect').value;
  try {
    await apiFetch(`/users/${USER_ID}`, 'PATCH', { current_role: v });
    document.getElementById('currentRoleDisplay').textContent = v;
    closeModal('modalCurrentRole');
  } catch (e) {
    alert('保存に失敗しました: ' + e.message);
  }
}

// ===== 目標ロール =====
async function saveTargetRole() {
  const v = document.getElementById('targetRoleInput').value.trim();
  if (!v) return;
  try {
    await apiFetch(`/users/${USER_ID}`, 'PATCH', { target_role: v });
    document.getElementById('targetRoleDisplay').textContent = v;
    closeModal('modalTargetRole');
  } catch (e) {
    alert('保存に失敗しました: ' + e.message);
  }
}

// ===== 星評価 =====
function setStars(n) {
  starLevel = n;
  document.querySelectorAll('.star-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.val) <= n);
  });
}

// ===== スキル描画 =====
// サーバーJSON: { id, skill_id, skill_name, category, skill_level }
function renderSkills() {
  renderSkillStats();
  renderCatTabs();
  renderFilteredSkills();
  if (chartMode === 'radar') { drawRadar(); renderRadarLegend(); }
  else drawSkillBars();
}

function openAddSkill() {
  editingSkillId = null;
  document.getElementById('skillModalTitle').textContent = 'スキル追加';
  document.getElementById('skillNameInput').value = '';
  document.getElementById('skillNameInput').readOnly = false;
  document.getElementById('skillCategoryHint').textContent = '';
  document.getElementById('skillNameGroup').style.display = '';
  setStars(3);
  openModal('modalSkill');
}

function openEditSkill(id) {
  const s = skills.find(x => x.id === id);
  if (!s) return;
  editingSkillId = id;
  document.getElementById('skillModalTitle').textContent = 'スキル編集';
  document.getElementById('skillNameInput').value = s.skill_name;
  document.getElementById('skillNameInput').readOnly = true;
  document.getElementById('skillCategoryHint').textContent = s.category ? `領域: ${s.category}` : '';
  setStars(s.skill_level);
  openModal('modalSkill');
}

async function saveSkill() {
  const nameInput = document.getElementById('skillNameInput').value.trim();
  if (!nameInput) { alert('スキル名を入力してください'); return; }

  try {
    if (editingSkillId) {
      // 編集: レベルのみ更新
      await apiFetch(`/users/${USER_ID}/skills/${editingSkillId}`, 'PATCH', { skill_level: starLevel });
    } else {
      // 新規: マスタからskill_idを解決。なければ新規マスタ登録
      let master = skillMaster.find(s => s.skill_name === nameInput);
      if (!master) {
        master = await apiFetch('/users/skills/master', 'POST', { skill_name: nameInput, category: null });
        if (master) skillMaster.push(master);
      }
      await apiFetch(`/users/${USER_ID}/skills`, 'POST', { skill_id: master.skill_id, skill_level: starLevel });
    }
    closeModal('modalSkill');
    await reloadSkills();
  } catch (e) {
    alert('保存に失敗しました: ' + e.message);
  }
}

// ===== 職務経歴描画 =====
// サーバーJSON: { career_id, project_name, role, tech_stack(string), period_start, period_end, description }
function renderCareers() {
  const el = document.getElementById('careerList');
  if (careers.length === 0) {
    el.innerHTML = '<p style="color:var(--gray-light);font-size:13px;padding:8px 0">職務経歴がありません</p>';
    return;
  }
  el.innerHTML = careers.map(c => {
    const techArr = c.tech_stack
      ? c.tech_stack.split(',').map(t => t.trim()).filter(Boolean)
      : [];
    return `
    <div class="career-item">
      <div class="career-name">${c.project_name}</div>
      <div class="career-meta">期間：${formatMonth(c.period_start)} 〜 ${formatMonth(c.period_end)}</div>
      <div class="career-meta">役割：${c.role || ''}</div>
      <div class="career-tech">${techArr.map(t => `<span class="tech-tag">${t}</span>`).join('')}</div>
      <div class="career-actions">
        <button class="btn btn-sm" onclick="openCareerDetail(${c.career_id})">詳細</button>
        <button class="btn btn-sm" onclick="openEditCareer(${c.career_id})">編集</button>
        <button class="btn btn-sm btn-danger" onclick="confirmDelete('career',${c.career_id},'${c.project_name.replace(/'/g, "\\'")}')">削除</button>
      </div>
    </div>
  `;
  }).join('');
}

function openAddCareer() {
  editingCareerId = null;
  document.getElementById('careerModalTitle').textContent = '職務経歴 追加';
  ['careerProjectName','careerStart','careerEnd','careerRole','careerTech','careerDesc']
    .forEach(id => document.getElementById(id).value = '');
  openModal('modalCareer');
}

function openEditCareer(id) {
  const c = careers.find(x => x.career_id === id);
  if (!c) return;
  editingCareerId = id;
  document.getElementById('careerModalTitle').textContent = '職務経歴 編集';
  document.getElementById('careerProjectName').value = c.project_name;
  document.getElementById('careerStart').value        = toMonthInput(c.period_start);
  document.getElementById('careerEnd').value          = toMonthInput(c.period_end);
  document.getElementById('careerRole').value         = c.role || '';
  document.getElementById('careerTech').value         = c.tech_stack || '';
  document.getElementById('careerDesc').value         = c.description || '';
  openModal('modalCareer');
}

async function saveCareer() {
  const project_name = document.getElementById('careerProjectName').value.trim();
  if (!project_name) { alert('プロジェクト名を入力してください'); return; }

  const payload = {
    project_name,
    period_start: toDateStr(document.getElementById('careerStart').value),
    period_end:   toDateStr(document.getElementById('careerEnd').value),
    role:         document.getElementById('careerRole').value || null,
    tech_stack:   document.getElementById('careerTech').value || null,
    description:  document.getElementById('careerDesc').value || null,
  };

  try {
    if (editingCareerId) {
      await apiFetch(`/users/${USER_ID}/careers/${editingCareerId}`, 'PATCH', payload);
    } else {
      await apiFetch(`/users/${USER_ID}/careers`, 'POST', payload);
    }
    closeModal('modalCareer');
    await reloadCareers();
  } catch (e) {
    alert('保存に失敗しました: ' + e.message);
  }
}

function openCareerDetail(id) {
  const c = careers.find(x => x.career_id === id);
  if (!c) return;
  const techArr = c.tech_stack
    ? c.tech_stack.split(',').map(t => t.trim()).filter(Boolean)
    : [];
  document.getElementById('careerDetailBody').innerHTML = `
    <div class="detail-row"><span class="detail-label">プロジェクト</span><span class="detail-value">${c.project_name}</span></div>
    <div class="detail-row"><span class="detail-label">期間</span><span class="detail-value">${formatMonth(c.period_start)} 〜 ${formatMonth(c.period_end)}</span></div>
    <div class="detail-row"><span class="detail-label">役割</span><span class="detail-value">${c.role || ''}</span></div>
    <div class="detail-row"><span class="detail-label">使用技術</span><span class="detail-value">${techArr.join(' / ')}</span></div>
    <div class="detail-row"><span class="detail-label">業務概要</span><span class="detail-value">${c.description || ''}</span></div>
  `;
  openModal('modalCareerDetail');
}

// ===== 削除確認 =====
function confirmDelete(type, id, label) {
  document.getElementById('confirmText').textContent = `「${label}」を削除してよろしいですか？`;

  document.getElementById('confirmOkBtn').onclick = async () => {
    try {
      if (type === 'skill') {
        await apiFetch(`/users/${USER_ID}/skills/${id}`, 'DELETE');
        closeModal('modalConfirm');
        await reloadSkills();
      } else {
        await apiFetch(`/users/${USER_ID}/careers/${id}`, 'DELETE');
        closeModal('modalConfirm');
        await reloadCareers();
      }
    } catch (e) {
      alert('削除に失敗しました: ' + e.message);
      closeModal('modalConfirm');
    }
  };

  openModal('modalConfirm');
}

// ===== 研修 =====
// サーバーJSON: { training_id, title, description, target, tags, held_at, location, match }
function renderTrainings() {
  document.getElementById('trainingGrid').innerHTML = trainings.map((t, i) => `
    <div class="training-card">
      <div class="training-rank">${i + 1}</div>
      <div class="training-name">${t.title}</div>
      <div class="training-match">
        <div class="match-bar-bg"><div class="match-bar" style="width:${t.match}%"></div></div>
        <span class="match-pct">${t.match}%</span>
      </div>
      <button class="btn btn-sm" onclick="openTrainingDetail(${t.training_id})">詳細</button>
    </div>
  `).join('');
}

function openTrainingDetail(id) {
  const t = trainings.find(x => x.training_id === id);
  if (!t) return;
  document.getElementById('trainingDetailBody').innerHTML = `
    <div class="detail-row"><span class="detail-label">研修名</span><span class="detail-value" style="font-weight:700">${t.title}</span></div>
    <div class="detail-row"><span class="detail-label">概要</span><span class="detail-value">${t.description}</span></div>
    <div class="detail-row"><span class="detail-label">開催日時</span><span class="detail-value">${t.held_at}</span></div>
    <div class="detail-row"><span class="detail-label">開催場所</span><span class="detail-value">${t.location}</span></div>
    <div class="detail-row"><span class="detail-label">対象者</span><span class="detail-value">${t.target}</span></div>
    <div class="detail-row"><span class="detail-label">マッチ度</span><span class="detail-value" style="color:var(--orange);font-weight:700">${t.match}%</span></div>
  `;
  openModal('modalTrainingDetail');
}

function applyTraining() {
  closeModal('modalTrainingDetail');
  alert('申し込みを受け付けました。社内掲示板の申請システムへ連携します。');
}

// ===== レーダーチャート（カテゴリ平均レベルで描画・スキル数無制限） =====
function drawRadar() {
  const canvas = document.getElementById('radarCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  // カテゴリ集計（最大10カテゴリ）
  const catData = buildCategoryData().slice(0, 10);
  const n = catData.length;

  if (n < 3) {
    ctx.fillStyle = '#bbb';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('3カテゴリ以上のスキルを追加するとチャートが表示されます', W / 2, H / 2);
    return;
  }

  const cx = W / 2, cy = H / 2;
  const maxR = Math.min(cx, cy) - 58;
  const maxLevel = 5;
  const ORANGE        = '#c84b11';
  const ORANGE_STROKE = 'rgba(200,75,17,0.85)';

  const angle = i => (Math.PI * 2 * i / n) - Math.PI / 2;
  const pt    = (i, r) => ({ x: cx + r * Math.cos(angle(i)), y: cy + r * Math.sin(angle(i)) });

  // 外枠背景
  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const p = pt(i, maxR);
    i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
  }
  ctx.closePath();
  ctx.fillStyle = 'rgba(0,0,0,0.025)';
  ctx.fill();

  // グリッドリング
  for (let level = maxLevel; level >= 1; level--) {
    const r = (level / maxLevel) * maxR;
    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const p = pt(i, r);
      i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
    ctx.fillStyle   = level % 2 === 0 ? 'rgba(255,255,255,0.6)' : 'rgba(240,240,240,0.4)';
    ctx.fill();
    ctx.strokeStyle = '#d0d0d0';
    ctx.lineWidth   = 0.8;
    ctx.stroke();
    const lp = pt(0, r);
    ctx.fillStyle    = '#aaa';
    ctx.font         = '9px sans-serif';
    ctx.textAlign    = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(level, lp.x + 6, lp.y + 2);
  }

  // 軸（破線）
  for (let i = 0; i < n; i++) {
    const p = pt(i, maxR);
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(p.x, p.y);
    ctx.strokeStyle = '#bbb';
    ctx.lineWidth   = 0.8;
    ctx.setLineDash([3, 3]);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // 軸交点ティック
  for (let level = 1; level <= maxLevel; level++) {
    const r = (level / maxLevel) * maxR;
    for (let i = 0; i < n; i++) {
      const p = pt(i, r);
      ctx.beginPath();
      ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
      ctx.fillStyle = '#ccc';
      ctx.fill();
    }
  }

  // データポリゴン（カテゴリ平均レベル使用）
  ctx.beginPath();
  catData.forEach((d, i) => {
    const r = (d.avg / maxLevel) * maxR;
    const p = pt(i, r);
    i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
  });
  ctx.closePath();
  const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxR);
  grad.addColorStop(0, 'rgba(200,75,17,0.3)');
  grad.addColorStop(1, 'rgba(200,75,17,0.05)');
  ctx.fillStyle   = grad;
  ctx.fill();
  ctx.strokeStyle = ORANGE_STROKE;
  ctx.lineWidth   = 2.5;
  ctx.lineJoin    = 'round';
  ctx.stroke();

  // データ点
  catData.forEach((d, i) => {
    const r = (d.avg / maxLevel) * maxR;
    const p = pt(i, r);
    ctx.beginPath();
    ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(200,75,17,0.15)';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = ORANGE;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();
  });

  // カテゴリ名ラベル（ピル背景＋スキル件数）
  catData.forEach((d, i) => {
    const a      = angle(i);
    const labelR = maxR + 30;
    const lx     = cx + labelR * Math.cos(a);
    const ly     = cy + labelR * Math.sin(a);
    const label  = d.name.length > 9 ? d.name.slice(0, 8) + '…' : d.name;
    ctx.font     = 'bold 11px sans-serif';
    const tw     = ctx.measureText(label).width;
    const pw = tw + 12, ph = 18;
    ctx.fillStyle = 'rgba(52,52,52,0.88)';
    ctx.beginPath();
    ctx.roundRect(lx - pw / 2, ly - ph / 2, pw, ph, 5);
    ctx.fill();
    ctx.fillStyle    = 'white';
    ctx.textAlign    = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, lx, ly);
    // スキル件数サブテキスト
    ctx.font      = '9px sans-serif';
    ctx.fillStyle = 'rgba(200,75,17,0.9)';
    ctx.fillText(`avg ${d.avg.toFixed(1)} (${d.count}件)`, lx, ly + 14);
  });
}

function renderRadarLegend() {
  const el = document.getElementById('radarLegend');
  if (!el) return;
  const catData = buildCategoryData().slice(0, 10);
  if (catData.length === 0) {
    el.innerHTML = '<span style="font-size:12px;color:var(--gray-light)">スキルを追加するとチャートが表示されます</span>';
    return;
  }
  el.innerHTML = catData.map(d => `
    <div class="legend-item">
      <div class="legend-dot"></div>
      <span style="font-weight:600">${d.name}</span>
      <span class="legend-level">avg ${d.avg.toFixed(1)}</span>
      <span style="font-size:10px;color:var(--gray-light);margin-left:2px">${d.count}件</span>
    </div>
  `).join('');
}

// ===== 初期化 =====
document.addEventListener('DOMContentLoaded', async () => {
  setStars(3);
  renderSkills();
  renderCareers();
  renderTrainings();

  // スキルマスタを非同期で読み込み（スキル追加モーダル用）
  await loadSkillMaster();

  // 目標ロールモーダルを開く前に現在値を pre-fill
  const targetBtn = document.querySelector('[onclick="openModal(\'modalTargetRole\')"]');
  if (targetBtn) {
    targetBtn.onclick = () => {
      document.getElementById('targetRoleInput').value =
        document.getElementById('targetRoleDisplay').textContent;
      openModal('modalTargetRole');
    };
  }

  // スキル名入力時にカテゴリヒントを表示
  const skillInput = document.getElementById('skillNameInput');
  if (skillInput) {
    skillInput.addEventListener('input', () => {
      const matched = skillMaster.find(s => s.skill_name === skillInput.value);
      const hint = document.getElementById('skillCategoryHint');
      if (hint) hint.textContent = matched && matched.category ? `領域: ${matched.category}` : '';
    });
  }
});
