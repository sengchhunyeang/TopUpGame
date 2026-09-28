import { $, $$ } from '../lib/dom.js';

/** Wires a [data-carousel] element rendered by components/carousel.html. */
export function initCarousel(root) {
  const track = $('[data-track]', root);
  const dots = $$('[data-dot]', root);
  const count = track.children.length;
  const interval = +root.dataset.interval || 5000;
  let index = 0, timer = null;

  function go(i) {
    index = (i + count) % count;
    track.style.transform = `translateX(-${index * 100}%)`;
    dots.forEach((d, j) => d.setAttribute('aria-current', j === index ? 'true' : 'false'));
  }
  function restart() {
    clearInterval(timer);
    timer = setInterval(() => go(index + 1), interval);
  }

  $('[data-prev]', root).addEventListener('click', () => { go(index - 1); restart(); });
  $('[data-next]', root).addEventListener('click', () => { go(index + 1); restart(); });
  dots.forEach(d => d.addEventListener('click', () => { go(+d.dataset.dot); restart(); }));

  go(0);
  restart();
}
