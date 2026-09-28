import { $, $$ } from '../lib/dom.js';
import { api } from '../lib/api.js';
import { toast } from './toast.js';

/**
 * Player ID verification box rendered by player_status().
 * `getPayload()` returns { game_id, uid, server } for /api/player/check.
 */
export function createPlayerCheck(root, getPayload) {
  let state = 'idle', seq = 0;

  function set(next, name = '') {
    state = next;
    root.dataset.state = next;
    $('[data-player-name]', root).textContent = name;
  }

  async function check() {
    const payload = getPayload();
    if (!payload.uid) { toast('Please enter your Game ID'); return; }
    const mine = ++seq;
    set('loading');
    const res = await api('/api/player/check', payload);
    if (mine !== seq) return; // input changed while checking
    if (res.ok) set('ok', res.name);
    else { set('idle'); toast(res.error); }
  }

  function reset() { seq++; set('idle'); }

  $$('[data-check]', root).forEach(b => b.addEventListener('click', check));

  return {
    check,
    reset,
    get verified() { return state === 'ok'; },
    get loading() { return state === 'loading'; }
  };
}
