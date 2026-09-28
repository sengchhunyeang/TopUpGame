import { $, $$ } from '../lib/dom.js';
import { toast } from './toast.js';

/** Menu / search panels (only one open at a time) and the login placeholder. */
export function initHeader() {
  const toggles = $$('[data-toggle-panel]');
  const panels = toggles.map(b => document.getElementById(b.dataset.togglePanel));

  toggles.forEach((btn, i) => btn.addEventListener('click', () => {
    const panel = panels[i];
    const open = panel.classList.contains('hidden');
    panels.forEach((p, j) => { p.classList.add('hidden'); toggles[j].setAttribute('aria-expanded', 'false'); });
    if (open) {
      panel.classList.remove('hidden');
      btn.setAttribute('aria-expanded', 'true');
      panel.querySelector('input')?.focus();
    }
  }));

  // Keep the search panel open when arriving with ?q=
  if ($('#searchInput')?.value) $('#searchPanel').classList.remove('hidden');

  $('[data-login]')?.addEventListener('click', e => {
    e.preventDefault();
    toast('Login is not connected yet');
  });
}
