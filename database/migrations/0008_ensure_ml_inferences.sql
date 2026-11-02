-- WEB_MINERA | Asegurar tablas ML (ml_models + ml_inferences) + RLS
-- Ejecutar en Supabase SQL Editor si GET /api/v1/ml/inferences falla (tabla ausente).
-- Idempotente. No borra datos existentes.

create extension if not exists pgcrypto;

create table if not exists public.ml_models (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  version text not null,
  status text not null default 'active' check (status in ('active', 'archived')),
  metrics jsonb not null default '{}'::jsonb,
  registered_at timestamptz not null default now(),
  unique (name, version)
);

create table if not exists public.ml_inferences (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  lot_id uuid not null references public.lots (id),
  model_id uuid references public.ml_models (id),
  model_version text not null,
  expected_quantity numeric not null,
  observed_quantity numeric,
  deviation numeric,
  deviation_percent numeric,
  signal text not null default 'none' check (signal in ('none', 'review_signal')),
  features jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists ml_inferences_lot_idx on public.ml_inferences (lot_id);
create index if not exists ml_inferences_org_idx on public.ml_inferences (organization_id);
create index if not exists ml_inferences_org_created_idx
  on public.ml_inferences (organization_id, created_at desc);
create index if not exists ml_inferences_signal_idx on public.ml_inferences (signal);

-- FK opcional desde alerts (si la tabla alerts existe).
do $$
begin
  if exists (
    select 1 from information_schema.tables
    where table_schema = 'public' and table_name = 'alerts'
  ) and not exists (
    select 1 from pg_constraint where conname = 'alerts_ml_inference_fk'
  ) then
    alter table public.alerts
      add constraint alerts_ml_inference_fk
      foreign key (ml_inference_id) references public.ml_inferences (id);
  end if;
end $$;

insert into public.ml_models (name, version, status, metrics)
select
  'expected-quantity-baseline',
  '1.0.0',
  'active',
  '{"mae": 2.4, "mape": 3.1, "description": "Estimador estadístico de cantidad esperada"}'::jsonb
where not exists (
  select 1 from public.ml_models
  where name = 'expected-quantity-baseline' and version = '1.0.0'
);

insert into public.ml_models (name, version, status, metrics)
select
  'expected-quantity-baseline',
  '1.1.0',
  'active',
  '{"mae": 2.1, "mape": 2.8, "description": "Estimador v1.1 con ajuste mineral"}'::jsonb
where not exists (
  select 1 from public.ml_models
  where name = 'expected-quantity-baseline' and version = '1.1.0'
);

alter table public.ml_models enable row level security;
alter table public.ml_inferences enable row level security;

drop policy if exists ml_models_select on public.ml_models;
create policy ml_models_select on public.ml_models
  for select using (auth.role() = 'authenticated');

drop policy if exists ml_inferences_select on public.ml_inferences;
create policy ml_inferences_select on public.ml_inferences
  for select using (organization_id = public.current_org_id());

drop policy if exists ml_inferences_insert on public.ml_inferences;
create policy ml_inferences_insert on public.ml_inferences
  for insert with check (
    organization_id = public.current_org_id()
    and public.current_role() in (
      'admin', 'auditor', 'supervisor', 'control_center', 'receiver', 'plant_manager'
    )
  );

grant select on public.ml_models to authenticated;
grant select, insert on public.ml_inferences to authenticated;
grant all on public.ml_models to service_role;
grant all on public.ml_inferences to service_role;

notify pgrst, 'reload schema';
