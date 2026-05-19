# AI-SEO Agent Starter Repo

This starter repository contains:
- Cloudflare Workers (basic SERP, Autocomplete, PAA, Page Fetch)
- Antigravity agent skeletons (TypeScript)
- Playwright scrapers (Python)
- Supabase schema (Postgres + pgvector)
- Prompt templates (JSON)

**Where to start**
1. Create a Supabase project and run `supabase/schema.sql`.
2. Create Cloudflare Worker and bind a KV namespace. Deploy workers using wrangler.
3. Create Antigravity project and add agent files. Insert LLM keys and Supabase secrets.
4. Test workers locally with `wrangler dev` or deploy and call endpoints.

**Notes**
- Worker parsers use simple regex extraction as a starting point. Replace with robust DOM parsing for production.
- Respect robots.txt and rate limits.
- Keep LLM keys secret.

