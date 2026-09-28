/* Admin panel: hover/focus tooltip for chart marks ([data-tip]). */
const tip = document.getElementById('chart-tip');

function show(el) {
  tip.textContent = el.dataset.tip;
  tip.classList.remove('hidden');
  const r = el.getBoundingClientRect();
  const w = tip.offsetWidth, h = tip.offsetHeight;
  const x = Math.min(Math.max(r.left + r.width / 2 - w / 2, 8), window.innerWidth - w - 8);
  const y = r.top - h - 8 < 8 ? r.bottom + 8 : r.top - h - 8;
  tip.style.left = `${x}px`;
  tip.style.top = `${y}px`;
}
const hide = () => tip.classList.add('hidden');

document.querySelectorAll('[data-tip]').forEach(el => {
  el.addEventListener('mouseenter', () => show(el));
  el.addEventListener('focus', () => show(el));
  el.addEventListener('mouseleave', hide);
  el.addEventListener('blur', hide);
});
window.addEventListener('scroll', hide, { passive: true });
