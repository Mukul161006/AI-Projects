/**
 * Keyword Agent skeleton for Antigravity
 * Responsibilities:
 *  - Call Workers for autocomplete/PAA
 *  - Normalize suggestions
 *  - Insert into Supabase keywords table
 *
 * Replace SUPABASE_CLIENT placeholder with actual client instance.
 */

import fetch from 'node-fetch';

export default async function runKeywordAgent(payload: { project_id: number, seed: string }) {
  const { project_id, seed } = payload;
  const workerBase = process.env.WORKER_BASE_URL; // e.g. https://your-worker.example.workers.dev

  // 1) autocomplete
  const ac = await fetch(`${workerBase}/api/autocomplete?q=${encodeURIComponent(seed)}`).then(r=>r.json()).catch(()=>({suggestions:[]}));

  // 2) paa
  const paa = await fetch(`${workerBase}/api/paa?q=${encodeURIComponent(seed)}`).then(r=>r.json()).catch(()=>({paa:[]}));

  // 3) combine
  const suggestions = new Set();
  (ac.suggestions || []).forEach(s=>suggestions.add(s));
  (paa.paa || []).forEach(s=>suggestions.add(s));
  suggestions.add(seed);

  const keywords = Array.from(suggestions).map(k => ({ project_id, keyword: k, source: 'combined', raw: {}, canonical: k }));

  // TODO: insert into Supabase using SUPABASE_CLIENT
  return { inserted: keywords.length, sample: keywords.slice(0,5) };
}
