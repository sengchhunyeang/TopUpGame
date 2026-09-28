/**
 * Call the JSON API. Always resolves to an object with `ok`;
 * on failure `error` holds a message safe to show the user.
 */
export async function api(path, body) {
  try {
    const r = await fetch(path, {
      method: body ? 'POST' : 'GET',
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined
    });
    const data = await r.json().catch(() => ({}));
    return r.ok ? data : { ok: false, error: data.error || 'Request failed' };
  } catch {
    return { ok: false, error: 'Network error, please try again' };
  }
}
