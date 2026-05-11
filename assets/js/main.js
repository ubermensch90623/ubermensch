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

  /* ---------------- Feature flag toggles ---------------- */
  document.querySelectorAll('#flags .flag').forEach(flag => {
    flag.addEventListener('click', () => {
      const next = flag.getAttribute('aria-pressed') !== 'true';
      flag.setAttribute('aria-pressed', String(next));
    });
  });

});
