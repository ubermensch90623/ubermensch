const toast = document.getElementById("toast");
const logList = document.getElementById("logList");
const STORAGE_KEY = "antigravityActivityLog";
const MAX_LOGS = 200;
let toastTimer;

const showToast = (message) => {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2000);
};

const loadLogs = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    return [];
  }
};

const saveLogs = (logs) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(logs));
  } catch (error) {
    showToast("로그 저장에 실패했습니다. 저장 공간을 확인하세요.");
  }
};

const renderLogs = () => {
  const logs = loadLogs();
  logList.innerHTML = "";

  if (!logs.length) {
    const empty = document.createElement("li");
    empty.className = "log-empty";
    empty.textContent = "아직 기록된 학습 활동이 없습니다.";
    logList.appendChild(empty);
    return;
  }

  logs.forEach((log) => {
    const item = document.createElement("li");
    item.className = "log-item";

    const info = document.createElement("div");
    const target = document.createElement("div");
    target.className = "log-target";
    target.textContent = log.target;

    const meta = document.createElement("div");
    meta.className = "log-meta";
    meta.textContent = log.action;

    info.appendChild(target);
    info.appendChild(meta);

    const time = document.createElement("time");
    time.textContent = log.timestamp;

    item.appendChild(info);
    item.appendChild(time);
    logList.appendChild(item);
  });
};

const addLog = ({ target, action }) => {
  const logs = loadLogs();
  const timestamp = new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date());

  const updated = [
    { target, action, timestamp },
    ...logs,
  ].slice(0, MAX_LOGS);

  saveLogs(updated);
  renderLogs();
};

document.querySelectorAll("[data-action='open']").forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.target ?? "링크";
    addLog({ target, action: "대시보드 버튼 클릭" });
    showToast(`${target} 화면으로 이동합니다 (데모).`);
  });
});

document.querySelectorAll("[data-action='clear-log']").forEach((button) => {
  button.addEventListener("click", () => {
    saveLogs([]);
    renderLogs();
    showToast("활동 로그가 초기화되었습니다.");
  });
});

document.querySelectorAll("[data-action='export-log']").forEach((button) => {
  button.addEventListener("click", () => {
    const logs = loadLogs();
    const blob = new Blob([JSON.stringify(logs, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "antigravity-activity-log.json";
    anchor.click();
    URL.revokeObjectURL(url);
    showToast("활동 로그를 내려받았습니다.");
  });
});

renderLogs();
