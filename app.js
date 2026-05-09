/* Ubermensch — 능동적 회상 + Leitner 학습 SPA
 * 단일 IIFE, ES 모듈 미사용 (file:// 호환)
 */
(function () {
  'use strict';

  // ============================================================
  // 1. 상수 & 유틸
  // ============================================================
  const LS_KEY = 'ubermensch.state.v1';
  const BOX_INTERVALS = { 1: 1, 2: 3, 3: 7, 4: 14, 5: 30 };
  const DEFAULT_SETTINGS = {
    autoKeywordMinLen: 2,
    clozeBlanksPerCard: 1,
    dailyNewLimit: 20,
  };

  function uid() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
      return window.crypto.randomUUID();
    }
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
  }

  function todayISO() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }

  function addDaysISO(iso, n) {
    const d = new Date(iso + 'T00:00:00');
    d.setDate(d.getDate() + n);
    return todayISOFromDate(d);
  }

  function todayISOFromDate(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }

  function nowISO() {
    return new Date().toISOString();
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function debounce(fn, ms) {
    let t = null;
    return function () {
      const args = arguments;
      const ctx = this;
      if (t) clearTimeout(t);
      t = setTimeout(() => fn.apply(ctx, args), ms);
    };
  }

  function normalize(s) {
    if (s == null) return '';
    return String(s).normalize('NFC').toLowerCase();
  }

  // ============================================================
  // 2. Store (localStorage 영속화)
  // ============================================================
  const Store = (function () {
    function blank() {
      return {
        version: 1,
        decks: {},
        notes: {},
        cards: {},
        settings: { ...DEFAULT_SETTINGS },
        meta: { createdAt: nowISO(), lastOpenedAt: nowISO() },
      };
    }

    function load() {
      try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return blank();
        const parsed = JSON.parse(raw);
        if (!parsed || parsed.version !== 1) {
          console.warn('Unknown state version, resetting.');
          return blank();
        }
        parsed.settings = { ...DEFAULT_SETTINGS, ...(parsed.settings || {}) };
        parsed.meta = parsed.meta || { createdAt: nowISO(), lastOpenedAt: nowISO() };
        parsed.meta.lastOpenedAt = nowISO();
        return parsed;
      } catch (e) {
        console.error('Failed to load state', e);
        return blank();
      }
    }

    function save(state) {
      try {
        localStorage.setItem(LS_KEY, JSON.stringify(state));
      } catch (e) {
        alert('저장 실패: ' + e.message);
      }
    }

    function exportJSON(state) {
      const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ubermensch-${todayISO()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    function importJSON(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function () {
          try {
            const parsed = JSON.parse(reader.result);
            if (!parsed || parsed.version !== 1) {
              return reject(new Error('지원하지 않는 형식입니다.'));
            }
            resolve(parsed);
          } catch (e) {
            reject(e);
          }
        };
        reader.onerror = () => reject(reader.error);
        reader.readAsText(file);
      });
    }

    function reset() {
      return blank();
    }

    return { load, save, exportJSON, importJSON, reset };
  })();

  // ============================================================
  // 3. 도메인 로직
  // ============================================================

  // 클로즈 마크업 파싱: {{...}} 또는 **...**
  function parseCloze(body) {
    const tokens = [];
    if (!body) return { raw: body || '', tokens };
    const re = /\{\{([^{}]+)\}\}|\*\*([^*]+)\*\*/g;
    const counts = Object.create(null);
    let m;
    while ((m = re.exec(body)) !== null) {
      const tok = (m[1] || m[2]).trim();
      if (!tok) continue;
      const idx = counts[tok] || 0;
      counts[tok] = idx + 1;
      tokens.push({
        token: tok,
        index: idx,
        start: m.index,
        end: m.index + m[0].length,
        kind: m[1] != null ? 'cloze' : 'emph',
      });
    }
    return { raw: body, tokens };
  }

  // 본문에서 마크업을 제거한 평문 (퀴즈 표시용)
  function plainBody(body) {
    if (!body) return '';
    return body
      .replace(/\{\{([^{}]+)\}\}/g, '$1')
      .replace(/\*\*([^*]+)\*\*/g, '$1');
  }

  function clozeKey(token, index) {
    return `cloze::${token}::${index}`;
  }

  function generateClozeCards(state, noteId) {
    const note = state.notes[noteId];
    if (!note) return { added: 0, archived: 0 };

    const parsed = parseCloze(note.body);
    const wantedKeys = new Set(parsed.tokens.map((t) => clozeKey(t.token, t.index)));

    // 기존 클로즈 카드 점검: 사라진 토큰은 archived 처리
    let archived = 0;
    for (const cid of note.cardIds) {
      const c = state.cards[cid];
      if (!c || c.kind !== 'cloze' || c.archived) continue;
      const k = clozeKey(c.ref.token, c.ref.index);
      if (!wantedKeys.has(k)) {
        c.archived = true;
        archived++;
      }
    }

    // 기존 키 집합 (archived 포함, dedup용)
    const existingKeys = new Set(
      note.cardIds
        .map((cid) => state.cards[cid])
        .filter((c) => c && c.kind === 'cloze')
        .map((c) => clozeKey(c.ref.token, c.ref.index)),
    );

    let added = 0;
    for (const t of parsed.tokens) {
      const k = clozeKey(t.token, t.index);
      if (existingKeys.has(k)) continue;
      const card = {
        id: uid(),
        noteId: note.id,
        kind: 'cloze',
        ref: { type: 'cloze', token: t.token, index: t.index },
        box: 1,
        nextDue: todayISO(),
        lastReviewed: null,
        history: [],
        createdAt: nowISO(),
      };
      state.cards[card.id] = card;
      note.cardIds.push(card.id);
      existingKeys.add(k);
      added++;
    }
    note.updatedAt = nowISO();
    return { added, archived };
  }

  function extractKeywords(note) {
    const set = new Set();
    if (note.keywords) note.keywords.forEach((k) => k && set.add(k.trim()));
    const parsed = parseCloze(note.body || '');
    parsed.tokens.forEach((t) => set.add(t.token));
    return Array.from(set).filter(Boolean);
  }

  function scoreRecall(note, typed) {
    const keywords = extractKeywords(note);
    const typedN = normalize(typed);
    const typedNoWs = typedN.replace(/\s+/g, '');
    const hits = [];
    const misses = [];
    const hitRanges = [];
    const seen = new Set();
    for (const kw of keywords) {
      if (seen.has(kw)) continue;
      seen.add(kw);
      const kwN = normalize(kw);
      const kwNoWs = kwN.replace(/\s+/g, '');
      let idx = typedN.indexOf(kwN);
      if (idx >= 0) {
        hits.push(kw);
        hitRanges.push([idx, idx + kwN.length]);
      } else if (kwNoWs && typedNoWs.indexOf(kwNoWs) >= 0) {
        hits.push(kw);
      } else {
        misses.push(kw);
      }
    }
    const total = keywords.length;
    const score = total === 0 ? 0 : Math.round((100 * hits.length) / total);
    return { score, hits, misses, hitRanges, total, keywords };
  }

  function srsGradeCard(card, result, score) {
    const today = todayISO();
    const newBox = result === 'correct' ? Math.min(5, card.box + 1) : 1;
    const interval = BOX_INTERVALS[newBox];
    const updated = {
      ...card,
      box: newBox,
      nextDue: addDaysISO(today, interval),
      lastReviewed: today,
      history: card.history.concat([
        { date: today, result, score: typeof score === 'number' ? score : undefined },
      ]),
    };
    return updated;
  }

  function dueCards(state, isoToday) {
    const today = isoToday || todayISO();
    return Object.values(state.cards)
      .filter((c) => !c.archived && c.nextDue <= today)
      .sort((a, b) => {
        if (a.box !== b.box) return a.box - b.box;
        if (a.nextDue !== b.nextDue) return a.nextDue < b.nextDue ? -1 : 1;
        return 0;
      });
  }

  function dueByDeck(state, deckId, isoToday) {
    const today = isoToday || todayISO();
    return Object.values(state.cards).filter((c) => {
      if (c.archived) return false;
      const note = state.notes[c.noteId];
      return note && note.deckId === deckId && c.nextDue <= today;
    });
  }

  function notesInDeck(state, deckId) {
    const deck = state.decks[deckId];
    if (!deck) return [];
    return deck.noteIds.map((id) => state.notes[id]).filter(Boolean);
  }

  function activeCardsForNote(state, noteId) {
    const note = state.notes[noteId];
    if (!note) return [];
    return note.cardIds.map((id) => state.cards[id]).filter((c) => c && !c.archived);
  }

  // ============================================================
  // 4. State 변경 헬퍼
  // ============================================================
  let state = Store.load();
  let reviewQueue = []; // 세션 내 복습 진행용
  let editorDraft = null; // 노트 에디터 진행 중 드래프트 (키워드, QA)

  function persist() {
    Store.save(state);
  }

  function rerender() {
    Router.handle();
  }

  function addDeck(name, description) {
    const deck = {
      id: uid(),
      name: (name || '').trim(),
      description: (description || '').trim(),
      createdAt: nowISO(),
      noteIds: [],
    };
    if (!deck.name) return null;
    state.decks[deck.id] = deck;
    persist();
    return deck;
  }

  function updateDeck(id, patch) {
    const d = state.decks[id];
    if (!d) return;
    Object.assign(d, patch);
    persist();
  }

  function deleteDeck(id) {
    const d = state.decks[id];
    if (!d) return;
    for (const nid of d.noteIds.slice()) deleteNote(nid, true);
    delete state.decks[id];
    persist();
  }

  function addNote(deckId, data) {
    const deck = state.decks[deckId];
    if (!deck) return null;
    const note = {
      id: uid(),
      deckId,
      title: (data.title || '').trim(),
      body: data.body || '',
      keywords: Array.isArray(data.keywords) ? data.keywords.filter(Boolean) : [],
      qaPairs: [],
      cardIds: [],
      createdAt: nowISO(),
      updatedAt: nowISO(),
    };
    if (!note.title) return null;

    state.notes[note.id] = note;
    deck.noteIds.push(note.id);

    // recall 카드 생성
    const recallCard = {
      id: uid(),
      noteId: note.id,
      kind: 'recall',
      ref: { type: 'recall' },
      box: 1,
      nextDue: todayISO(),
      lastReviewed: null,
      history: [],
      createdAt: nowISO(),
    };
    state.cards[recallCard.id] = recallCard;
    note.cardIds.push(recallCard.id);

    // QA 페어 처리
    if (Array.isArray(data.qaPairs)) {
      for (const qa of data.qaPairs) {
        if (!qa || !qa.question || !qa.answer) continue;
        const pair = { id: uid(), question: qa.question.trim(), answer: qa.answer.trim() };
        note.qaPairs.push(pair);
        const qaCard = {
          id: uid(),
          noteId: note.id,
          kind: 'qa',
          ref: { type: 'qa', qaPairId: pair.id },
          box: 1,
          nextDue: todayISO(),
          lastReviewed: null,
          history: [],
          createdAt: nowISO(),
        };
        state.cards[qaCard.id] = qaCard;
        note.cardIds.push(qaCard.id);
      }
    }
    persist();
    return note;
  }

  function updateNote(id, patch) {
    const note = state.notes[id];
    if (!note) return;
    if (typeof patch.title === 'string') note.title = patch.title.trim();
    if (typeof patch.body === 'string') note.body = patch.body;
    if (Array.isArray(patch.keywords)) note.keywords = patch.keywords.filter(Boolean);
    note.updatedAt = nowISO();
    persist();
  }

  function deleteNote(id, skipDeckCleanup) {
    const note = state.notes[id];
    if (!note) return;
    for (const cid of note.cardIds) delete state.cards[cid];
    delete state.notes[id];
    if (!skipDeckCleanup) {
      const deck = state.decks[note.deckId];
      if (deck) deck.noteIds = deck.noteIds.filter((x) => x !== id);
    }
    persist();
  }

  function addQAPair(noteId, question, answer) {
    const note = state.notes[noteId];
    if (!note) return null;
    if (!question || !answer) return null;
    const pair = { id: uid(), question: question.trim(), answer: answer.trim() };
    note.qaPairs.push(pair);
    const card = {
      id: uid(),
      noteId,
      kind: 'qa',
      ref: { type: 'qa', qaPairId: pair.id },
      box: 1,
      nextDue: todayISO(),
      lastReviewed: null,
      history: [],
      createdAt: nowISO(),
    };
    state.cards[card.id] = card;
    note.cardIds.push(card.id);
    note.updatedAt = nowISO();
    persist();
    return pair;
  }

  function deleteQAPair(noteId, pairId) {
    const note = state.notes[noteId];
    if (!note) return;
    note.qaPairs = note.qaPairs.filter((p) => p.id !== pairId);
    // 연관 카드 archive
    for (const cid of note.cardIds) {
      const c = state.cards[cid];
      if (c && c.kind === 'qa' && c.ref.qaPairId === pairId) c.archived = true;
    }
    note.updatedAt = nowISO();
    persist();
  }

  function gradeCard(cardId, result, score) {
    const c = state.cards[cardId];
    if (!c) return;
    state.cards[cardId] = srsGradeCard(c, result, score);
    persist();
  }

  // ============================================================
  // 5. Router
  // ============================================================
  const Router = (function () {
    const routes = [
      { pattern: /^#?\/?$/, view: () => renderDashboard() },
      { pattern: /^#\/deck\/([^/]+)$/, view: (m) => renderDeck(m[1]) },
      { pattern: /^#\/note\/new\/([^/]+)$/, view: (m) => renderNoteEditor(null, m[1]) },
      { pattern: /^#\/note\/([^/]+)$/, view: (m) => renderNoteEditor(m[1]) },
      { pattern: /^#\/recall\/([^/]+)$/, view: (m) => renderRecall(m[1]) },
      { pattern: /^#\/quiz\/([^/]+)$/, view: (m) => renderQuiz(m[1]) },
      { pattern: /^#\/review$/, view: () => renderReview() },
      { pattern: /^#\/settings$/, view: () => renderSettings() },
    ];

    function handle() {
      const hash = location.hash || '#/';
      // 노트 에디터가 아니면 드래프트 폐기
      if (!/^#\/note\//.test(hash)) editorDraft = null;
      for (const r of routes) {
        const m = hash.match(r.pattern);
        if (m) {
          try {
            r.view(m);
          } catch (e) {
            console.error(e);
            renderError(e);
          }
          window.scrollTo(0, 0);
          return;
        }
      }
      // 매칭 없음 → 대시보드로
      location.hash = '#/';
    }

    function go(hash) {
      if (location.hash === hash) {
        handle();
      } else {
        location.hash = hash;
      }
    }

    return { handle, go };
  })();

  // ============================================================
  // 6. 뷰
  // ============================================================
  const $app = document.getElementById('app');

  function setApp(html) {
    $app.innerHTML = html;
  }

  function renderError(e) {
    setApp(
      `<div class="banner warn"><strong>오류:</strong> ${escapeHtml(
        e && e.message ? e.message : String(e),
      )}</div><p><a href="#/">대시보드로</a></p>`,
    );
  }

  function crumbs(items) {
    return (
      '<div class="crumbs">' +
      items
        .map((it, i) => {
          if (it.href && i < items.length - 1)
            return `<a href="${it.href}">${escapeHtml(it.label)}</a>`;
          return escapeHtml(it.label);
        })
        .join(' / ') +
      '</div>'
    );
  }

  function badgeForBox(box) {
    return `<span class="badge box-${box}">박스 ${box}</span>`;
  }

  // ---------- 대시보드 ----------
  function renderDashboard() {
    const due = dueCards(state);
    const decks = Object.values(state.decks).sort((a, b) =>
      a.createdAt < b.createdAt ? -1 : 1,
    );
    const totalNotes = Object.keys(state.notes).length;
    const totalCards = Object.values(state.cards).filter((c) => !c.archived).length;

    let html = `
      <section class="hero">
        <div>
          <div style="color:var(--fg-dim);font-size:0.9rem;">오늘 복습 카드</div>
          <div class="big-number">${due.length}</div>
        </div>
        <div class="actions">
          <button class="btn primary" data-action="start-review" ${
            due.length === 0 ? 'disabled' : ''
          }>오늘 복습 시작</button>
          <button class="btn" data-action="new-deck">+ 새 덱</button>
        </div>
      </section>

      <div class="stats">
        <div class="stat"><div class="label">덱</div><div class="val">${decks.length}</div></div>
        <div class="stat"><div class="label">노트</div><div class="val">${totalNotes}</div></div>
        <div class="stat"><div class="label">활성 카드</div><div class="val">${totalCards}</div></div>
      </div>

      <h2>덱</h2>
    `;

    if (decks.length === 0) {
      html += `
        <div class="empty">
          <p>아직 덱이 없습니다.</p>
          <p>"+ 새 덱"을 눌러 과목을 만드세요. (예: 헌법, 행정법, 영단어)</p>
          <button class="btn primary" data-action="new-deck">+ 새 덱 만들기</button>
        </div>`;
    } else {
      html += '<div class="cards">';
      for (const d of decks) {
        const dueN = dueByDeck(state, d.id).length;
        const noteN = d.noteIds.length;
        html += `
          <div class="card">
            <h3>${escapeHtml(d.name)}</h3>
            <div class="meta">노트 ${noteN}개${
          dueN > 0 ? ` · <span class="badge due">복습 ${dueN}</span>` : ''
        }</div>
            ${
              d.description
                ? `<div class="meta">${escapeHtml(d.description)}</div>`
                : ''
            }
            <div class="actions">
              <a class="btn sm" href="#/deck/${d.id}">열기</a>
            </div>
          </div>`;
      }
      html += '</div>';
    }

    setApp(html);
  }

  // ---------- 덱 상세 ----------
  function renderDeck(deckId) {
    const deck = state.decks[deckId];
    if (!deck) {
      renderError(new Error('덱을 찾을 수 없습니다.'));
      return;
    }
    const notes = notesInDeck(state, deckId);
    const dueN = dueByDeck(state, deckId).length;

    let html =
      crumbs([{ label: '대시보드', href: '#/' }, { label: deck.name }]) +
      `
      <div class="row">
        <h1 style="margin:0;">${escapeHtml(deck.name)}</h1>
        ${dueN > 0 ? `<span class="badge due">복습 ${dueN}</span>` : ''}
        <div class="spacer"></div>
        <button class="btn sm" data-action="rename-deck" data-id="${deck.id}">이름 수정</button>
        <button class="btn sm" data-action="delete-deck" data-id="${deck.id}">덱 삭제</button>
      </div>
      ${
        deck.description
          ? `<p style="color:var(--fg-dim);">${escapeHtml(deck.description)}</p>`
          : ''
      }
      <div class="row" style="margin-top:0.5rem;">
        <a class="btn primary" href="#/note/new/${deck.id}">+ 새 노트</a>
        ${
          dueN > 0
            ? `<button class="btn" data-action="start-review-deck" data-id="${deck.id}">이 덱만 복습</button>`
            : ''
        }
      </div>
      <h2>노트</h2>
    `;

    if (notes.length === 0) {
      html += `<div class="empty"><p>아직 노트가 없습니다. 첫 개념을 적어보세요.</p></div>`;
    } else {
      html += '<div class="cards">';
      for (const n of notes) {
        const cards = activeCardsForNote(state, n.id);
        const dueOnNote = cards.filter((c) => c.nextDue <= todayISO()).length;
        html += `
          <div class="card">
            <h3>${escapeHtml(n.title)}</h3>
            <div class="meta">카드 ${cards.length}개${
          dueOnNote > 0 ? ` · <span class="badge due">복습 ${dueOnNote}</span>` : ''
        }</div>
            <div class="actions">
              <a class="btn sm" href="#/note/${n.id}">열기</a>
            </div>
          </div>`;
      }
      html += '</div>';
    }

    setApp(html);
  }

  // ---------- 노트 에디터 ----------
  function renderNoteEditor(noteId, deckIdForNew) {
    const isNew = !noteId;
    const note = isNew ? null : state.notes[noteId];
    if (!isNew && !note) {
      renderError(new Error('노트를 찾을 수 없습니다.'));
      return;
    }
    const deckId = isNew ? deckIdForNew : note.deckId;
    const deck = state.decks[deckId];
    if (!deck) {
      renderError(new Error('덱을 찾을 수 없습니다.'));
      return;
    }

    const title = note ? note.title : '';
    const body = note ? note.body : '';
    const keywords = note ? note.keywords.slice() : [];
    const qaPairs = note ? note.qaPairs.slice() : [];

    let html =
      crumbs([
        { label: '대시보드', href: '#/' },
        { label: deck.name, href: `#/deck/${deck.id}` },
        { label: isNew ? '새 노트' : title || '(제목 없음)' },
      ]) +
      `
      <h1>${isNew ? '새 노트' : '노트 수정'}</h1>
      <form id="note-form">
        <label for="f-title">개념 제목</label>
        <input type="text" id="f-title" required value="${escapeHtml(title)}" placeholder="예: 법치주의" />

        <label for="f-body">개념 설명 (파인만식: 초등학생도 이해할 수 있게)</label>
        <div class="editor-toolbar">
          <button type="button" class="btn sm" data-action="wrap" data-pre="{{" data-post="}}">{{빈칸}}</button>
          <button type="button" class="btn sm" data-action="wrap" data-pre="**" data-post="**">**강조**</button>
        </div>
        <textarea id="f-body" class="mono" placeholder="본문에서 외울 단어를 {{단어}} 또는 **단어**로 감싸면 자동으로 빈칸 카드가 만들어집니다.">${escapeHtml(
          body,
        )}</textarea>
        <div class="editor-hint">
          <code>{{단어}}</code> = 빈칸 카드, <code>**단어**</code> = 강조 + 빈칸 카드. 둘 다 회상 채점의 키워드로 자동 등록됩니다.
        </div>

        <label>추가 키워드</label>
        <div id="kw-chips" class="chips"></div>
        <div class="row" style="margin-top:0.4rem;">
          <input type="text" id="f-kw" placeholder="키워드 추가 후 Enter" style="flex:1;" />
          <button type="button" class="btn sm" data-action="add-kw">추가</button>
        </div>

        <h2>Q/A 페어</h2>
        <div id="qa-list" class="qa-list"></div>
        <div class="row">
          <input type="text" id="f-q" placeholder="질문" style="flex:1;" />
          <input type="text" id="f-a" placeholder="답" style="flex:1;" />
          <button type="button" class="btn sm" data-action="add-qa-draft">+ 추가</button>
        </div>

        <hr />
        <div class="row">
          <button type="submit" class="btn primary">${isNew ? '노트 저장' : '변경사항 저장'}</button>
          ${
            isNew
              ? ''
              : `<button type="button" class="btn" data-action="generate-cloze" data-id="${note.id}">클로즈 카드 생성/갱신</button>`
          }
          ${
            isNew
              ? ''
              : `<a class="btn" href="#/recall/${getRecallCardId(note.id) || ''}">회상 연습</a>`
          }
          <div class="spacer"></div>
          ${
            isNew
              ? ''
              : `<button type="button" class="btn bad" data-action="delete-note" data-id="${note.id}">노트 삭제</button>`
          }
        </div>
      </form>

      ${
        isNew
          ? ''
          : renderAttachedCards(note)
      }
    `;
    setApp(html);

    // 드래프트 상태는 모듈 스코프 변수에 보관 → 글로벌 핸들러가 접근
    editorDraft = {
      isNew,
      noteId: note ? note.id : null,
      deckId,
      kw: keywords.slice(),
      qa: qaPairs.slice(),
    };
    paintKwChips();
    paintQADraft();

    document.getElementById('note-form').addEventListener('submit', (e) => {
      e.preventDefault();
      submitEditor();
    });
    document.getElementById('f-kw').addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter') {
        ev.preventDefault();
        addKwFromInput();
      }
    });
  }

  function paintKwChips() {
    const $box = document.getElementById('kw-chips');
    if (!$box || !editorDraft) return;
    $box.innerHTML = editorDraft.kw.length
      ? editorDraft.kw
          .map(
            (k, i) =>
              `<span class="chip">${escapeHtml(
                k,
              )}<button type="button" class="x" data-action="rm-kw" data-i="${i}">×</button></span>`,
          )
          .join('')
      : '<span style="color:var(--fg-dim);font-size:0.85rem;">없음</span>';
  }

  function paintQADraft() {
    const $box = document.getElementById('qa-list');
    if (!$box || !editorDraft) return;
    if (editorDraft.qa.length === 0) {
      $box.innerHTML =
        '<div style="color:var(--fg-dim);font-size:0.85rem;">Q/A 페어가 없습니다. 아래에서 추가하세요.</div>';
      return;
    }
    $box.innerHTML = editorDraft.qa
      .map(
        (q, i) => `
      <div class="qa-item">
        <div><strong>Q.</strong> ${escapeHtml(q.question)}</div>
        <div><strong>A.</strong> ${escapeHtml(q.answer)}</div>
        <button type="button" class="btn sm bad" data-action="rm-qa-draft" data-i="${i}">삭제</button>
      </div>`,
      )
      .join('');
  }

  function addKwFromInput() {
    if (!editorDraft) return;
    const $i = document.getElementById('f-kw');
    if (!$i) return;
    const v = $i.value.trim();
    if (!v) return;
    if (!editorDraft.kw.includes(v)) editorDraft.kw.push(v);
    $i.value = '';
    paintKwChips();
  }

  function wrapSelection(pre, post) {
    const $ta = document.getElementById('f-body');
    if (!$ta) return;
    const s = $ta.selectionStart;
    const e = $ta.selectionEnd;
    const before = $ta.value.slice(0, s);
    const sel = $ta.value.slice(s, e) || '단어';
    const after = $ta.value.slice(e);
    $ta.value = before + pre + sel + post + after;
    $ta.focus();
    $ta.selectionStart = before.length + pre.length;
    $ta.selectionEnd = before.length + pre.length + sel.length;
  }

  function submitEditor() {
    if (!editorDraft) return;
    const t = document.getElementById('f-title').value.trim();
    const b = document.getElementById('f-body').value;
    if (!t) {
      alert('제목을 입력하세요.');
      return;
    }
    if (editorDraft.isNew) {
      const created = addNote(editorDraft.deckId, {
        title: t,
        body: b,
        keywords: editorDraft.kw,
        qaPairs: editorDraft.qa,
      });
      if (!created) {
        alert('저장 실패');
        return;
      }
      editorDraft = null;
      location.hash = `#/note/${created.id}`;
    } else {
      const note = state.notes[editorDraft.noteId];
      if (!note) return;
      updateNote(note.id, { title: t, body: b, keywords: editorDraft.kw });
      const existingIds = new Set(note.qaPairs.map((p) => p.id));
      for (const qa of editorDraft.qa) {
        if (qa.id && existingIds.has(qa.id)) continue;
        addQAPair(note.id, qa.question, qa.answer);
      }
      const draftIds = new Set(editorDraft.qa.map((q) => q.id).filter(Boolean));
      for (const old of note.qaPairs.slice()) {
        if (!draftIds.has(old.id)) deleteQAPair(note.id, old.id);
      }
      editorDraft = null;
      rerender();
    }
  }

  function renderAttachedCards(note) {
    const cards = activeCardsForNote(state, note.id);
    if (cards.length === 0)
      return '<h2>연결된 카드</h2><div class="empty"><p>아직 카드가 없습니다.</p></div>';
    let h = '<h2>연결된 카드</h2><div class="cards">';
    for (const c of cards) {
      let label;
      if (c.kind === 'recall') label = '회상 (전체 본문)';
      else if (c.kind === 'qa') {
        const pair = note.qaPairs.find((p) => p.id === c.ref.qaPairId);
        label = `Q/A: ${pair ? pair.question.slice(0, 30) : '(삭제됨)'}`;
      } else {
        label = `클로즈: ${c.ref.token}`;
      }
      h += `<div class="card"><h3 style="font-size:0.95rem;">${escapeHtml(label)}</h3>
        <div class="meta">${badgeForBox(c.box)} · 다음 복습 ${c.nextDue}</div>
        <div class="actions">
          <a class="btn sm" href="#/${c.kind === 'recall' ? 'recall' : 'quiz'}/${c.id}">바로 복습</a>
        </div></div>`;
    }
    h += '</div>';
    return h;
  }

  function getRecallCardId(noteId) {
    const note = state.notes[noteId];
    if (!note) return null;
    for (const cid of note.cardIds) {
      const c = state.cards[cid];
      if (c && c.kind === 'recall' && !c.archived) return c.id;
    }
    return null;
  }

  // ---------- 회상 ----------
  function renderRecall(cardId) {
    const card = state.cards[cardId];
    if (!card || card.kind !== 'recall' || card.archived) {
      renderError(new Error('회상 카드를 찾을 수 없습니다.'));
      return;
    }
    const note = state.notes[card.noteId];
    if (!note) {
      renderError(new Error('노트를 찾을 수 없습니다.'));
      return;
    }
    const deck = state.decks[note.deckId];

    const html =
      crumbs([
        { label: '대시보드', href: '#/' },
        { label: deck ? deck.name : '덱', href: deck ? `#/deck/${deck.id}` : '#/' },
        { label: '회상 연습' },
      ]) +
      `
      <h1>${escapeHtml(note.title)}</h1>
      <p style="color:var(--fg-dim);">책을 덮고, 기억나는 대로 적어보세요. (Ctrl/Cmd+Enter로 채점)</p>
      <textarea id="recall-input" placeholder="여기에 자유롭게 풀어 적어보세요…" autofocus></textarea>
      <div class="row" style="margin-top:0.6rem;">
        <button class="btn primary" data-action="grade-recall" data-card="${card.id}">채점</button>
        <button class="btn ghost" data-action="reveal-recall" data-card="${card.id}">정답 보기 (포기)</button>
        <div class="spacer"></div>
        ${badgeForBox(card.box)}
      </div>
      <div id="recall-result"></div>
    `;
    setApp(html);

    const $ta = document.getElementById('recall-input');
    $ta.addEventListener('keydown', (ev) => {
      if ((ev.metaKey || ev.ctrlKey) && ev.key === 'Enter') {
        ev.preventDefault();
        gradeRecallNow(card.id);
      }
    });
  }

  function gradeRecallNow(cardId) {
    const card = state.cards[cardId];
    if (!card) return;
    const note = state.notes[card.noteId];
    const typed = document.getElementById('recall-input').value;
    const r = scoreRecall(note, typed);
    const $out = document.getElementById('recall-result');

    if (r.total === 0) {
      $out.innerHTML = `
        <div class="banner warn">이 노트에는 채점할 키워드가 없습니다.
        본문에서 <code>{{단어}}</code> 또는 <code>**단어**</code>로 감싸거나, 키워드를 추가하세요.</div>
        <div class="row">
          <button class="btn ok" data-action="finish-recall" data-card="${cardId}" data-result="correct" data-score="0">정답 처리</button>
          <button class="btn bad" data-action="finish-recall" data-card="${cardId}" data-result="wrong" data-score="0">오답 처리</button>
        </div>`;
      return;
    }

    const klass = r.score >= 70 ? 'high' : 'low';
    const renderedOriginal = highlightOriginal(note.body, new Set(r.hits), new Set(r.misses));
    const renderedTyped = highlightTyped(typed, r.hitRanges);
    $out.innerHTML = `
      <hr />
      <div class="row">
        <div class="score-ring ${klass}">${r.score}<span class="pct">%</span></div>
        <div>
          <div>맞은 키워드 ${r.hits.length} / ${r.total}</div>
          <div style="color:var(--fg-dim);font-size:0.85rem;">기본 제안: ${
            r.score >= 70 ? '정답 처리 (다음 박스로 승급)' : '오답 처리 (1번 박스로 복귀)'
          }</div>
        </div>
        <div class="spacer"></div>
        <button class="btn ok" data-action="finish-recall" data-card="${cardId}" data-result="correct" data-score="${r.score}">정답 처리</button>
        <button class="btn bad" data-action="finish-recall" data-card="${cardId}" data-result="wrong" data-score="${r.score}">오답 처리</button>
      </div>

      <div class="diff">
        <div class="panel">
          <h3>원본</h3>
          ${renderedOriginal}
        </div>
        <div class="panel">
          <h3>내가 쓴 답</h3>
          ${renderedTyped}
        </div>
      </div>

      <h3>키워드</h3>
      <div class="chips">
        ${r.hits.map((k) => `<span class="chip hit">✓ ${escapeHtml(k)}</span>`).join('')}
        ${r.misses.map((k) => `<span class="chip miss">✗ ${escapeHtml(k)}</span>`).join('')}
      </div>
    `;
  }

  function highlightOriginal(body, hitSet, missSet) {
    if (!body) return '';
    // 본문의 마크업을 시각화하면서 hit/miss 분류
    const out = [];
    const re = /\{\{([^{}]+)\}\}|\*\*([^*]+)\*\*/g;
    let last = 0;
    let m;
    while ((m = re.exec(body)) !== null) {
      out.push(escapeHtml(body.slice(last, m.index)));
      const tok = (m[1] || m[2]).trim();
      const cls = hitSet.has(tok) ? 'kw-hit' : missSet.has(tok) ? 'kw-miss' : 'kw-emph';
      out.push(`<span class="${cls}">${escapeHtml(tok)}</span>`);
      last = m.index + m[0].length;
    }
    out.push(escapeHtml(body.slice(last)));
    return out.join('');
  }

  function highlightTyped(typed, ranges) {
    if (!typed) return '<em style="color:var(--fg-dim);">(빈 입력)</em>';
    if (!ranges || ranges.length === 0) return escapeHtml(typed);
    // 정규화된 인덱스 기준이지만 NFC + lowercase는 길이를 보존하므로 안전.
    const sorted = ranges.slice().sort((a, b) => a[0] - b[0]);
    const merged = [];
    for (const r of sorted) {
      if (merged.length && r[0] <= merged[merged.length - 1][1])
        merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], r[1]);
      else merged.push([r[0], r[1]]);
    }
    let out = '';
    let last = 0;
    for (const [s, e] of merged) {
      out += escapeHtml(typed.slice(last, s));
      out += `<span class="typed-hit">${escapeHtml(typed.slice(s, e))}</span>`;
      last = e;
    }
    out += escapeHtml(typed.slice(last));
    return out;
  }

  // ---------- 퀴즈 (QA 또는 클로즈) ----------
  function renderQuiz(cardId) {
    const card = state.cards[cardId];
    if (!card || card.archived) {
      renderError(new Error('카드를 찾을 수 없습니다.'));
      return;
    }
    const note = state.notes[card.noteId];
    if (!note) {
      renderError(new Error('노트를 찾을 수 없습니다.'));
      return;
    }
    const deck = state.decks[note.deckId];
    const head = crumbs([
      { label: '대시보드', href: '#/' },
      { label: deck ? deck.name : '덱', href: deck ? `#/deck/${deck.id}` : '#/' },
      { label: '퀴즈' },
    ]);

    if (card.kind === 'qa') {
      const pair = note.qaPairs.find((p) => p.id === card.ref.qaPairId);
      if (!pair) {
        renderError(new Error('Q/A 페어가 삭제되었습니다.'));
        return;
      }
      setApp(
        head +
          `
        <h1>${escapeHtml(note.title)}</h1>
        <div class="panel">
          <h3>질문</h3>
          <div style="font-size:1.1rem;">${escapeHtml(pair.question)}</div>
        </div>
        <label for="quiz-input">답</label>
        <input type="text" id="quiz-input" autofocus placeholder="답을 입력하고 Enter" />
        <div class="row" style="margin-top:0.6rem;">
          <button class="btn primary" data-action="reveal-qa" data-card="${card.id}">정답 확인</button>
          <div class="spacer"></div>
          ${badgeForBox(card.box)}
        </div>
        <div id="quiz-result"></div>
      `,
      );
      const $i = document.getElementById('quiz-input');
      $i.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') revealQA(card.id);
      });
    } else if (card.kind === 'cloze') {
      const tok = card.ref.token;
      const idx = card.ref.index;
      const ctxHtml = renderClozeContext(note.body, tok, idx);
      setApp(
        head +
          `
        <h1>${escapeHtml(note.title)}</h1>
        <div class="cloze-context">${ctxHtml}</div>
        <label for="quiz-input">빈칸에 들어갈 말</label>
        <input type="text" id="quiz-input" autofocus />
        <div class="row" style="margin-top:0.6rem;">
          <button class="btn primary" data-action="reveal-cloze" data-card="${card.id}">정답 확인</button>
          <div class="spacer"></div>
          ${badgeForBox(card.box)}
        </div>
        <div id="quiz-result"></div>
      `,
      );
      const $i = document.getElementById('quiz-input');
      $i.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') revealCloze(card.id);
      });
    } else {
      // recall은 별도 페이지
      location.hash = `#/recall/${card.id}`;
    }
  }

  function renderClozeContext(body, token, occurrenceIndex) {
    if (!body) return '';
    // 마크업 본문을 한 번 훑으며: 마크업 부분은 평문으로 풀고,
    // 우리가 찾는 token 의 occurrenceIndex 번째 마크업 매치는 빈칸으로 치환
    const re = /\{\{([^{}]+)\}\}|\*\*([^*]+)\*\*/g;
    let out = '';
    let last = 0;
    let counter = 0;
    let replaced = false;
    let m;
    while ((m = re.exec(body)) !== null) {
      out += escapeHtml(body.slice(last, m.index));
      const tok = (m[1] || m[2]).trim();
      if (tok === token) {
        if (counter === occurrenceIndex) {
          out += `<span class="cloze-blank">${escapeHtml(tok)}</span>`;
          replaced = true;
        } else {
          out += escapeHtml(tok);
        }
        counter++;
      } else {
        out += escapeHtml(tok);
      }
      last = m.index + m[0].length;
    }
    out += escapeHtml(body.slice(last));
    if (!replaced) {
      // 마크업이 사라진 경우: 평문 첫 등장을 빈칸 처리
      const plain = plainBody(body);
      const idx = plain.indexOf(token);
      if (idx >= 0) {
        return (
          escapeHtml(plain.slice(0, idx)) +
          `<span class="cloze-blank">${escapeHtml(token)}</span>` +
          escapeHtml(plain.slice(idx + token.length))
        );
      }
      return escapeHtml(plain);
    }
    return out;
  }

  function revealQA(cardId) {
    const card = state.cards[cardId];
    if (!card) return;
    const note = state.notes[card.noteId];
    const pair = note.qaPairs.find((p) => p.id === card.ref.qaPairId);
    if (!pair) return;
    const typed = document.getElementById('quiz-input').value.trim();
    const correct =
      normalize(typed).replace(/\s+/g, '') === normalize(pair.answer).replace(/\s+/g, '');
    const $out = document.getElementById('quiz-result');
    $out.innerHTML = `
      <hr />
      <div class="panel">
        <h3>정답</h3>
        <div style="font-size:1.05rem;">${escapeHtml(pair.answer)}</div>
        ${
          typed
            ? `<div style="margin-top:0.4rem;color:var(--fg-dim);">내 답: ${escapeHtml(typed)}</div>`
            : ''
        }
      </div>
      <div class="row" style="margin-top:0.6rem;">
        <div class="${correct ? 'score-ring high' : 'score-ring low'}">${
      correct ? '맞음' : '틀림'
    }</div>
        <div class="spacer"></div>
        <button class="btn ok" data-action="finish-quiz" data-card="${cardId}" data-result="correct">정답 처리</button>
        <button class="btn bad" data-action="finish-quiz" data-card="${cardId}" data-result="wrong">오답 처리</button>
      </div>
    `;
  }

  function revealCloze(cardId) {
    const card = state.cards[cardId];
    if (!card) return;
    const note = state.notes[card.noteId];
    const typed = document.getElementById('quiz-input').value.trim();
    const correct = normalize(typed).replace(/\s+/g, '') === normalize(card.ref.token).replace(/\s+/g, '');
    const $out = document.getElementById('quiz-result');
    $out.innerHTML = `
      <hr />
      <div class="panel">
        <h3>정답</h3>
        <div style="font-size:1.05rem;"><strong>${escapeHtml(card.ref.token)}</strong></div>
        ${
          typed
            ? `<div style="margin-top:0.4rem;color:var(--fg-dim);">내 답: ${escapeHtml(typed)}</div>`
            : ''
        }
      </div>
      <div class="row" style="margin-top:0.6rem;">
        <div class="${correct ? 'score-ring high' : 'score-ring low'}">${
      correct ? '맞음' : '틀림'
    }</div>
        <div class="spacer"></div>
        <button class="btn ok" data-action="finish-quiz" data-card="${cardId}" data-result="correct">정답 처리</button>
        <button class="btn bad" data-action="finish-quiz" data-card="${cardId}" data-result="wrong">오답 처리</button>
      </div>
    `;
  }

  // ---------- 복습 큐 ----------
  function renderReview() {
    if (!reviewQueue.length) reviewQueue = dueCards(state).map((c) => c.id);
    // 이미 채점된 카드(오늘 다음 due) 자동 제거
    reviewQueue = reviewQueue.filter((id) => {
      const c = state.cards[id];
      return c && !c.archived && c.nextDue <= todayISO();
    });
    if (reviewQueue.length === 0) {
      setApp(`
        <h1>오늘 복습 끝!</h1>
        <p>예정된 카드를 모두 마쳤습니다.</p>
        <p><a class="btn" href="#/">대시보드로</a></p>
      `);
      return;
    }
    const nextId = reviewQueue[0];
    const card = state.cards[nextId];
    if (card.kind === 'recall') location.hash = `#/recall/${nextId}`;
    else location.hash = `#/quiz/${nextId}`;
  }

  function advanceReviewAfterGrade(cardId) {
    // 큐에서 해당 카드 제거 후 다음으로
    reviewQueue = reviewQueue.filter((id) => id !== cardId);
    // 큐가 비어있고, 단발 회상(복습 시작 안 함)이라면 노트로 돌아감
    if (reviewQueue.length > 0) {
      Router.go('#/review');
    } else {
      const c = state.cards[cardId];
      if (c) {
        const note = state.notes[c.noteId];
        if (note) {
          location.hash = `#/note/${note.id}`;
          return;
        }
      }
      location.hash = '#/';
    }
  }

  // ---------- 설정 ----------
  function renderSettings() {
    const html =
      crumbs([{ label: '대시보드', href: '#/' }, { label: '설정' }]) +
      `
      <h1>설정</h1>

      <h2>데이터 백업</h2>
      <p style="color:var(--fg-dim);">localStorage는 브라우저가 정리하면 사라질 수 있습니다. 정기적으로 JSON으로 내보내세요.</p>
      <div class="row">
        <button class="btn primary" data-action="export">JSON 내보내기</button>
        <label class="btn" style="cursor:pointer;">
          JSON 가져오기
          <input type="file" id="import-file" accept="application/json" style="display:none;" />
        </label>
        <div class="spacer"></div>
        <button class="btn bad" data-action="reset-all">전체 초기화</button>
      </div>

      <h2>현재 상태</h2>
      <div class="stats">
        <div class="stat"><div class="label">덱</div><div class="val">${
          Object.keys(state.decks).length
        }</div></div>
        <div class="stat"><div class="label">노트</div><div class="val">${
          Object.keys(state.notes).length
        }</div></div>
        <div class="stat"><div class="label">활성 카드</div><div class="val">${
          Object.values(state.cards).filter((c) => !c.archived).length
        }</div></div>
        <div class="stat"><div class="label">마지막 업데이트</div><div class="val" style="font-size:0.9rem;">${escapeHtml(
          (state.meta && state.meta.lastOpenedAt) || '-',
        ).slice(0, 16)}</div></div>
      </div>

      <h2>학습 방법론</h2>
      <div class="panel" style="white-space:normal;">
        <p><strong>개념화 → 능동적 회상 → 문제 풀이 → 간격 반복.</strong></p>
        <ol>
          <li>덱(과목)을 만들고, 노트에 개념을 <em>파인만식</em>으로 적습니다.</li>
          <li>본문에서 외울 단어를 <code>{{단어}}</code> 또는 <code>**단어**</code>로 감싸세요. 자동으로 빈칸 카드 + 회상 채점 키워드가 됩니다.</li>
          <li>Q/A 페어를 추가해 문제집 효과를 더하세요.</li>
          <li>매일 "오늘 복습"으로 능동적 회상 + 문제 풀이를 합니다.</li>
          <li>정답 시 박스 1→2→3→4→5 (1, 3, 7, 14, 30일 간격), 오답 시 1번 박스 복귀 (Leitner).</li>
        </ol>
      </div>
    `;
    setApp(html);

    document.getElementById('import-file').addEventListener('change', async (ev) => {
      const f = ev.target.files && ev.target.files[0];
      if (!f) return;
      if (!confirm('현재 상태를 가져온 파일로 덮어씁니다. 계속할까요?')) {
        ev.target.value = '';
        return;
      }
      try {
        const next = await Store.importJSON(f);
        state = next;
        persist();
        alert('가져오기 완료.');
        Router.go('#/');
      } catch (e) {
        alert('가져오기 실패: ' + e.message);
      } finally {
        ev.target.value = '';
      }
    });
  }

  // ============================================================
  // 7. 글로벌 이벤트 위임
  // ============================================================
  document.addEventListener('click', (ev) => {
    const btn = ev.target.closest('[data-action]');
    if (!btn) return;
    const a = btn.dataset.action;

    if (a === 'new-deck') {
      const name = prompt('새 덱 이름은?', '');
      if (name == null) return;
      const desc = prompt('설명 (선택, 비워도 됨):', '') || '';
      const d = addDeck(name, desc);
      if (d) Router.go(`#/deck/${d.id}`);
    } else if (a === 'rename-deck') {
      const d = state.decks[btn.dataset.id];
      if (!d) return;
      const name = prompt('덱 이름', d.name);
      if (name == null) return;
      const desc = prompt('설명', d.description || '');
      updateDeck(d.id, { name: name.trim() || d.name, description: (desc || '').trim() });
      rerender();
    } else if (a === 'delete-deck') {
      const d = state.decks[btn.dataset.id];
      if (!d) return;
      if (!confirm(`덱 "${d.name}"과 그 안의 모든 노트/카드를 삭제합니다. 계속할까요?`)) return;
      deleteDeck(d.id);
      Router.go('#/');
    } else if (a === 'start-review') {
      reviewQueue = dueCards(state).map((c) => c.id);
      Router.go('#/review');
    } else if (a === 'start-review-deck') {
      reviewQueue = dueByDeck(state, btn.dataset.id).map((c) => c.id);
      Router.go('#/review');
    } else if (a === 'generate-cloze') {
      const r = generateClozeCards(state, btn.dataset.id);
      persist();
      alert(`클로즈 카드: 추가 ${r.added}개${r.archived > 0 ? `, 보관 처리 ${r.archived}개` : ''}.`);
      rerender();
    } else if (a === 'delete-note') {
      const note = state.notes[btn.dataset.id];
      if (!note) return;
      if (!confirm(`노트 "${note.title}"과 연결된 카드를 모두 삭제합니다. 계속할까요?`)) return;
      const deckId = note.deckId;
      deleteNote(note.id);
      Router.go(`#/deck/${deckId}`);
    } else if (a === 'grade-recall') {
      gradeRecallNow(btn.dataset.card);
    } else if (a === 'reveal-recall') {
      // 입력 비워두고 채점 → 점수 0이라도 그래프/정답 표시
      gradeRecallNow(btn.dataset.card);
    } else if (a === 'finish-recall') {
      const cardId = btn.dataset.card;
      const result = btn.dataset.result;
      const score = parseInt(btn.dataset.score, 10);
      gradeCard(cardId, result, isNaN(score) ? undefined : score);
      advanceReviewAfterGrade(cardId);
    } else if (a === 'finish-quiz') {
      const cardId = btn.dataset.card;
      const result = btn.dataset.result;
      gradeCard(cardId, result);
      advanceReviewAfterGrade(cardId);
    } else if (a === 'reveal-qa') {
      revealQA(btn.dataset.card);
    } else if (a === 'reveal-cloze') {
      revealCloze(btn.dataset.card);
    } else if (a === 'export' || a === 'quick-export') {
      Store.exportJSON(state);
    } else if (a === 'rm-kw') {
      if (editorDraft) {
        editorDraft.kw.splice(parseInt(btn.dataset.i, 10), 1);
        paintKwChips();
      }
    } else if (a === 'add-kw') {
      addKwFromInput();
    } else if (a === 'add-qa-draft') {
      if (editorDraft) {
        const q = (document.getElementById('f-q').value || '').trim();
        const an = (document.getElementById('f-a').value || '').trim();
        if (!q || !an) return;
        editorDraft.qa.push({ id: null, question: q, answer: an });
        document.getElementById('f-q').value = '';
        document.getElementById('f-a').value = '';
        paintQADraft();
      }
    } else if (a === 'rm-qa-draft') {
      if (editorDraft) {
        editorDraft.qa.splice(parseInt(btn.dataset.i, 10), 1);
        paintQADraft();
      }
    } else if (a === 'wrap') {
      wrapSelection(btn.dataset.pre, btn.dataset.post);
    } else if (a === 'reset-all') {
      if (!confirm('모든 데이터를 삭제합니다. 정말로?')) return;
      if (!confirm('정말로 정말로? 이 작업은 되돌릴 수 없습니다.')) return;
      state = Store.reset();
      persist();
      alert('초기화 완료.');
      Router.go('#/');
    }
  });

  // ============================================================
  // 8. 부트
  // ============================================================
  window.addEventListener('hashchange', () => Router.handle());
  if (!location.hash) location.hash = '#/';
  Router.handle();

  // 디버그용 노출
  window.__um = { state: () => state, Store, parseCloze, scoreRecall, srsGradeCard };
})();
