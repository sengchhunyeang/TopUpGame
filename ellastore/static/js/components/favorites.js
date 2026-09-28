import { $$ } from '../lib/dom.js';

/** Heart toggles on game cards. */
export function initFavorites(root = document) {
  $$('[data-fav]', root).forEach(btn => btn.addEventListener('click', e => {
    e.preventDefault();
    const on = btn.getAttribute('aria-pressed') !== 'true';
    btn.setAttribute('aria-pressed', String(on));
  }));
}
