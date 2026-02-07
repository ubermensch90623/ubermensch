const toast = document.getElementById("toast");
let toastTimer;

const showToast = (message) => {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2000);
};

document.querySelectorAll("[data-action='open']").forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.target ?? "링크";
    showToast(`${target} 화면으로 이동합니다 (데모).`);
  });
});
