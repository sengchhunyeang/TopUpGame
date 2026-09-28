import { $, money } from '../lib/dom.js';
import { api } from '../lib/api.js';
import { toast } from '../components/toast.js';
import { createChoiceGroup } from '../components/choice-group.js';
import { createPlayerCheck } from '../components/player-check.js';
import { createCouponField } from '../components/coupon-field.js';

export function initTopup(root) {
  const gameId = root.dataset.gameId;
  const serverType = root.dataset.serverType;
  const uid = $('#uid'), sid = $('#sid'), srv = $('#srv');

  const serverValue = () => serverType === 'text' ? sid.value.trim() : serverType === 'select' ? srv.value : '';

  const player = createPlayerCheck($('[data-player-status]', root), () => ({
    game_id: gameId, uid: uid.value.trim(), server: serverValue()
  }));
  const products = createChoiceGroup($('[data-products]', root), { onChange: paintBar });
  const payments = createChoiceGroup($('[data-payments]', root), { initial: 'khqr' });
  const coupon = createCouponField($('[data-coupon]', root), paintBar);

  // Digits only; any edit invalidates a previous check.
  [uid, sid].filter(Boolean).forEach(el => el.addEventListener('input', () => {
    el.value = el.value.replace(/\D/g, '');
    player.reset();
  }));
  srv?.addEventListener('change', () => player.reset());

  function paintBar() {
    const sel = products.selected, disc = coupon?.value.discount || 0;
    $('[data-total]').textContent = money(sel ? +sel.dataset.price * (1 - disc) : 0);
    $('[data-product]').textContent = sel ? sel.dataset.title + (disc ? ` (-${Math.round(disc * 100)}%)` : '') : '-';
  }

  const payBtn = $('[data-paynow]');
  payBtn.addEventListener('click', async () => {
    if (!uid.value.trim()) { toast('Please enter your Game ID'); uid.focus(); return; }
    if (player.loading) { toast('Please wait, checking Player ID...'); return; }
    if (!player.verified) { toast('Please check your player ID first'); return; }
    if (products.value === null) { toast('Please choose a product'); return; }

    payBtn.disabled = true;
    const res = await api('/api/orders', {
      game_id: gameId, uid: uid.value.trim(), server: serverValue(),
      item: +products.value, pay: payments.value, coupon: coupon.value.code
    });
    payBtn.disabled = false;
    if (res.ok) toast(`Order #${res.order.id} created: ${res.order.item} - ${money(res.order.total)}. Payment gateway not connected yet.`, 4000);
    else toast(res.error);
  });

  initMascot();
  paintBar();
}

/** Support mascot: dismissible tip; clicking the mascot re-opens it and focuses the ID field. */
function initMascot() {
  const tip = $('[data-tip]');
  if (!tip) return;
  $('[data-close-tip]').addEventListener('click', () => tip.classList.add('hidden'));
  $('[data-open-tip]').addEventListener('click', () => {
    tip.classList.remove('hidden');
    const uid = $('#uid');
    uid?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    uid?.focus();
  });
}
