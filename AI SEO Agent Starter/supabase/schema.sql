-- projects
create table projects (
  id bigserial primary key,
  name text not null,
  slug text unique,
  created_at timestamptz default now()
);

-- keywords
create table keywords (
  id bigserial primary key,
  project_id bigint references projects(id),
  keyword text not null,
  source text,
  raw jsonb,
  canonical text,
  created_at timestamptz default now()
);

-- clusters
create table clusters (
  id bigserial primary key,
  project_id bigint references projects(id),
  name text,
  keywords jsonb,
  intent text,
  difficulty integer,
  created_at timestamptz default now()
);

-- serp snapshots
create table serp_snapshots (
  id bigserial primary key,
  project_id bigint references projects(id),
  keyword text,
  snapshot_at timestamptz default now(),
  results jsonb
);

-- competitors
create table competitors (
  id bigserial primary key,
  project_id bigint references projects(id),
  domain text,
  url text,
  title text,
  meta text,
  headings jsonb,
  outbound_links jsonb,
  word_count int,
  scraped_at timestamptz default now()
);

-- backlinks
create table backlinks (
  id bigserial primary key,
  project_id bigint references projects(id),
  from_domain text,
  to_domain text,
  anchor text,
  context text,
  discovered_at timestamptz default now()
);

-- briefs
create table briefs (
  id bigserial primary key,
  project_id bigint references projects(id),
  cluster_id bigint references clusters(id),
  title text,
  h1 text,
  outline jsonb,
  entities jsonb,
  internal_links jsonb,
  json_ld jsonb,
  created_at timestamptz default now()
);

-- articles
create table articles (
  id bigserial primary key,
  project_id bigint references projects(id),
  cluster_id bigint references clusters(id),
  brief_id bigint references briefs(id),
  title text,
  slug text unique,
  html text,
  json_ld jsonb,
  published boolean default false,
  published_at timestamptz,
  created_at timestamptz default now()
);

-- audits
create table audits (
  id bigserial primary key,
  project_id bigint references projects(id),
  url text,
  audit jsonb,
  score integer,
  audited_at timestamptz default now()
);

create extension if not exists vector;
alter table articles add column if not exists embedding vector(1536);
