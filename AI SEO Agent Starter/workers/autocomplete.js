export default {
  async fetch(req) {
    const url = new URL(req.url);
    const q = url.searchParams.get('q');
    if (!q) return new Response('missing q', { status: 400 });

    const api = `https://suggestqueries.google.com/complete/search?client=firefox&q=${encodeURIComponent(q)}`;
    const r = await fetch(api);
    if (!r.ok) return new Response(JSON.stringify({ error: 'fetch_failed' }), { status: 502 });

    const text = await r.text();
    let json = [];
    try { json = JSON.parse(text); } catch (e) {
      // fallback: try to extract between brackets
      return new Response(JSON.stringify({ error: 'parse_failed' }), { status: 500 });
    }
    const suggestions = json[1] || [];
    return new Response(JSON.stringify({ q, suggestions }), { headers: { 'Content-Type': 'application/json' } });
  }
};
