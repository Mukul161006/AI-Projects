import scrape_serp from './scrape_serp.js';
import autocomplete from './autocomplete.js';
import scrape_paa from './scrape_paa.js';
import page_fetch from './page_fetch.js';

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname.replace(/^\//,'');
    if (path.startsWith('api/serp')) return scrape_serp.fetch(req, env);
    if (path.startsWith('api/autocomplete')) return autocomplete.fetch(req, env);
    if (path.startsWith('api/paa')) return scrape_paa.fetch(req, env);
    if (path.startsWith('api/page')) return page_fetch.fetch(req, env);
    return new Response('OK - AI SEO Workers', { status: 200 });
  }
};
