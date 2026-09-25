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
