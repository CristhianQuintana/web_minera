-- Opcional: promover un usuario existente a administrador web.
-- Reemplazar el correo antes de ejecutar.

update public.profiles p
set role = 'admin',
    status = 'active',
    invitation_status = 'active',
    email = u.email,
    updated_at = now()
from auth.users u
where p.id = u.id
  and u.email = 'productor.prueba@cooperativa.org';
