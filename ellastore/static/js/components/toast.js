let timer = null;

export function toast(msg, ms = 2300) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.remove('hidden');
  clearTimeout(timer);
  timer = setTimeout(() => t.classList.add('hidden'), ms);
}
