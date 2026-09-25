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
