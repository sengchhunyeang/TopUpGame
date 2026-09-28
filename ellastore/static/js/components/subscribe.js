import { $$ } from '../lib/dom.js';
import { api } from '../lib/api.js';
import { toast } from './toast.js';

/** Newsletter forms marked with [data-subscribe]. */
export function initSubscribe() {
  $$('form[data-subscribe]').forEach(form => form.addEventListener('submit', async e => {
    e.preventDefault();
    const res = await api('/api/subscribe', { email: form.email.value.trim() });
    if (res.ok) { toast('Subscribed. Thank you!'); form.reset(); }
    else toast(res.error);
  }));
}
