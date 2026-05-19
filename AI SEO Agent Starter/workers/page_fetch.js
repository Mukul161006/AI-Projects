export default {
  async fetch(req) {
    const url = new URL(req.url);
    const target = url.searchParams.get('url');
    if (!target) return new Response('missing url param', { status: 400 });

    // Basic proxy fetch - keep headers minimal
    try {
      const resp = await fetch(target, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; Bot/1.0)' }});
      const html = await resp.text();

      // Extract title, meta description, headings (h1-h3), outbound links and simple word count
      const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
      const title = titleMatch ? titleMatch[1] : '';
      const metaMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([^"']*)["']/i);
      const meta = metaMatch ? metaMatch[1] : '';

      const headings = [...html.matchAll(/<(h1|h2|h3)[^>]*>(.*?)<\/\1>/gis)].map(m => ({ tag: m[1], text: m[2].replace(/<[^>]+>/g,'').trim() }));
      const linkMatches = [...html.matchAll(/<a[^>]*href=["'](http[^"']+)["'][^>]*>/gi)].slice(0,200).map(m=>m[1]);

      const wordCount = html.replace(/<[^>]+>/g,'').split(/\s+/).filter(Boolean).length;

      const out = { url: target, title, meta, headings, outbound_links: linkMatches, word_count: wordCount };
      return new Response(JSON.stringify(out), { headers: { 'Content-Type': 'application/json' } });
    } catch (e) {
      return new Response(JSON.stringify({ error: 'fetch_error', details: String(e) }), { status: 502 });
    }
  }
};
