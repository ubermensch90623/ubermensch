document.addEventListener('DOMContentLoaded', () => {

  /* ---------------- Tabs (Visual Clarity mock) ---------------- */
  const tabs = document.querySelectorAll('#visual-clarity .tab');
  const panels = document.querySelectorAll('#visual-clarity [data-panel]:not(.tab)');

  function activateTab(target) {
    tabs.forEach(t => t.setAttribute('aria-selected', String(t === target)));
    const panelId = target.dataset.panel;
    panels.forEach(p => {
      if (p.dataset.panel === panelId) p.removeAttribute('hidden');
      else p.setAttribute('hidden', '');
    });
  }
  tabs.forEach(t => {
    t.addEventListener('click', () => activateTab(t));
    t.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault();
      const list = Array.from(tabs);
      const i = list.indexOf(t);
      const next = e.key === 'ArrowRight'
        ? list[(i + 1) % list.length]
        : list[(i - 1 + list.length) % list.length];
      next.focus();
      activateTab(next);
    });
  });

  /* ---------------- Palette: click to copy ---------------- */
  const swatches = document.querySelectorAll('#palette .swatch');
  swatches.forEach(sw => {
    sw.addEventListener('click', async () => {
      const hex = sw.dataset.hex || '';
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(hex);
        } else {
          const ta = document.createElement('textarea');
          ta.value = hex;
          ta.style.position = 'fixed';
          ta.style.opacity = '0';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          ta.remove();
        }
      } catch (_) { /* silent */ }
      sw.classList.add('copied');
      clearTimeout(sw._copiedTimer);
      sw._copiedTimer = setTimeout(() => sw.classList.remove('copied'), 900);
    });
  });

  /* ---------------- Checkout button playground ---------------- */
  const btn = document.getElementById('btnPreview');
  const slDuration = document.getElementById('slDuration');
  const slShadow = document.getElementById('slShadow');
  const slSpring = document.getElementById('slSpring');
  const valDuration = document.getElementById('valDuration');
  const valShadow = document.getElementById('valShadow');
  const valSpring = document.getElementById('valSpring');

  function springEasing(strength) {
    // 0 → linear-ish; 100 → very bouncy spring
    const overshoot = 1.0 + (strength / 100) * 1.4; // 1.0 → 2.4
    return `cubic-bezier(.34, ${overshoot.toFixed(2)}, .64, 1)`;
  }

  function syncBtn() {
    if (!btn) return;
    const d = slDuration.value;
    const s = slShadow.value;
    const sp = slSpring.value;
    btn.style.setProperty('--pb-duration', `${d}ms`);
    btn.style.setProperty('--pb-shadow', `${s}px`);
    btn.style.setProperty('--pb-spring', springEasing(Number(sp)));
    valDuration.textContent = `${d}ms`;
    valShadow.textContent = `${s}px`;
    valSpring.textContent = `${sp}%`;
  }

  [slDuration, slShadow, slSpring].forEach(el => el && el.addEventListener('input', syncBtn));
  syncBtn();

  if (btn) {
    btn.addEventListener('click', () => {
      btn.animate(
        [{ transform: 'scale(0.92) translateY(2px)' }, { transform: 'scale(1) translateY(0)' }],
        { duration: Number(slDuration.value), easing: springEasing(Number(slSpring.value)) }
      );
    });
  }

  /* ---------------- UC1: Approach selector ---------------- */
  const approaches = {
    trailing: {
      code:
`<span class="cm">// fires once, after the user stops typing</span>
<span class="kw">const</span> <span class="fn">trailing</span> = (fn, ms) =&gt; {
  <span class="kw">let</span> t, args;
  <span class="kw">return</span> (...a) =&gt; {
    args = a; <span class="fn">clearTimeout</span>(t);
    t = <span class="fn">setTimeout</span>(() =&gt; fn(...args), ms);
  };
};`,
      latency: 'latency: ~ms wait',
      calls: 'calls: minimum',
    },
    leading: {
      code:
`<span class="cm">// fires immediately, then locks for ms</span>
<span class="kw">const</span> <span class="fn">leading</span> = (fn, ms) =&gt; {
  <span class="kw">let</span> open = <span class="kw">true</span>;
  <span class="kw">return</span> (...a) =&gt; {
    <span class="kw">if</span> (!open) <span class="kw">return</span>;
    open = <span class="kw">false</span>; fn(...a);
    <span class="fn">setTimeout</span>(() =&gt; (open = <span class="kw">true</span>), ms);
  };
};`,
      latency: 'latency: 0',
      calls: 'calls: capped',
    },
    hybrid: {
      code:
`<span class="cm">// fires now AND after last keystroke</span>
<span class="kw">const</span> <span class="fn">hybrid</span> = (fn, ms) =&gt; {
  <span class="kw">let</span> t, open = <span class="kw">true</span>;
  <span class="kw">return</span> (...a) =&gt; {
    <span class="kw">if</span> (open) { fn(...a); open = <span class="kw">false</span>; }
    <span class="fn">clearTimeout</span>(t);
    t = <span class="fn">setTimeout</span>(() =&gt; { fn(...a); open = <span class="kw">true</span>; }, ms);
  };
};`,
      latency: 'latency: 0',
      calls: 'calls: 2 per burst',
    },
  };
  const approachTabs = document.querySelectorAll('#approachTabs .approach-tab');
  const approachCodeEl = document.querySelector('#approachCode code');
  const metaLatency = document.getElementById('metaLatency');
  const metaCalls = document.getElementById('metaCalls');
  function selectApproach(key) {
    approachTabs.forEach(t => t.setAttribute('aria-selected', String(t.dataset.approach === key)));
    const a = approaches[key];
    if (!a || !approachCodeEl) return;
    approachCodeEl.innerHTML = a.code;
    metaLatency.textContent = a.latency;
    metaCalls.textContent = a.calls;
  }
  approachTabs.forEach(t => t.addEventListener('click', () => selectApproach(t.dataset.approach)));
  selectApproach('trailing');

  /* ---------------- UC2: Annotation dots ---------------- */
  const popover = document.getElementById('notePopover');
  document.querySelectorAll('#diffMock .note-dot').forEach(dot => {
    dot.addEventListener('click', (e) => {
      e.stopPropagation();
      const note = dot.dataset.note || '';
      const warn = dot.classList.contains('note-warn');
      popover.textContent = note;
      popover.classList.toggle('warn', warn);
      popover.hidden = false;
    });
  });
  document.addEventListener('click', (e) => {
    if (!popover || popover.hidden) return;
    if (!e.target.closest('.note-dot') && !e.target.closest('#notePopover')) {
      popover.hidden = true;
    }
  });

  /* ---------------- UC4: Expandable research rows ---------------- */
  document.querySelectorAll('#researchList .research-row').forEach(row => {
    row.addEventListener('click', () => {
      const next = row.getAttribute('aria-expanded') !== 'true';
      row.setAttribute('aria-expanded', String(next));
    });
  });

  /* ---------------- UC5: Feature flag toggles + live export ---------------- */
  const flagsRoot = document.getElementById('flags');
  const flagExport = document.querySelector('#flagExport code');

  function renderFlagExport() {
    if (!flagsRoot || !flagExport) return;
    const flags = Array.from(flagsRoot.querySelectorAll('.flag'));
    const lines = flags.map(f => {
      const name = f.firstChild.textContent.trim();
      const on = f.getAttribute('aria-pressed') === 'true';
      const val = on
        ? '<span class="on">true</span>'
        : '<span class="off">false</span>';
      return `  <span class="key">${name}</span>: ${val},`;
    });
    flagExport.innerHTML = '{\n' + lines.join('\n') + '\n}';
  }

  document.querySelectorAll('#flags .flag').forEach(flag => {
    flag.addEventListener('click', () => {
      const next = flag.getAttribute('aria-pressed') !== 'true';
      flag.setAttribute('aria-pressed', String(next));
      renderFlagExport();
    });
  });
  renderFlagExport();

});
