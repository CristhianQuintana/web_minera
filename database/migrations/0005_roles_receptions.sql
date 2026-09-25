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
