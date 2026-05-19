/**
 * Clustering Agent skeleton (Claude Sonnet)
 * - Accepts batches of keywords for a project
 * - Calls Claude with clustering prompt
 * - Persists clusters into Supabase
 */

export default async function runClusteringAgent(payload: { project_id: number, keywords: string[] }) {
  const { project_id, keywords } = payload;

  // Example prompt formation (send to Claude)
  const prompt = `Cluster the following keywords into up to 10 clusters and output JSON: ${JSON.stringify(keywords)}`;

  // TODO: call Claude API and parse JSON response
  // TODO: persist clusters to Supabase

  return { status: 'ok', clusters_count: 0 };
}
