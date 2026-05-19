export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const q = url.searchParams.get('q');
    if (!q) return new Response('missing q', { status: 400 });

    const cacheKey = `serp:${q}`;
    try {
      const cached = await env.KV.get(cacheKey);
      if (cached) return new Response(cached, { headers: { 'Content-Type': 'application/json' } });
    } catch (e) {
      // KV might not be bound in local dev
      console.warn('KV read error', e);
    }

    const serpUrl = `https://www.google.com/search?q=${encodeURIComponent(q)}&hl=en`;
    const resp = await fetch(serpUrl, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; Bot/1.0)' } });
    const html = await resp.text();

    // Basic regex extraction (fragile) - replace with DOM parser for production
    const matches = [...html.matchAll(/<a href="\/url\?q=(.*?)&/g)].slice(0, 12);
    const results = matches.map((m, i) => ({
      position: i + 1,
      url: decodeURIComponent(m[1])
    }));

    const body = JSON.stringify({ keyword: q, results, fetched_at: new Date().toISOString() });
    try {
      await env.KV.put(cacheKey, body, { expirationTtl: 86400 });
    } catch(e) { console.warn('KV put error', e); }

    return new Response(body, { headers: { 'Content-Type': 'application/json' } });
  }
};
