-- Promueve un usuario Auth existente a administrador web activo.
-- Reemplazar el correo antes de ejecutar.
-- Rol canónico: 'admin' (no 'administrator').
-- Campos que valida el login: status='active', invitation_status='active', organization_id.

insert into public.organizations (id, name)
values ('e857fa80-1678-4b27-b80f-c38f471a8931', 'Cooperativa piloto')
on conflict (id) do nothing;

insert into public.profiles (
  id, full_name, role, organization_id, status, email, invitation_status
)
select
  u.id,
  coalesce(u.raw_user_meta_data->>'full_name', split_part(u.email, '@', 1), 'Administrador'),
  'admin',
  'e857fa80-1678-4b27-b80f-c38f471a8931',
  'active',
  u.email,
  'active'
from auth.users u
where u.email = 'cristhian@gmail.com'
on conflict (id) do update set
  role = 'admin',
  status = 'active',
  invitation_status = 'active',
  organization_id = excluded.organization_id,
  email = excluded.email,
  full_name = excluded.full_name,
  updated_at = now();
