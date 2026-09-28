import { $ } from '../lib/dom.js';
import { api } from '../lib/api.js';

/** Coupon input rendered by coupon_field(). Calls onChange({ code, discount }). */
export function createCouponField(root, onChange = () => {}) {
  const input = $('input', root), msg = $('[data-coupon-msg]', root);
  let applied = { code: '', discount: 0 };

  function show(text, ok) {
    msg.textContent = text;
    msg.classList.toggle('text-emerald-600', ok);
    msg.classList.toggle('text-red-500', !ok);
  }

  async function apply() {
    const res = await api('/api/coupon', { code: input.value.trim() });
    if (res.ok) {
      applied = { code: res.code, discount: res.discount };
      show(`Coupon applied: ${Math.round(res.discount * 100)}% off`, true);
    } else {
      applied = { code: '', discount: 0 };
      show(res.error, false);
    }
    onChange(applied);
  }

  $('[data-apply]', root).addEventListener('click', apply);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); apply(); } });

  return { get value() { return applied; } };
}
