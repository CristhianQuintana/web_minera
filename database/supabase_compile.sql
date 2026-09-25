-- =============================================================================
-- WEB_MINERA — PEGAR ESTE BLOQUE COMPLETO EN SUPABASE → SQL EDITOR → RUN
-- =============================================================================
-- Requiere que 0001, 0004 y 0005 de APP_MINERA ya estén aplicadas.
-- Idempotente: se puede re-ejecutar.
-- Opcional después: database/seeds/promote_admin.sql
-- =============================================================================
-- WEB_MINERA — extensión de plataforma web sobre el esquema de APP_MINERA.
-- Ejecutar DESPUÉS de 0001_init.sql, 0004_fix_rls_and_profiles.sql y 0005_roles_receptions.sql.
-- Idempotente: se puede re-ejecutar sin romper datos existentes.
--
-- Añade: invitaciones, tolerancias versionadas, balance de masas,
-- alertas, ML, notificaciones, configuración y columnas de perfil web.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Perfiles: estados de invitación y actividad (no rompe status active/inactive)
-- ---------------------------------------------------------------------------
alter table public.profiles
  add column if not exists email text,
  add column if not exists last_activity_at timestamptz,
  add column if not exists invitation_status text not null default 'active';

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'profiles_invitation_status_check'
  ) then
    alter table public.profiles
      add constraint profiles_invitation_status_check
      check (invitation_status in ('pending', 'active', 'inactive', 'expired'));
  end if;
end $$;

update public.profiles p
set email = u.email
from auth.users u
where p.id = u.id
  and (p.email is null or p.email = '');

-- ---------------------------------------------------------------------------
-- Invitaciones (sin registro público)
-- ---------------------------------------------------------------------------
create table if not exists public.invitations (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  full_name text not null,
  role text not null,
  organization_id uuid not null references public.organizations (id),
  token_hash text not null unique,
  invited_by uuid references auth.users (id),
  expires_at timestamptz not null,
  accepted_at timestamptz,
  status text not null default 'pending' check (
    status in ('pending', 'accepted', 'expired', 'revoked')
  ),
  created_at timestamptz not null default now()
);

create index if not exists invitations_email_idx on public.invitations (lower(email));
create index if not exists invitations_org_idx on public.invitations (organization_id);

-- ---------------------------------------------------------------------------
-- Tolerancias versionadas (nunca sobrescribir historial)
-- ---------------------------------------------------------------------------
create table if not exists public.tolerance_rules (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  rule_key text not null,
  name text not null,
  value numeric not null check (value >= 0),
  unit text not null,
  version integer not null default 1,
  effective_from timestamptz not null default now(),
  effective_to timestamptz,
  is_active boolean not null default true,
  created_by uuid references auth.users (id),
  created_at timestamptz not null default now(),
  unique (organization_id, rule_key, version)
);

create index if not exists tolerance_rules_active_idx
  on public.tolerance_rules (organization_id, rule_key, is_active);

-- ---------------------------------------------------------------------------
-- Balance de masas
-- ---------------------------------------------------------------------------
create table if not exists public.mass_balances (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  lot_id uuid not null references public.lots (id),
  origin_quantity numeric not null,
  received_quantity numeric,
  difference numeric,
  difference_percent numeric,
  tolerance_value numeric,
  tolerance_unit text,
  tolerance_rule_id uuid references public.tolerance_rules (id),
  tolerance_version integer,
  status text not null default 'insufficient_data' check (
    status in ('within_tolerance', 'review_required', 'insufficient_data')
  ),
  calculated_at timestamptz not null default now(),
  unique (lot_id)
);

create index if not exists mass_balances_org_idx on public.mass_balances (organization_id);
create index if not exists mass_balances_status_idx on public.mass_balances (status);

-- ---------------------------------------------------------------------------
-- Alertas y revisiones
-- ---------------------------------------------------------------------------
create table if not exists public.alerts (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  lot_id uuid references public.lots (id),
  severity text not null check (severity in ('low', 'medium', 'high', 'critical')),
  alert_type text not null,
  title text not null,
  summary text,
  reason text,
  status text not null default 'new' check (
    status in ('new', 'in_review', 'attended', 'closed')
  ),
  assigned_to uuid references auth.users (id),
  rule_applied text,
  ml_inference_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists alerts_org_status_idx on public.alerts (organization_id, status);
create index if not exists alerts_lot_idx on public.alerts (lot_id);

create table if not exists public.alert_reviews (
  id uuid primary key default gen_random_uuid(),
  alert_id uuid not null references public.alerts (id) on delete cascade,
  reviewer_id uuid references auth.users (id),
  result text not null,
  observation text,
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Machine Learning (señales revisables, nunca sentencia)
-- ---------------------------------------------------------------------------
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

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'alerts_ml_inference_fk'
  ) then
    alter table public.alerts
      add constraint alerts_ml_inference_fk
      foreign key (ml_inference_id) references public.ml_inferences (id);
  end if;
end $$;

-- ---------------------------------------------------------------------------
-- Notificaciones
-- ---------------------------------------------------------------------------
create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  organization_id uuid references public.organizations (id),
  title text not null,
  body text,
  type text not null default 'operational',
  resource_type text,
  resource_id text,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists notifications_user_idx
  on public.notifications (user_id, created_at desc);

-- ---------------------------------------------------------------------------
-- Configuración de organización
-- ---------------------------------------------------------------------------
create table if not exists public.organization_settings (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null unique references public.organizations (id),
  general jsonb not null default '{}'::jsonb,
  security jsonb not null default '{}'::jsonb,
  notifications jsonb not null default '{}'::jsonb,
  integrations jsonb not null default '{}'::jsonb,
  updated_by uuid references auth.users (id),
  updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Auditoría: contexto y organización
-- ---------------------------------------------------------------------------
alter table public.audit_log
  add column if not exists context jsonb,
  add column if not exists organization_id uuid references public.organizations (id);

create index if not exists audit_log_entity_idx on public.audit_log (entity, entity_id);
create index if not exists audit_log_created_idx on public.audit_log (created_at desc);

-- ---------------------------------------------------------------------------
-- Custodia: responsable y estado para la vista web
-- ---------------------------------------------------------------------------
alter table public.custody_transfers
  add column if not exists created_by uuid references auth.users (id),
  add column if not exists status text not null default 'completed',
  add column if not exists responsible text;

-- ---------------------------------------------------------------------------
-- Semilla de tolerancia por defecto (3% relativo) — versionada
-- ---------------------------------------------------------------------------
insert into public.tolerance_rules (
  organization_id, rule_key, name, value, unit, version, is_active
)
select
  o.id,
  'mass_balance_percent',
  'Tolerancia de balance de masas',
  3,
  'percent',
  1,
  true
from public.organizations o
where not exists (
  select 1
  from public.tolerance_rules t
  where t.organization_id = o.id
    and t.rule_key = 'mass_balance_percent'
);

insert into public.ml_models (name, version, status, metrics)
select
  'expected-quantity-baseline',
  '1.0.0',
  'active',
  '{"mae": 2.4, "mape": 3.1, "description": "Estimador estadístico de cantidad esperada"}'::jsonb
where not exists (
  select 1 from public.ml_models where name = 'expected-quantity-baseline' and version = '1.0.0'
);

insert into public.organization_settings (organization_id, general)
select o.id, jsonb_build_object('timezone', 'America/Bogota', 'locale', 'es-CO')
from public.organizations o
where not exists (
  select 1 from public.organization_settings s where s.organization_id = o.id
);

-- ---------------------------------------------------------------------------
-- RLS
-- ---------------------------------------------------------------------------
alter table public.invitations enable row level security;
alter table public.tolerance_rules enable row level security;
alter table public.mass_balances enable row level security;
alter table public.alerts enable row level security;
alter table public.alert_reviews enable row level security;
alter table public.ml_models enable row level security;
alter table public.ml_inferences enable row level security;
alter table public.notifications enable row level security;
alter table public.organization_settings enable row level security;

drop policy if exists invitations_admin on public.invitations;
create policy invitations_admin on public.invitations
  for all using (
    organization_id = public.current_org_id()
    and public.current_role() = 'admin'
  )
  with check (
    organization_id = public.current_org_id()
    and public.current_role() = 'admin'
  );

drop policy if exists tolerance_select on public.tolerance_rules;
create policy tolerance_select on public.tolerance_rules
  for select using (organization_id = public.current_org_id());

drop policy if exists tolerance_admin on public.tolerance_rules;
create policy tolerance_admin on public.tolerance_rules
  for insert with check (
    organization_id = public.current_org_id()
    and public.current_role() = 'admin'
  );

drop policy if exists mass_balances_select on public.mass_balances;
create policy mass_balances_select on public.mass_balances
  for select using (organization_id = public.current_org_id());

drop policy if exists mass_balances_write on public.mass_balances;
create policy mass_balances_write on public.mass_balances
  for all using (
    organization_id = public.current_org_id()
    and public.current_role() in ('admin', 'auditor', 'receiver', 'plant_manager', 'supervisor')
  )
  with check (organization_id = public.current_org_id());

drop policy if exists alerts_select on public.alerts;
create policy alerts_select on public.alerts
  for select using (organization_id = public.current_org_id());

drop policy if exists alerts_write on public.alerts;
create policy alerts_write on public.alerts
  for all using (
    organization_id = public.current_org_id()
    and public.current_role() in ('admin', 'auditor', 'supervisor', 'control_center')
  )
  with check (organization_id = public.current_org_id());

drop policy if exists alert_reviews_select on public.alert_reviews;
create policy alert_reviews_select on public.alert_reviews
  for select using (
    exists (
      select 1 from public.alerts a
      where a.id = alert_id and a.organization_id = public.current_org_id()
    )
  );

drop policy if exists alert_reviews_insert on public.alert_reviews;
create policy alert_reviews_insert on public.alert_reviews
  for insert with check (
    exists (
      select 1 from public.alerts a
      where a.id = alert_id and a.organization_id = public.current_org_id()
    )
    and public.current_role() in ('admin', 'auditor', 'supervisor')
  );

drop policy if exists ml_models_select on public.ml_models;
create policy ml_models_select on public.ml_models
  for select using (auth.role() = 'authenticated');

drop policy if exists ml_inferences_select on public.ml_inferences;
create policy ml_inferences_select on public.ml_inferences
  for select using (organization_id = public.current_org_id());

drop policy if exists notifications_own on public.notifications;
create policy notifications_own on public.notifications
  for all using (user_id = auth.uid())
  with check (user_id = auth.uid());

drop policy if exists settings_select on public.organization_settings;
create policy settings_select on public.organization_settings
  for select using (organization_id = public.current_org_id());

drop policy if exists settings_admin on public.organization_settings;
create policy settings_admin on public.organization_settings
  for update using (
    organization_id = public.current_org_id()
    and public.current_role() = 'admin'
  );

grant select, insert, update, delete on public.invitations to authenticated;
grant select, insert, update on public.tolerance_rules to authenticated;
grant select, insert, update on public.mass_balances to authenticated;
grant select, insert, update on public.alerts to authenticated;
grant select, insert on public.alert_reviews to authenticated;
grant select on public.ml_models to authenticated;
grant select, insert on public.ml_inferences to authenticated;
grant select, insert, update on public.notifications to authenticated;
grant select, insert, update on public.organization_settings to authenticated;

-- El backend con service_role omite RLS. Grants para service_role implícitos.
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
