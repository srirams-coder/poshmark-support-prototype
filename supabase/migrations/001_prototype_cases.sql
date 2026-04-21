-- Run in Supabase SQL Editor (Dashboard → SQL) after creating a project.
-- Stores full case objects as JSON for the static prototype.

create table if not exists public.prototype_cases (
  id text primary key,
  payload jsonb not null,
  created_at timestamptz not null default now()
);

create index if not exists prototype_cases_created_at_idx on public.prototype_cases (created_at desc);

alter table public.prototype_cases enable row level security;

-- Prototype: allow anon read/write. Tighten for production (auth.uid(), service role only, etc.).
create policy "prototype_cases_select_anon" on public.prototype_cases
  for select using (true);

create policy "prototype_cases_insert_anon" on public.prototype_cases
  for insert with check (true);

create policy "prototype_cases_update_anon" on public.prototype_cases
  for update using (true);

create policy "prototype_cases_delete_anon" on public.prototype_cases
  for delete using (true);
