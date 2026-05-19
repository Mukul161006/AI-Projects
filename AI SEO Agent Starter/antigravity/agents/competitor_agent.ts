/**
 * Competitor Agent skeleton
 * - Accepts SERP snapshots and analyzes competitor pages
 * - Calls Cloudflare worker /api/page for each URL
 * - Calls Claude for strengths/weaknesses extraction
 */

import fetch from 'node-fetch';

export default async function runCompetitorAgent(payload:{ project_id:number, serp_results: any[] }) {
  const { project_id, serp_results } = payload;
  const workerBase = process.env.WORKER_BASE_URL;
  const reports = [];

  for (const r of serp_results) {
    try {
      const data = await fetch(`${workerBase}/api/page?url=${encodeURIComponent(r.url)}`).then(res=>res.json());
      // TODO: call Claude for analysis and store results
      reports.push({ url: r.url, summary: 'placeholder', data });
    } catch(e) {
      reports.push({ url: r.url, error: String(e) });
    }
  }
  return { reports };
}
