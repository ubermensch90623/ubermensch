// harness Drill Store v3 — NCS 수리능력 회독 엔진 (P12 HYBRID 판정 반영)
// 좌: 도메인 tree (기초연산·도표분석·기초통계)
// 중: drill 패널 (문제·선지·즉시채점·오답 2분류 + 풀이해설)
// 우: 진도·오답노트·별표

document.addEventListener('alpine:init', () => {
  Alpine.data('harness', () => ({
    // ── raw state ──
    items: [],
    history: [],
    starred: [],
    stats: {},
    // ── UI state ──
    currentCard: null,
    selected: null,
    submitted: false,
    showCardViewer: true,
    filter: 'drillable',
    search: '',
    expandedDomains: {},
    footerStatus: 'booting',

    async boot() {
      await Promise.all([this.loadItems(), this.loadProgress()]);
      this.bindKeys();
      this.footerStatus = `ready · NCS 수리 ${this.items.length}제 · 정답률 ${((this.stats.accuracy||0)*100).toFixed(0)}%`;
      const first = this.items.find(i => i.drillable);
      if (first) this.openCard(first);
      // 도메인 전체 펼쳐두기 (초기)
      for (const d of Object.keys(this.itemsByDomain)) this.expandedDomains[d] = true;
    },

    async loadItems() {
      try {
        const r = await fetch('/api/drill/items');
        if (r.ok) {
          const j = await r.json();
          this.items = j.items || [];
        }
      } catch (e) { this.footerStatus = 'items 로드 실패'; }
    },

    async loadProgress() {
      try {
        const r = await fetch('/api/progress');
        if (r.ok) {
          const j = await r.json();
          this.history = j.history || [];
          this.starred = j.starred || [];
          this.stats = j.stats || {};
        }
      } catch (_) {}
    },

    async _post(body) {
      try {
        const r = await fetch('/api/progress', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(body),
        });
        if (r.ok) {
          const j = await r.json();
          this.stats = j.stats || this.stats;
          await this.loadProgress();
        }
      } catch (e) { this.footerStatus = '저장 실패'; }
    },

    async saveAttempt(classification) {
      if (!this.currentCard || this.selected == null) return;
      const correct = this.currentCard.correct_index;
      const is_correct = this.selected === correct;
      await this._post({
        action: 'attempt',
        card_id: this.currentCard.id,
        selected: this.selected,
        correct: correct,
        is_correct: is_correct,
        classification: is_correct ? null : (classification || 'unknown'),
      });
    },

    async toggleStar() {
      if (!this.currentCard) return;
      const cur = this.currentCardStarLevel;
      const next = (cur + 1) % 4; // 0→1→2→3→0
      await this._post({action:'star', card_id:this.currentCard.id, level:next});
    },

    // ── derived ──
    get drillableCount() { return this.items.filter(i => i.drillable).length; },
    get readonlyCount() { return this.items.filter(i => !i.drillable).length; },

    get wrongIdSet() {
      const s = new Set();
      for (const h of this.history) if (h.is_correct === false) s.add(h.card_id);
      return s;
    },
    get starredIdSet() { return new Set(this.starred.map(s => s.card_id)); },
    get attemptedIdSet() {
      const s = new Set();
      for (const h of this.history) s.add(h.card_id);
      return s;
    },

    get filteredItems() {
      let arr = this.items;
      if (this.filter === 'drillable') arr = arr.filter(i => i.drillable);
      else if (this.filter === 'readonly') arr = arr.filter(i => !i.drillable);
      else if (this.filter === 'starred') arr = arr.filter(i => this.starredIdSet.has(i.id));
      else if (this.filter === 'wrong') arr = arr.filter(i => this.wrongIdSet.has(i.id));
      else if (this.filter === 'untouched') arr = arr.filter(i => i.drillable && !this.attemptedIdSet.has(i.id));
      if (this.search.trim()) {
        const q = this.search.toLowerCase();
        arr = arr.filter(i => (i.title + ' ' + i.subtopic + ' ' + (i.question||'')).toLowerCase().includes(q));
      }
      return arr;
    },

    get itemsByDomain() {
      const byDom = {};
      for (const it of this.filteredItems) {
        const d = it.domain || '미분류';
        if (!byDom[d]) byDom[d] = [];
        byDom[d].push(it);
      }
      return byDom;
    },

    get currentCardHistory() {
      if (!this.currentCard) return [];
      return this.history.filter(h => h.card_id === this.currentCard.id);
    },
    get currentCardStarLevel() {
      if (!this.currentCard) return 0;
      const s = this.starred.find(x => x.card_id === this.currentCard.id);
      return s ? s.level : 0;
    },

    statusOf(item) {
      const attempts = this.history.filter(h => h.card_id === item.id);
      if (!attempts.length) return 'new';
      const lastOk = attempts[attempts.length - 1].is_correct;
      return lastOk ? 'ok' : 'wrong';
    },

    // ── actions ──
    openCard(item) {
      this.currentCard = item;
      this.selected = null;
      this.submitted = false;
    },
    select(n) {
      if (!this.currentCard || !this.currentCard.drillable) return;
      if (this.submitted) return;
      this.selected = n;
    },
    async submit() {
      if (!this.currentCard || !this.currentCard.drillable) return;
      if (this.selected == null) return;
      this.submitted = true;
      const ok = this.selected === this.currentCard.correct_index;
      if (ok) await this.saveAttempt();
      // 오답이면 사용자가 classify 선택
    },
    async classify(type) {
      await this.saveAttempt(type);
    },
    clearSelection() {
      this.selected = null;
      this.submitted = false;
    },
    next() {
      const arr = this.filteredItems.filter(i => i.drillable);
      if (!arr.length) return;
      const idx = arr.findIndex(i => i.id === (this.currentCard && this.currentCard.id));
      this.openCard(arr[(idx + 1) % arr.length]);
    },
    prev() {
      const arr = this.filteredItems.filter(i => i.drillable);
      if (!arr.length) return;
      const idx = arr.findIndex(i => i.id === (this.currentCard && this.currentCard.id));
      this.openCard(arr[(idx - 1 + arr.length) % arr.length]);
    },
    toggleDomain(d) { this.expandedDomains[d] = !this.expandedDomains[d]; },
    setFilter(f) { this.filter = f; },

    bindKeys() {
      document.addEventListener('keydown', (e) => {
        const t = e.target && e.target.tagName;
        if (t === 'INPUT' || t === 'TEXTAREA') return;
        if (['1','2','3','4','5'].includes(e.key)) { this.select(parseInt(e.key,10)); }
        else if (e.key === 'Enter') { if (!this.submitted) this.submit(); }
        else if (e.key === ' ') { e.preventDefault(); this.clearSelection(); }
        else if (e.key === 'j' || e.key === 'J' || e.key === 'ArrowDown') { this.next(); }
        else if (e.key === 'k' || e.key === 'K' || e.key === 'ArrowUp') { this.prev(); }
        else if (e.key === 'v' || e.key === 'V') { this.showCardViewer = !this.showCardViewer; }
        else if (e.key === '*') { this.toggleStar(); }
      });
    },
  }));
});
