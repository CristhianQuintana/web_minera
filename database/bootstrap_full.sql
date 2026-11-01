-- WEB_MINERA bootstrap completo para proyecto Supabase vacío
-- Generado automáticamente — ejecutar en SQL Editor

-- ========== database\migrations\0001_init.sql ==========
-- Esquema inicial para trazabilidad y cadena de custodia.
-- Ejecutar en el SQL Editor de Supabase antes de usar la aplicación móvil.
-- No habilita políticas abiertas. Deny by default + least privilege.

create extension if not exists pgcrypto;

create table if not exists public.organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text not null,
  role text not null check (
    role in (
      'producer',
      'carrier',
      'receiver',
      'transporter',
      'plant_manager',
      'control_center',
      'supervisor',
      'admin',
      'auditor'
    )
  ),
  organization_id uuid references public.organizations (id),
  status text not null default 'active' check (status in ('active', 'inactive')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.mining_operations (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  name text not null,
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists public.lots (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  organization_id uuid not null references public.organizations (id),
  mining_operation_id uuid references public.mining_operations (id),
  code text not null,
  mineral text not null,
  quantity numeric not null check (quantity > 0),
  unit text not null,
  status text not null default 'registered',
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  qr_payload text,
  observation text,
  created_by uuid not null references auth.users (id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (organization_id, code)
);

create table if not exists public.lot_events (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  event_type text not null,
  occurred_at timestamptz not null,
  user_id uuid references auth.users (id),
  notes text,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.custody_transfers (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  origin text not null,
  destination text not null,
  quantity numeric not null check (quantity > 0),
  occurred_at timestamptz not null,
  notes text,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.transports (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  vehicle text not null,
  plate text not null,
  driver text not null,
  status text not null,
  started_at timestamptz not null,
  ended_at timestamptz,
  notes text,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.transport_events (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  transport_id uuid not null references public.transports (id),
  description text not null,
  occurred_at timestamptz not null,
  is_incident boolean not null default false,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.evidences (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  event_id uuid references public.lot_events (id),
  file_name text not null,
  mime_type text not null,
  size_bytes integer not null check (size_bytes > 0),
  storage_path text,
  created_by uuid references auth.users (id),
  created_at timestamptz not null default now()
);

create table if not exists public.audit_log (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  action text not null,
  entity text not null,
  entity_id text,
  lot_id uuid,
  result text,
  created_at timestamptz not null default now()
);

create or replace function public.current_org_id()
returns uuid
language sql
stable
security definer
set search_path = public
as $$
  select organization_id from public.profiles where id = auth.uid()
$$;

create or replace function public.current_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select role from public.profiles where id = auth.uid()
$$;

revoke all on function public.current_org_id() from public;
revoke all on function public.current_role() from public;
grant execute on function public.current_org_id() to authenticated;
grant execute on function public.current_role() to authenticated;

alter table public.organizations enable row level security;
alter table public.profiles enable row level security;
alter table public.mining_operations enable row level security;
alter table public.lots enable row level security;
alter table public.lot_events enable row level security;
alter table public.custody_transfers enable row level security;
alter table public.transports enable row level security;
alter table public.transport_events enable row level security;
alter table public.evidences enable row level security;
alter table public.audit_log enable row level security;

create policy profiles_select on public.profiles
  for select using (id = auth.uid() or organization_id = public.current_org_id());

create policy organizations_select on public.organizations
  for select using (id = public.current_org_id());

create policy mining_operations_select on public.mining_operations
  for select using (organization_id = public.current_org_id());

create policy lots_select on public.lots
  for select using (organization_id = public.current_org_id());

create policy lots_insert on public.lots
  for insert with check (
    organization_id = public.current_org_id()
    and created_by = auth.uid()
    and public.current_role() in ('producer', 'plant_manager', 'admin')
  );

create policy lots_update on public.lots
  for update using (
    organization_id = public.current_org_id()
    and public.current_role() in ('producer', 'plant_manager', 'admin', 'transporter', 'carrier')
  );

create policy lot_events_select on public.lot_events
  for select using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
  );

create policy lot_events_insert on public.lot_events
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() <> 'auditor'
  );

create policy transfers_select on public.custody_transfers
  for select using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
  );

create policy transfers_insert on public.custody_transfers
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('producer', 'plant_manager', 'admin')
  );

create policy transports_select on public.transports
  for select using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
  );

create policy transports_insert on public.transports
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('transporter', 'carrier', 'admin')
  );

create policy transports_update on public.transports
  for update using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('transporter', 'carrier', 'admin')
  );

create policy transport_events_select on public.transport_events
  for select using (
    exists (
      select 1
      from public.transports t
      join public.lots l on l.id = t.lot_id
      where t.id = transport_id and l.organization_id = public.current_org_id()
    )
  );

create policy transport_events_insert on public.transport_events
  for insert with check (
    exists (
      select 1
      from public.transports t
      join public.lots l on l.id = t.lot_id
      where t.id = transport_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('transporter', 'carrier', 'admin')
  );

create policy evidences_select on public.evidences
  for select using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
  );

create policy evidences_insert on public.evidences
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() <> 'auditor'
  );

create policy audit_select on public.audit_log
  for select using (
    public.current_role() in ('admin', 'auditor', 'control_center')
  );

insert into storage.buckets (id, name, public)
values ('evidencias', 'evidencias', false)
on conflict (id) do nothing;

create policy evidencias_select on storage.objects
  for select using (
    bucket_id = 'evidencias'
    and auth.role() = 'authenticated'
  );

create policy evidencias_insert on storage.objects
  for insert with check (
    bucket_id = 'evidencias'
    and auth.role() = 'authenticated'
  );


-- ========== database\migrations\0004_fix_rls_and_profiles.sql ==========
-- Corrige recursión infinita en RLS y crea perfiles de los usuarios de Auth.
-- Ejecutar en SQL Editor después de 0001_init.sql.

create or replace function public.current_org_id()
returns uuid
language sql
stable
security definer
set search_path = public
as $$
  select organization_id from public.profiles where id = auth.uid()
$$;

create or replace function public.current_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select role from public.profiles where id = auth.uid()
$$;

revoke all on function public.current_org_id() from public;
revoke all on function public.current_role() from public;
grant execute on function public.current_org_id() to authenticated;
grant execute on function public.current_role() to authenticated;

insert into public.organizations (id, name)
values ('e857fa80-1678-4b27-b80f-c38f471a8931', 'Cooperativa piloto')
on conflict (id) do nothing;

insert into public.mining_operations (organization_id, name)
select 'e857fa80-1678-4b27-b80f-c38f471a8931', 'Operación El Alto'
where not exists (
  select 1
  from public.mining_operations
  where name = 'Operación El Alto'
    and organization_id = 'e857fa80-1678-4b27-b80f-c38f471a8931'
);

insert into public.profiles (id, full_name, role, organization_id, status)
select
  u.id,
  coalesce(u.raw_user_meta_data->>'full_name', split_part(u.email, '@', 1)),
  'producer',
  'e857fa80-1678-4b27-b80f-c38f471a8931',
  'active'
from auth.users u
on conflict (id) do update
  set full_name = excluded.full_name,
      role = excluded.role,
      organization_id = excluded.organization_id,
      status = excluded.status,
      updated_at = now();

select u.email, p.role, p.status, o.name as organization
from auth.users u
join public.profiles p on p.id = u.id
join public.organizations o on o.id = p.organization_id
order by u.email;


-- ========== database\migrations\0005_roles_receptions.sql ==========
-- Roles de campo, recepciones, pesajes y RLS para transportista/receptor.
-- Ejecutar después de 0001 y 0004.

alter table public.profiles drop constraint if exists profiles_role_check;
alter table public.profiles add constraint profiles_role_check check (
  role in (
    'producer',
    'carrier',
    'receiver',
    'transporter',
    'plant_manager',
    'control_center',
    'supervisor',
    'admin',
    'auditor'
  )
);

alter table public.transports
  add column if not exists code text,
  add column if not exists origin text,
  add column if not exists destination text,
  add column if not exists assigned_to uuid references auth.users (id),
  add column if not exists declared_quantity numeric;

alter table public.transport_events
  add column if not exists event_type text,
  add column if not exists user_id uuid references auth.users (id);

create table if not exists public.receptions (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  declared_quantity numeric not null check (declared_quantity > 0),
  received_quantity numeric not null check (received_quantity > 0),
  unit text not null,
  occurred_at timestamptz not null,
  responsible text not null,
  status text not null default 'confirmed',
  notes text,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_by uuid references auth.users (id),
  created_at timestamptz not null default now()
);

create table if not exists public.weighings (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  reception_id uuid references public.receptions (id),
  weight numeric not null check (weight > 0),
  unit text not null,
  occurred_at timestamptz not null,
  instrument text not null,
  responsible text not null,
  notes text,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_by uuid references auth.users (id),
  created_at timestamptz not null default now()
);

alter table public.receptions enable row level security;
alter table public.weighings enable row level security;

drop policy if exists transfers_insert on public.custody_transfers;
create policy transfers_insert on public.custody_transfers
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('producer', 'plant_manager', 'admin')
  );

drop policy if exists transports_select on public.transports;
create policy transports_select on public.transports
  for select using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and (
      public.current_role() in (
        'admin',
        'supervisor',
        'receiver',
        'producer',
        'plant_manager'
      )
      or assigned_to = auth.uid()
      or assigned_to is null
    )
  );

drop policy if exists transports_insert on public.transports;
create policy transports_insert on public.transports
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('transporter', 'carrier', 'admin')
  );

drop policy if exists transports_update on public.transports;
create policy transports_update on public.transports
  for update using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and (
      public.current_role() in ('transporter', 'carrier', 'admin')
      and (assigned_to = auth.uid() or assigned_to is null)
    )
  );

drop policy if exists transport_events_insert on public.transport_events;
create policy transport_events_insert on public.transport_events
  for insert with check (
    exists (
      select 1
      from public.transports t
      join public.lots l on l.id = t.lot_id
      where t.id = transport_id
        and l.organization_id = public.current_org_id()
        and (
          t.assigned_to = auth.uid()
          or t.assigned_to is null
          or public.current_role() = 'admin'
        )
    )
    and public.current_role() in ('transporter', 'carrier', 'admin')
  );

drop policy if exists receptions_select on public.receptions;
create policy receptions_select on public.receptions
  for select using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
  );

drop policy if exists receptions_insert on public.receptions;
create policy receptions_insert on public.receptions
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('receiver', 'plant_manager', 'admin')
    and created_by = auth.uid()
  );

drop policy if exists weighings_select on public.weighings;
create policy weighings_select on public.weighings
  for select using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
  );

drop policy if exists weighings_insert on public.weighings;
create policy weighings_insert on public.weighings
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('receiver', 'plant_manager', 'admin')
    and created_by = auth.uid()
  );

grant select, insert on public.receptions to authenticated;
grant select, insert on public.weighings to authenticated;


-- ========== database\migrations\0006_web_platform.sql ==========
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



-- Organización piloto (real). No se crean organizaciones ficticias tipo demo-org.
-- Asigna perfiles reales con database/seeds/promote_admin.sql tras crear el usuario en Auth.
-- insert into public.organizations (id, name)
-- values ('e857fa80-1678-4b27-b80f-c38f471a8931', 'Cooperativa piloto')
-- on conflict (id) do nothing;
