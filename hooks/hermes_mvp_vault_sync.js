/**
 * HERMES MVP localStorage → vault .md 자동 sync
 *
 * 자가진화 제안 5 (severity 5, 5/23 carry-over, 2026-05-24 채택)
 * - 관찰: MVP 안에 Export 버튼 없음. JS 의지·열기 0건 = 데이터 증발 위험.
 * - 처방: localStorage 전체 → 1일 1회 .md export → 분신 vault watcher가 자동 흡수.
 *
 * 적용:
 *   1. 이 파일을 종환 PC `Desktop/HERMES/hermes_mvp_vault_sync.js`에 저장
 *   2. MVP HTML(`Desktop/HERMES/hermes_mvp.html`) </body> 직전에 한 줄 추가:
 *        <script src="hermes_mvp_vault_sync.js"></script>
 *   3. MVP 새로고침 → 우상단 [↓ Vault Export] 버튼 자동 생성
 *   4. 1일 1회 클릭 → 다운로드 폴더에 `HERMES_YYYY-MM-DD.md` 저장
 *   5. 분신 watcher가 다운로드 폴더 → vault `_SSOT/hermes_mvp/` 매시간 sync
 *
 * 의존성: 없음 (vanilla JS, FileSaver 미사용 — Blob + URL.createObjectURL)
 */

(function () {
  "use strict";

  const VERSION = "0.1.0";
  const BTN_ID = "hermes-vault-export-btn";
  const AUTO_PROMPT_HOUR = 21; // 22시 취침 직전, 1회 자동 prompt
  const LAST_EXPORT_KEY = "hermes_mvp_last_export";

  function today() {
    return new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function localStorageToMarkdown() {
    const lines = [];
    lines.push("---");
    lines.push("type: hermes-mvp-export");
    lines.push(`date: ${today()}`);
    lines.push(`exported_at: ${nowIso()}`);
    lines.push(`source: hermes_mvp.html localStorage`);
    lines.push(`mvp_vault_sync_version: ${VERSION}`);
    lines.push("---");
    lines.push("");
    lines.push(`# HERMES MVP Export — ${today()}`);
    lines.push("");

    if (localStorage.length === 0) {
      lines.push("> ⚠️ localStorage empty.");
      return lines.join("\n");
    }

    // 키 정렬 (재현성).
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) keys.push(localStorage.key(i));
    keys.sort();

    for (const key of keys) {
      const raw = localStorage.getItem(key) ?? "";
      lines.push(`## \`${key}\``);
      lines.push("");

      // JSON 시도. 실패 시 raw string.
      let pretty = raw;
      try {
        pretty = JSON.stringify(JSON.parse(raw), null, 2);
        lines.push("```json");
        lines.push(pretty);
        lines.push("```");
      } catch {
        lines.push("```");
        lines.push(raw);
        lines.push("```");
      }
      lines.push("");
    }

    lines.push("---");
    lines.push("");
    lines.push("**다음 단계** (자동):");
    lines.push("");
    lines.push("- 분신 watcher가 매시간 다운로드 폴더 → vault `_SSOT/hermes_mvp/` 동기화");
    lines.push("- 동기화 완료 시 이 파일은 다운로드 폴더에서 자동 제거 (vault에 dedup)");
    return lines.join("\n");
  }

  function downloadMarkdown() {
    const md = localStorageToMarkdown();
    const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `HERMES_${today()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    localStorage.setItem(LAST_EXPORT_KEY, nowIso());
  }

  function injectButton() {
    if (document.getElementById(BTN_ID)) return;
    const btn = document.createElement("button");
    btn.id = BTN_ID;
    btn.textContent = "↓ Vault Export";
    btn.title = "localStorage 전체 → HERMES_YYYY-MM-DD.md 다운로드";
    Object.assign(btn.style, {
      position: "fixed",
      top: "12px",
      right: "12px",
      zIndex: "2147483647",
      padding: "8px 12px",
      background: "#1a1a1a",
      color: "#eaeaea",
      border: "1px solid #444",
      borderRadius: "6px",
      fontFamily: "system-ui, -apple-system, sans-serif",
      fontSize: "13px",
      cursor: "pointer",
      boxShadow: "0 2px 6px rgba(0,0,0,0.4)",
    });
    btn.addEventListener("click", downloadMarkdown);
    btn.addEventListener("mouseenter", () => (btn.style.background = "#2a2a2a"));
    btn.addEventListener("mouseleave", () => (btn.style.background = "#1a1a1a"));
    document.body.appendChild(btn);
  }

  function maybeAutoPrompt() {
    const last = localStorage.getItem(LAST_EXPORT_KEY);
    const now = new Date();
    if (now.getHours() < AUTO_PROMPT_HOUR) return;
    if (last && last.slice(0, 10) === today()) return; // 오늘 이미 export 됨
    // 22시 직전 1회 자동 다운로드 (의지 우회).
    downloadMarkdown();
    console.info("[hermes-mvp-vault-sync] auto-exported at", nowIso());
  }

  function init() {
    injectButton();
    maybeAutoPrompt();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
