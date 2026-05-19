/**
 * Brief Agent skeleton (Gemini)
 * - Takes cluster + top competitor snapshots
 * - Produces a JSON brief (title, outline, entities, json_ld)
 */

export default async function runBriefAgent(payload:{ project_id:number, cluster:any, competitors:any[] }) {
  const { project_id, cluster, competitors } = payload;

  const prompt = `Create an SEO content brief for cluster: ${JSON.stringify(cluster)} with competitors: ${JSON.stringify(competitors.slice(0,3))}`;
  // TODO: call Gemini 3 to generate the brief and persist to Supabase

  return { status: 'ok', brief_id: null };
}
