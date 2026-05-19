export default {
  async fetch(req) {
    const url = new URL(req.url);
    const q = url.searchParams.get('q');
    if (!q) return new Response('missing q', { status: 400 });

    // A lightweight approach: query Google and attempt to extract PAA blocks.
    const serpUrl = `https://www.google.com/search?q=${encodeURIComponent(q)}`;
    const resp = await fetch(serpUrl, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    const html = await resp.text();

    // Very fragile regex extraction for PAA; intended as a starter
    const paaMatches = [...html.matchAll(/<div[^>]*>(?:People also ask|People also ask)[\s\S]*?<\/div>/gi)].slice(0, 10);
    const paa = paaMatches.map(m => m[0].replace(/<[^>]+>/g, '').trim()).slice(0,5);

    return new Response(JSON.stringify({ q, paa }), { headers: { 'Content-Type': 'application/json' } });
  }
};
