/**
 * Audit Agent skeleton
 * - Fetches a page (worker) and runs simple audit checks
 * - Returns JSON audit with score
 */

import fetch from 'node-fetch';

export default async function runAuditAgent(payload:{ project_id:number, url:string }) {
  const workerBase = process.env.WORKER_BASE_URL;
  const data = await fetch(`${workerBase}/api/page?url=${encodeURIComponent(payload.url)}`).then(r=>r.json());
  // Simple checks:
  const hasTitle = data.title && data.title.length > 10;
  const hasMeta = data.meta && data.meta.length > 20;
  const hCount = (data.headings || []).length;
  const score = (hasTitle?30:0) + (hasMeta?30:0) + Math.min(hCount*10,40);
  return { url: payload.url, score, issues: [], details: data };
}
