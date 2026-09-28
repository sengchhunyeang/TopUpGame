import { $$ } from '../lib/dom.js';

/**
 * Single-select group of [data-choice] buttons inside `root`.
 * Selection is shown via aria-pressed (styled in style.css).
 */
export function createChoiceGroup(root, { initial = null, onChange = () => {} } = {}) {
  const buttons = $$('[data-choice]', root);
  let value = null;

  function select(v) {
    value = v;
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.choice === v)));
    onChange(v, buttons.find(b => b.dataset.choice === v) || null);
  }

  buttons.forEach(b => b.addEventListener('click', () => select(b.dataset.choice)));
  if (initial !== null) select(String(initial));

  return {
    get value() { return value; },
    get selected() { return buttons.find(b => b.dataset.choice === value) || null; },
    select
  };
}
