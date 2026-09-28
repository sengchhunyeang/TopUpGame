import { $, $$ } from '../lib/dom.js';
import { initCarousel } from '../components/carousel.js';
import { initFavorites } from '../components/favorites.js';

/** Live-filter game cards by name. */
function filterGames(query) {
  const q = query.trim().toLowerCase();
  let shown = 0;
  $$('[data-game-card]').forEach(card => {
    const match = card.dataset.name.includes(q);
    card.classList.toggle('hidden', !match);
    shown += match;
  });
  $('[data-empty]')?.classList.toggle('hidden', shown > 0);
}

export function initHome() {
  $$('[data-carousel]').forEach(initCarousel);
  initFavorites();

  // On the home page the header search filters in place instead of submitting.
  const input = $('#searchInput');
  input?.addEventListener('input', () => filterGames(input.value));
  $('#searchPanel')?.addEventListener('submit', e => {
    e.preventDefault();
    $('[data-game-grid]')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}
