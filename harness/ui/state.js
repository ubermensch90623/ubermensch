// harness Alpine.js store — 로컬 전용 stdlib 서버 API 연동
document.addEventListener('alpine:init', () => {
  Alpine.data('harness', () => ({
    // state
    agencies: ['캠코', '수협', '신보', '주금공'],
    currentAgency: '캠코',
    currentArea: null,
    score: { overall_rate: 0, agencies: [] },
    lineage: [],
    restored: [],
    cards: [],
    predictions: [],
    panels: { left: true, right: true },
    drillHtml: '',
    footerStatus: 'idle',

    async boot() {
      await Promise.all([
        this.refreshScore(),
        this.refreshLineage(),
        this.refreshRestored(),
        this.refreshCards(),
        this.refreshPredictions(),
      ]);
      this.bindKeys();
      this.applyResponsive();
      window.addEventListener('resize', () => this.applyResponsive());
      this.footerStatus = `ready · 해설카드 ${this.cards.length} · 예상문항 ${this.predictions.length}`;
    },

    async refreshCards() {
      try {
        const r = await fetch('/api/cards/catalog');
        if (r.ok) {
          const j = await r.json();
          this.cards = j.cards || [];
        }
      } catch (_) {}
    },

    async refreshPredictions() {
      try {
        const r = await fetch('/api/predictions');
        if (r.ok) {
          const j = await r.json();
          this.predictions = j.questions || [];
        }
      } catch (_) {}
    },

    applyResponsive() {
      const w = window.innerWidth;
      if (w < 768) { this.panels.left = false; this.panels.right = false; }
      else if (w < 1280) { this.panels.left = false; this.panels.right = true; }
      else { this.panels.left = true; this.panels.right = true; }
    },

    async refreshScore() {
      try {
        const r = await fetch('/api/score');
        if (r.ok) {
          const j = await r.json();
          j.agencies.forEach(m => {
            m.areas = Object.entries(m.cells || {}).map(([name, c]) => ({
              name, restored: c.restored || 0, target: c.target || 0, rate: c.rate || 0
            }));
          });
          this.score = j;
        }
      } catch (_) { this.footerStatus = 'score fetch 실패'; }
    },

    async refreshLineage() {
      try {
        const r = await fetch('/api/lineage');
        if (r.ok) this.lineage = (await r.json()).entries || [];
      } catch (_) { /* 무시 */ }
    },

    async refreshRestored() {
      try {
        const r = await fetch('/api/claims/restored');
        if (r.ok) this.restored = (await r.json()).records || [];
      } catch (_) { /* 무시 */ }
    },

    setAgency(a) {
      this.currentAgency = a;
      this.currentArea = null;
      this.drillHtml = '';
    },

    setArea(area) {
      this.currentArea = area;
      // M4 에서 drill_card.html 템플릿 로드 + 데이터 바인딩 완성
      this.drillHtml = `<div class="box blue"><p>영역 선택: <b>${area}</b></p>`
        + `<p class="text-sm mt-2" style="color: var(--text-secondary);">`
        + `복원된 실제 기출 문항이 도착하면 8단계 drill card 로 교체됩니다.</p></div>`;
    },

    togglePanel(side) {
      this.panels[side] = !this.panels[side];
    },

    globalRate() {
      const ags = this.score.agencies || [];
      if (!ags.length) return 0;
      let r = 0, t = 0;
      ags.forEach(m => { r += (m.total_restored || 0); t += (m.total_target || 0); });
      return t ? (r / t) : 0;
    },

    get cardsForArea() {
      if (!this.currentArea) return [];
      // subtopic 이나 domain 또는 이름에 currentArea 포함
      const key = this.currentArea.toLowerCase();
      return (this.cards || []).filter(c => {
        const hay = ((c.subtopic||'') + ' ' + (c.domain||'') + ' ' + (c.filename||'') + ' ' + (c.title||'')).toLowerCase();
        return hay.includes(key);
      });
    },

    openPrediction(q) {
      this.drillHtml = this.renderPrediction(q);
    },

    renderPrediction(q) {
      const choices = (q.choices||[]).map((ch, i) => `<li class="mb-1">${ch}</li>`).join('');
      const steps = (q.explanation_steps||[]).map(s => `<li>${s}</li>`).join('');
      const triggers = (q.trigger_words||[]).map(t => `<span class="trigger">${t}</span>`).join(' ');
      return `<article class="drill-card">
        <div class="step-title font-bold mb-2" style="color:var(--text-accent);">${q.id} · ${q.domain} · ${q.topic||''}</div>
        <p class="mb-3">${q.question_text||''}</p>
        <ol class="mb-3">${choices}</ol>
        <div class="box blue"><strong>정답:</strong> ${q.correct_index}</div>
        <div class="mt-3"><strong>트리거:</strong> ${triggers}</div>
        <div class="mt-3"><strong>해설 8단계:</strong><ol class="list-decimal list-inside">${steps}</ol></div>
        <div class="box warn mt-3"><strong>약점 힌트:</strong> ${q.weakness_hint||''}</div>
      </article>`;
    },

    get currentMatrix() {
      const m = (this.score.agencies || []).find(a => a.agency === this.currentAgency);
      return m || { agency: this.currentAgency, areas: [] };
    },

    get restoredEmpty() {
      return (this.restored || []).length === 0;
    },

    heatClass(rate) {
      if (rate >= 0.90) return 'heat-green text-xs px-2 rounded';
      if (rate >= 0.70) return 'heat-amber text-xs px-2 rounded';
      return 'heat-red text-xs px-2 rounded';
    },

    stageClass(stage) {
      const ok = ['restored', 'sc_reviewed', 'p12_approved'];
      const bad = ['quarantined', 'reset'];
      if (ok.includes(stage)) return 'text-xs pill';
      if (bad.includes(stage)) return 'text-xs';
      return 'text-xs';
    },

    layoutClass() {
      const l = this.panels.left, r = this.panels.right;
      if (l && r) return 'grid-cols-[320px_1fr_360px]';
      if (l && !r) return 'grid-cols-[320px_1fr]';
      if (!l && r) return 'grid-cols-[1fr_360px]';
      return 'grid-cols-1';
    },

    bindKeys() {
      document.addEventListener('keydown', (e) => {
        if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
        if (e.key === '[') { this.togglePanel('left'); }
        else if (e.key === ']') { this.togglePanel('right'); }
        else if (e.key === 'j' || e.key === 'J') { this.nextArea(1); }
        else if (e.key === 'k' || e.key === 'K') { this.nextArea(-1); }
        else if (e.key === ' ') { e.preventDefault(); this.clearSelection(); }
      });
    },

    nextArea(step) {
      const areas = this.currentMatrix.areas || [];
      if (!areas.length) return;
      const idx = areas.findIndex(a => a.name === this.currentArea);
      const next = (idx + step + areas.length) % areas.length;
      this.setArea(areas[next].name);
    },

    clearSelection() {
      // drill 내부 답 선택 해제 — drill card 탑재 후 실구현
      this.footerStatus = 'selection cleared';
      setTimeout(() => this.footerStatus = 'ready', 800);
    },
  }));
});
