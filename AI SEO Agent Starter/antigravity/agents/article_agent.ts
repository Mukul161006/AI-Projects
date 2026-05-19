/**
 * Article Agent skeleton (Gemini)
 * - Accepts brief id, generates full article HTML + json-ld
 * - Runs visibility checklist and computes visibility_score
 */

export default async function runArticleAgent(payload:{ project_id:number, brief_id:number }) {
  // TODO: fetch brief from Supabase
  // TODO: call Gemini to generate article
  // TODO: compute visibility score and save HTML + json_ld into articles table

  return { status: 'ok', article_id: null };
}
